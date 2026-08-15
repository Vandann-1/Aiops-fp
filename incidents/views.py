import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponseNotAllowed
from accounts.decorators import employee_required, it_admin_required
from accounts.utils import is_it_admin, is_employee
from .models import Incident, IncidentActivity
from .forms import IncidentCreateForm, IncidentAdminUpdateForm

logger = logging.getLogger(__name__)

@login_required
@employee_required
def employee_dashboard(request):
    user_incidents = Incident.objects.filter(created_by=request.user)
    
    context = {
        'total_incidents': user_incidents.count(),
        'open_incidents': user_incidents.filter(status=Incident.Status.OPEN).count(),
        'inprogress_incidents': user_incidents.filter(status=Incident.Status.IN_PROGRESS).count(),
        'resolved_incidents': user_incidents.filter(status=Incident.Status.RESOLVED).count(),
        'recent_incidents': user_incidents[:5]
    }
    return render(request, 'employee/dashboard.html', context)

@login_required
@it_admin_required
def admin_dashboard(request):
    all_incidents = Incident.objects.all()
    
    # Unresolved critical incidents
    unresolved_critical = all_incidents.filter(
        priority=Incident.Priority.CRITICAL
    ).exclude(
        status__in=[Incident.Status.RESOLVED, Incident.Status.REJECTED]
    )[:5]

    from runbooks.models import Runbook
    active_runbooks = Runbook.objects.filter(is_active=True).count()
    inactive_runbooks = Runbook.objects.filter(is_active=False).count()

    context = {
        'total_incidents': all_incidents.count(),
        'open_incidents': all_incidents.filter(status=Incident.Status.OPEN).count(),
        'critical_incidents': all_incidents.filter(priority=Incident.Priority.CRITICAL).count(),
        'resolved_incidents': all_incidents.filter(status=Incident.Status.RESOLVED).count(),
        'pending_approvals': 0,  # Reserved for Phase 5
        'active_runbooks': active_runbooks,
        'inactive_runbooks': inactive_runbooks,
        'recent_incidents': all_incidents[:5],
        'unresolved_critical': unresolved_critical
    }
    return render(request, 'admin_portal/dashboard.html', context)

@login_required
@employee_required
def employee_incident_create(request):
    if request.method == 'POST':
        form = IncidentCreateForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.status = Incident.Status.ANALYZING
            incident.save()
            
            # 1. Create incident reported timeline activity
            IncidentActivity.objects.create(
                incident=incident,
                actor=request.user,
                action='INCIDENT_CREATED',
                description=f"Incident reported by {request.user.get_full_name() or request.user.username}."
            )
            
            # 2. Run AI Runbook Retrieval safely (non-blocking)
            from runbooks.retrieval import retrieve_best_runbook
            from runbooks.models import RunbookRecommendation

            try:
                # Log analysis started
                IncidentActivity.objects.create(
                    incident=incident,
                    actor=None,
                    action='AI_ANALYSIS_STARTED',
                    description="AI retrieval engine started analyzing the incident description."
                )

                result = retrieve_best_runbook(incident)
                best_runbook = result['runbook']
                best_score = result['score']

                if best_runbook:
                    # Persist the best recommendation
                    RunbookRecommendation.objects.update_or_create(
                        incident=incident,
                        defaults={
                            'runbook': best_runbook,
                            'match_score': best_score,
                            'retrieval_method': 'tfidf'
                        }
                    )
                    incident.status = Incident.Status.RECOMMENDATION_READY
                    incident.save()

                    # Log successful match activity
                    IncidentActivity.objects.create(
                        incident=incident,
                        actor=None,
                        action='AI_ANALYSIS_COMPLETED',
                        description=f"AI retrieval recommended {best_runbook.runbook_number} — {best_runbook.title} with a {best_score * 100:.2f}% match score."
                    )
                else:
                    # Clean up old recommendations if they somehow existed
                    RunbookRecommendation.objects.filter(incident=incident).delete()
                    incident.status = Incident.Status.OPEN
                    incident.save()

                    # Log no suitable match found activity
                    IncidentActivity.objects.create(
                        incident=incident,
                        actor=None,
                        action='AI_ANALYSIS_COMPLETED',
                        description="AI retrieval completed. No suitable runbook was found for this incident."
                    )
            except Exception as e:
                # Safe fallback: reset status to OPEN, do not crash view execution
                incident.status = Incident.Status.OPEN
                incident.save()
                logger.error(f"Retrieval engine failed on ticket create: {str(e)}", exc_info=True)

            messages.success(request, f"Incident {incident.incident_number} reported successfully.")
            return redirect('employee_incident_detail', pk=incident.pk)
    else:
        form = IncidentCreateForm()
        
    return render(request, 'employee/incident_create.html', {'form': form})

