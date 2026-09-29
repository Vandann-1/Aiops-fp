import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponseNotAllowed
from accounts.decorators import employee_required, it_admin_required
from accounts.utils import is_it_admin, is_employee
from .models import Incident, IncidentActivity, IncidentFeedback
from .forms import IncidentCreateForm, IncidentAdminUpdateForm, IncidentFeedbackForm


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
    from runbooks.models import Runbook
    from automation.models import AutomationApproval, AutomationExecution, VerificationResult, AuditLog

    all_incidents = Incident.objects.all()
    
    # Unresolved critical incidents
    unresolved_critical = all_incidents.filter(
        priority=Incident.Priority.CRITICAL
    ).exclude(
        status__in=[Incident.Status.RESOLVED, Incident.Status.REJECTED]
    )[:5]

    total_incidents = all_incidents.count()
    open_incidents = all_incidents.filter(status=Incident.Status.OPEN).count()
    critical_incidents = all_incidents.filter(priority=Incident.Priority.CRITICAL).count()
    resolved_incidents = all_incidents.filter(status=Incident.Status.RESOLVED).count()

    active_runbooks = Runbook.objects.filter(is_active=True).count()
    inactive_runbooks = Runbook.objects.filter(is_active=False).count()

    # Phase 5: Pending approvals
    pending_approvals = AutomationApproval.objects.filter(status=AutomationApproval.ApprovalStatus.PENDING).count()

    # Phase 6 & 8: Automation Execution metrics
    successful_executions = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.SUCCESS).count()
    failed_executions = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.FAILED).count()
    blocked_executions = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.BLOCKED).count()
    total_executions = AutomationExecution.objects.count()

    # Success rate
    completed_executions = successful_executions + failed_executions
    if completed_executions > 0:
        automation_success_rate = round((successful_executions / completed_executions) * 100, 1)
    else:
        automation_success_rate = 0.0

    # Phase 7 & 8: Verification metrics
    verifications_passed = VerificationResult.objects.filter(status=VerificationResult.Status.PASSED).count()
    verifications_failed = VerificationResult.objects.filter(status=VerificationResult.Status.FAILED).count()
    total_verifications = VerificationResult.objects.count()

    # Phase 8: Audit logs & Recent Activity
    total_audit_events = AuditLog.objects.count()
    recent_audit_events = AuditLog.objects.select_related('incident', 'actor').order_by('-created_at')[:8]

    context = {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'critical_incidents': critical_incidents,
        'resolved_incidents': resolved_incidents,
        'pending_approvals': pending_approvals,
        'active_runbooks': active_runbooks,
        'inactive_runbooks': inactive_runbooks,
        'recent_incidents': all_incidents[:5],
        'unresolved_critical': unresolved_critical,

        # Automation Overview
        'successful_executions': successful_executions,
        'failed_executions': failed_executions,
        'blocked_executions': blocked_executions,
        'total_executions': total_executions,
        'automation_success_rate': automation_success_rate,

        # Verification Monitoring
        'verifications_passed': verifications_passed,
        'verifications_failed': verifications_failed,
        'total_verifications': total_verifications,

        # Audit & Monitoring
        'total_audit_events': total_audit_events,
        'recent_audit_events': recent_audit_events,
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
                    # Persist the best recommendation with citations
                    RunbookRecommendation.objects.update_or_create(
                        incident=incident,
                        defaults={
                            'runbook': best_runbook,
                            'match_score': best_score,
                            'retrieval_method': 'tfidf',
                            'citation_metadata': result.get('citation', {})
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

    feedback_form = None
    if incident.status == Incident.Status.RESOLVED and not hasattr(incident, 'feedback'):
        feedback_form = IncidentFeedbackForm()

    return render(request, 'employee/incident_detail.html', {
        'incident': incident,
        'activities': activities,
        'status_progress': status_progress,
        'feedback_form': feedback_form
    })


@login_required
@employee_required
def employee_submit_feedback(request, pk):
    """
    Phase 9 & 10: Allows employee to submit rating and comments for their resolved incident.
    Enforces object-level ownership and prevents duplicate feedback.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    incident = get_object_or_404(Incident, pk=pk, created_by=request.user)

    if incident.status != Incident.Status.RESOLVED:
        messages.error(request, "Feedback can only be submitted once the incident is resolved.")
        return redirect('employee_incident_detail', pk=incident.pk)

    if hasattr(incident, 'feedback'):
        messages.warning(request, "You have already submitted feedback for this incident.")
        return redirect('employee_incident_detail', pk=incident.pk)

    form = IncidentFeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.incident = incident
        feedback.user = request.user
        feedback.save()

        IncidentActivity.objects.create(
            incident=incident,
            actor=request.user,
            action='FEEDBACK_SUBMITTED',
            description=f"Incident feedback submitted with rating {feedback.rating}/5."
        )

        logger.info(f"[{incident.incident_number}] Feedback submitted: rating={feedback.rating}/5")

        messages.success(request, "Thank you! Your feedback has been recorded.")
    else:
        messages.error(request, "Failed to submit feedback. Please check the rating.")

    return redirect('employee_incident_detail', pk=incident.pk)


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
    audit_logs = incident.audit_logs.all().select_related('actor').order_by('created_at')
    form = IncidentAdminUpdateForm(instance=incident)

    # Phase 6 & 7: Safety checklist and Dry-Run preview
    from automation.safety import get_diagnostic_checklist
    from automation.actions import get_dry_run_preview, get_action_metadata

    approval = incident.approvals.first() if incident.approvals.exists() else None
    checklist = get_diagnostic_checklist(incident, approval=approval)
    action_name = ""
    if approval and approval.runbook:
        action_name = approval.runbook.automation_action
    elif hasattr(incident, 'runbook_recommendation') and incident.runbook_recommendation and incident.runbook_recommendation.runbook:
        action_name = incident.runbook_recommendation.runbook.automation_action

    dry_run = get_dry_run_preview(action_name) if action_name else None
    action_meta = get_action_metadata(action_name) if action_name else None
    
    return render(request, 'admin_portal/incident_detail.html', {
        'incident': incident,
        'activities': activities,
        'audit_logs': audit_logs,
        'form': form,
        'checklist': checklist,
        'dry_run': dry_run,
        'action_meta': action_meta,
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

        result = retrieve_best_runbook(incident, actor=request.user)
        best_runbook = result['runbook']
        best_score = result['score']

        if best_runbook:
            # Update or create recommendation
            RunbookRecommendation.objects.update_or_create(
                incident=incident,
                defaults={
                    'runbook': best_runbook,
                    'match_score': best_score,
                    'retrieval_method': 'tfidf',
                    'citation_metadata': result.get('citation', {})
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


@login_required
@it_admin_required
def project_overview(request):
    """
    Part 25: AIOps Capstone Compliance & Overview Console.
    Provides verifiable operational status, architecture explanation, AI methodology,
    safety controls, and live metrics from actual database entities.
    """
    from django.db.models import Avg, Count
    from runbooks.models import Runbook, RunbookRecommendation
    from automation.models import AutomationApproval, AutomationExecution, VerificationResult, AuditLog
    from incidents.models import IncidentFeedback

    total_incidents = Incident.objects.count()
    open_incidents = Incident.objects.filter(status=Incident.Status.OPEN).count()
    resolved_incidents = Incident.objects.filter(status=Incident.Status.RESOLVED).count()
    analyzed_incidents = Incident.objects.exclude(intent='Unknown').count()

    # Intent breakdown
    intent_stats = Incident.objects.values('intent').annotate(count=Count('id')).order_by('-count')

    # Knowledge Base
    total_runbooks = Runbook.objects.count()
    active_runbooks = Runbook.objects.filter(is_active=True).count()
    recommendations_count = RunbookRecommendation.objects.count()

    # Approvals & Executions
    total_approvals = AutomationApproval.objects.count()
    approved_count = AutomationApproval.objects.filter(status=AutomationApproval.ApprovalStatus.APPROVED).count()
    rejected_count = AutomationApproval.objects.filter(status=AutomationApproval.ApprovalStatus.REJECTED).count()

    successful_executions = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.SUCCESS).count()
    failed_executions = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.FAILED).count()
    blocked_executions = AutomationExecution.objects.filter(status=AutomationExecution.ExecutionStatus.BLOCKED).count()
    total_executions = AutomationExecution.objects.count()

    completed_execs = successful_executions + failed_executions
    exec_success_rate = round((successful_executions / completed_execs * 100), 1) if completed_execs > 0 else 0.0

    # Verifications
    verifications_passed = VerificationResult.objects.filter(status=VerificationResult.Status.PASSED).count()
    verifications_failed = VerificationResult.objects.filter(status=VerificationResult.Status.FAILED).count()

    # Feedback
    feedback_count = IncidentFeedback.objects.count()
    avg_rating_res = IncidentFeedback.objects.aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating_res, 2) if avg_rating_res is not None else None

    # Resolution Time
    resolved_with_time = Incident.objects.filter(status=Incident.Status.RESOLVED, resolved_at__isnull=False)
    total_duration_secs = 0
    valid_time_count = 0
    for inc in resolved_with_time:
        if inc.resolved_at and inc.created_at:
            total_duration_secs += (inc.resolved_at - inc.created_at).total_seconds()
            valid_time_count += 1
    mean_resolution_minutes = round(total_duration_secs / (valid_time_count * 60), 1) if valid_time_count > 0 else None

    # Unsafe action blocks
    blocked_audit_count = AuditLog.objects.filter(event_type=AuditLog.EventType.AUTOMATION_BLOCKED).count()

    import json
    from django.conf import settings
    eval_results = None
    eval_file = settings.BASE_DIR / 'data' / 'evaluation_results.json'
    if eval_file.exists():
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                eval_results = json.load(f)
        except Exception:
            eval_results = None

    context = {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'resolved_incidents': resolved_incidents,
        'analyzed_incidents': analyzed_incidents,
        'intent_stats': intent_stats,
        'total_runbooks': total_runbooks,
        'active_runbooks': active_runbooks,
        'recommendations_count': recommendations_count,
        'total_approvals': total_approvals,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'successful_executions': successful_executions,
        'failed_executions': failed_executions,
        'blocked_executions': blocked_executions,
        'total_executions': total_executions,
        'exec_success_rate': exec_success_rate,
        'verifications_passed': verifications_passed,
        'verifications_failed': verifications_failed,
        'feedback_count': feedback_count,
        'avg_rating': avg_rating,
        'mean_resolution_minutes': mean_resolution_minutes,
        'blocked_audit_count': blocked_audit_count,
        'eval_results': eval_results,
    }
    return render(request, 'admin_portal/project_overview.html', context)

