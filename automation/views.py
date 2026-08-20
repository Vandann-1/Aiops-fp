import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed

from accounts.decorators import it_admin_required
from incidents.models import Incident, IncidentActivity
from runbooks.models import Runbook, RunbookRecommendation
from .models import AutomationApproval

logger = logging.getLogger(__name__)

@login_required
@it_admin_required
def admin_incident_request_approval(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    incident = get_object_or_404(Incident, pk=pk)
    recommendation = getattr(incident, 'runbook_recommendation', None)

    # Verify recommendation exists
    if not recommendation or not recommendation.runbook:
        messages.warning(request, "No AI runbook recommendation is available for approval.")
        return redirect('admin_incident_detail', pk=incident.pk)

    runbook = recommendation.runbook

    # Verify runbook is active
    if not runbook.is_active:
        messages.warning(request, "The recommended runbook is no longer active. Please reanalyze the incident.")
        return redirect('admin_incident_detail', pk=incident.pk)

    # Check for existing PENDING approval
    if AutomationApproval.objects.filter(incident=incident, status=AutomationApproval.ApprovalStatus.PENDING).exists():
        messages.warning(request, "An approval request is already pending.")
        return redirect('admin_incident_detail', pk=incident.pk)

    # Create AutomationApproval
    approval = AutomationApproval.objects.create(
        incident=incident,
        runbook=runbook,
        requested_by=request.user,
        status=AutomationApproval.ApprovalStatus.PENDING
    )

    # Update incident status
    incident.status = Incident.Status.PENDING_APPROVAL
    incident.save()

    # Log timeline activity
    IncidentActivity.objects.create(
        incident=incident,
        actor=request.user,
        action='APPROVAL_REQUESTED',
        description=f"Approval requested by admin for {runbook.runbook_number} — {runbook.title}."
    )

    messages.success(request, f"Approval request submitted for runbook {runbook.runbook_number}.")
    return redirect('approval_detail', pk=approval.pk)


@login_required
@it_admin_required
def approval_list(request):
    status_filter = request.GET.get('status', 'PENDING').strip().upper()
    
    approvals_list = AutomationApproval.objects.all().select_related('incident', 'runbook', 'requested_by')
    
    if status_filter in ['PENDING', 'APPROVED', 'REJECTED']:
        approvals = approvals_list.filter(status=status_filter)
    elif status_filter == 'ALL':
        approvals = approvals_list
    else:
        status_filter = 'PENDING'
        approvals = approvals_list.filter(status='PENDING')

    return render(request, 'admin_portal/approval_list.html', {
        'approvals': approvals,
        'status_filter': status_filter
    })


@login_required
@it_admin_required
def approval_detail(request, pk):
    approval = get_object_or_404(AutomationApproval, pk=pk)
    # Check if a newer recommendation exists that doesn't match this approval
    recommendation = getattr(approval.incident, 'runbook_recommendation', None)
    is_recommendation_mismatched = (
        recommendation is not None and 
        recommendation.runbook != approval.runbook
    )
    
    return render(request, 'admin_portal/approval_detail.html', {
        'approval': approval,
        'is_recommendation_mismatched': is_recommendation_mismatched
    })


@login_required
@it_admin_required
def approve_action(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    approval = get_object_or_404(AutomationApproval, pk=pk)

    if approval.status != AutomationApproval.ApprovalStatus.PENDING:
        messages.error(request, "This approval request is not pending.")
        return redirect('approval_detail', pk=approval.pk)

    # Verify runbook is active
    if not approval.runbook.is_active:
        messages.error(request, "The recommended runbook is no longer active.")
        return redirect('approval_detail', pk=approval.pk)

    # Verify recommendation matches
    recommendation = getattr(approval.incident, 'runbook_recommendation', None)
    if not recommendation or recommendation.runbook != approval.runbook:
        messages.error(request, "The current recommendation does not match this approval request.")
        return redirect('approval_detail', pk=approval.pk)

    # Perform approval
    approval.status = AutomationApproval.ApprovalStatus.APPROVED
    approval.reviewed_by = request.user
    approval.reviewed_at = timezone.now()
    approval.reason = request.POST.get('reason', '').strip()
    approval.save()

    # Update incident status
    incident = approval.incident
    incident.status = Incident.Status.APPROVED
    incident.save()

    # Log activity
    IncidentActivity.objects.create(
        incident=incident,
        actor=request.user,
        action='APPROVAL_APPROVED',
        description=f"Automation action approved by admin for {approval.runbook.runbook_number} — {approval.runbook.title}."
    )

    messages.success(request, "Action approved. Automation execution will be handled by the next phase.")
    return redirect('approval_detail', pk=approval.pk)


@login_required
@it_admin_required
def reject_action(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    approval = get_object_or_404(AutomationApproval, pk=pk)

    if approval.status != AutomationApproval.ApprovalStatus.PENDING:
        messages.error(request, "This approval request is not pending.")
        return redirect('approval_detail', pk=approval.pk)

    reason = request.POST.get('reason', '').strip()
    if not reason:
        messages.error(request, "Rejection reason is required.")
        return redirect('approval_detail', pk=approval.pk)

    # Perform rejection
    approval.status = AutomationApproval.ApprovalStatus.REJECTED
    approval.reviewed_by = request.user
    approval.reviewed_at = timezone.now()
    approval.reason = reason
    approval.save()

    # Update incident status
    incident = approval.incident
    incident.status = Incident.Status.REJECTED
    incident.save()

    # Log activity
    IncidentActivity.objects.create(
        incident=incident,
        actor=request.user,
        action='APPROVAL_REJECTED',
        description=f"Automation action rejected by admin. Reason: {reason}"
    )

    messages.warning(request, "Automation was not approved. Manual investigation may be required.")
    return redirect('approval_detail', pk=approval.pk)