@login_required
@employee_required
def employee_incident_list(request):
    user_incidents = Incident.objects.filter(created_by=request.user)
    
    # Calculate stats
    stats = {
        'total': user_incidents.count(),
        'open': user_incidents.filter(status=Incident.Status.OPEN).count(),
        'inprogress': user_incidents.filter(status=Incident.Status.IN_PROGRESS).count(),
        'resolved': user_incidents.filter(status=Incident.Status.RESOLVED).count(),
    }
    
    paginator = Paginator(user_incidents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'employee/incident_list.html', {
        'page_obj': page_obj,
        'stats': stats
    })

@login_required
@employee_required
def employee_incident_detail(request, pk):
    # Enforces object-level owner check
    incident = get_object_or_404(Incident, pk=pk, created_by=request.user)
    activities = incident.activities.all().order_by('-created_at')
    
    # Map status to progress tracker
    # Progress step values: 1: Reported, 2: Analyzing, 3: Recommendation, 4: Approval, 5: Resolution
    status_progress = 1
    if incident.status in [Incident.Status.ANALYZING]:
        status_progress = 2
    elif incident.status in [Incident.Status.RECOMMENDATION_READY]:
        status_progress = 3
    elif incident.status in [Incident.Status.PENDING_APPROVAL, Incident.Status.APPROVED]:
        status_progress = 4
    elif incident.status in [Incident.Status.IN_PROGRESS, Incident.Status.RESOLVED, Incident.Status.FAILED, Incident.Status.REJECTED]:
        status_progress = 5

    return render(request, 'employee/incident_detail.html', {
        'incident': incident,
        'activities': activities,
        'status_progress': status_progress
    })

@login_required
@it_admin_required
def admin_incident_list(request):
    incidents_list = Incident.objects.all()
    
    # Handle Q Search (supports 'search' and 'q' parameters)
    q = request.GET.get('search', request.GET.get('q', '')).strip()
    if q:
        incidents_list = incidents_list.filter(
            Q(incident_number__icontains=q) |
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(created_by__username__icontains=q)
        )
        
    # Handle GET Filters
    status_filter = request.GET.get('status')
    if status_filter:
        incidents_list = incidents_list.filter(status=status_filter)
        
    priority_filter = request.GET.get('priority')
    if priority_filter:
        incidents_list = incidents_list.filter(priority=priority_filter)
        
    category_filter = request.GET.get('category')
    if category_filter:
        incidents_list = incidents_list.filter(category=category_filter)
        
    # Global Admin metrics
    global_stats = {
        'total': Incident.objects.count(),
        'open': Incident.objects.filter(status=Incident.Status.OPEN).count(),
        'critical': Incident.objects.filter(priority=Incident.Priority.CRITICAL).count(),
        'inprogress': Incident.objects.filter(status=Incident.Status.IN_PROGRESS).count(),
        'resolved': Incident.objects.filter(status=Incident.Status.RESOLVED).count(),
    }
    
    paginator = Paginator(incidents_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context data for dropdown filters
    categories = Incident.Category.choices
    priorities = Incident.Priority.choices
    statuses = Incident.Status.choices

    return render(request, 'admin_portal/incident_list.html', {
        'page_obj': page_obj,
        'global_stats': global_stats,
        'categories': categories,
        'priorities': priorities,
        'statuses': statuses,
        'q': q,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter
    })

@login_required
@it_admin_required
def admin_critical_incidents(request):
    # Retrieve critical incidents, sorting unresolved critical incidents first
    incidents_list = Incident.objects.filter(
        priority=Incident.Priority.CRITICAL
    ).annotate(
        is_resolved=Case(
            When(status=Incident.Status.RESOLVED, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_resolved', '-created_at')
    
    global_stats = {
        'total': Incident.objects.count(),
        'open': Incident.objects.filter(status=Incident.Status.OPEN).count(),
        'critical': Incident.objects.filter(priority=Incident.Priority.CRITICAL).count(),
        'inprogress': Incident.objects.filter(status=Incident.Status.IN_PROGRESS).count(),
        'resolved': Incident.objects.filter(status=Incident.Status.RESOLVED).count(),
    }

    paginator = Paginator(incidents_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_portal/incident_list.html', {
        'page_obj': page_obj,
        'global_stats': global_stats,
        'is_critical_view': True
    })

@login_required
@it_admin_required
def admin_incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    activities = incident.activities.all().order_by('-created_at')
    form = IncidentAdminUpdateForm(instance=incident)
    
    return render(request, 'admin_portal/incident_detail.html', {
        'incident': incident,
        'activities': activities,
        'form': form
    })

@login_required
@it_admin_required
def admin_incident_update(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
        
    incident = get_object_or_404(Incident, pk=pk)
    
    # Store current state for activity logging comparison
    old_priority = incident.priority
    old_status = incident.status
    
    form = IncidentAdminUpdateForm(request.POST, instance=incident)
    if form.is_valid():
        updated_incident = form.save(commit=False)
        
        # Check priority change
        if old_priority != updated_incident.priority:
            IncidentActivity.objects.create(
                incident=updated_incident,
                actor=request.user,
                action='PRIORITY_CHANGED',
                description=f"Priority changed from {dict(Incident.Priority.choices).get(old_priority)} to {dict(Incident.Priority.choices).get(updated_incident.priority)}."
            )
            
        # Check status change
        if old_status != updated_incident.status:
            IncidentActivity.objects.create(
                incident=updated_incident,
                actor=request.user,
                action='STATUS_CHANGED',
                description=f"Status changed from {dict(Incident.Status.choices).get(old_status)} to {dict(Incident.Status.choices).get(updated_incident.status)}."
            )
            
        updated_incident.save()
        messages.success(request, f"Incident {updated_incident.incident_number} updated successfully.")
        
    return redirect('admin_incident_detail', pk=incident.pk)


@login_required
@it_admin_required
def admin_incident_analyze(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
        
    incident = get_object_or_404(Incident, pk=pk)
    
    # Run AI Runbook Retrieval
    from runbooks.retrieval import retrieve_best_runbook
    from runbooks.models import RunbookRecommendation

    try:
        # 1. Create analysis log activity
        IncidentActivity.objects.create(
            incident=incident,
            actor=request.user,
            action='AI_ANALYSIS_STARTED',
            description="AI retrieval engine manually re-run by admin."
        )

        result = retrieve_best_runbook(incident)
        best_runbook = result['runbook']
        best_score = result['score']

        if best_runbook:
            # Update or create recommendation
            RunbookRecommendation.objects.update_or_create(
                incident=incident,
                defaults={
                    'runbook': best_runbook,
                    'match_score': best_score,
                    'retrieval_method': 'tfidf'
                }
            )
            incident.status = Incident.Status.RECOMMENDATION_READY
            incident.save()

            # Log completion activity
            IncidentActivity.objects.create(
                incident=incident,
                actor=request.user,
                action='AI_ANALYSIS_COMPLETED',
                description=f"AI retrieval recommended {best_runbook.runbook_number} — {best_runbook.title} with a {best_score * 100:.2f}% match score."
            )
            messages.success(request, f"Re-analysis completed. Recommended runbook: {best_runbook.runbook_number}.")
        else:
            # Delete old recommendation if no match found
            RunbookRecommendation.objects.filter(incident=incident).delete()
            incident.status = Incident.Status.OPEN
            incident.save()

            # Log no match found activity
            IncidentActivity.objects.create(
                incident=incident,
                actor=request.user,
                action='AI_ANALYSIS_COMPLETED',
                description="AI retrieval completed. No suitable runbook was found for this incident."
            )
            messages.warning(request, "Re-analysis completed. No suitable runbook found.")

    except Exception as e:
        messages.error(request, f"AI analysis failed: {str(e)}")
        logger.error(f"Manual re-analysis failed: {str(e)}", exc_info=True)

    return redirect('admin_incident_detail', pk=incident.pk)
