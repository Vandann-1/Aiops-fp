import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed

from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.decorators import it_admin_required
from incidents.models import Incident, IncidentActivity
from .models import AutomationApproval, AutomationExecution, VerificationResult, AuditLog
from automation.executor import execute_approved_action

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

    # Phase 8: Record audit log
    from automation.audit import create_audit_log
    from automation.models import AuditLog
    create_audit_log(
        incident=incident,
        event_type=AuditLog.EventType.APPROVAL_REQUESTED,
        message=f"Automation approval requested for runbook '{runbook.title}'.",
        actor=request.user,
        metadata={"approval_id": approval.id, "runbook_id": runbook.id, "runbook_title": runbook.title}
    )

    logger.info(f"[{incident.incident_number}] Approval requested for runbook {runbook.runbook_number}")

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

    from automation.safety import get_diagnostic_checklist
    from automation.actions import get_dry_run_preview, get_action_metadata

    checklist = get_diagnostic_checklist(approval.incident, approval=approval)
    action_name = approval.runbook.automation_action if approval.runbook else ""
    dry_run = get_dry_run_preview(action_name) if action_name else None
    action_meta = get_action_metadata(action_name) if action_name else None
    
    return render(request, 'admin_portal/approval_detail.html', {
        'approval': approval,
        'is_recommendation_mismatched': is_recommendation_mismatched,
        'checklist': checklist,
        'dry_run': dry_run,
        'action_meta': action_meta,
    })


@login_required
@it_admin_required
def admin_approval_dry_run(request, pk):
    """
    Part 7: Explicit Dry-Run Preview Endpoint.
    Displays what would happen during simulated execution without modifying
    incident status, execution records, database state, or operating system state.
    """
    approval = get_object_or_404(AutomationApproval, pk=pk)
    action_name = approval.runbook.automation_action if approval.runbook else ""

    from automation.actions import get_dry_run_preview, get_action_metadata
    from automation.safety import get_diagnostic_checklist

    preview = get_dry_run_preview(action_name)
    checklist = get_diagnostic_checklist(approval.incident, approval=approval)

    return render(request, 'admin_portal/dry_run_detail.html', {
        'approval': approval,
        'preview': preview,
        'checklist': checklist,
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

    # Phase 8: Record audit log
    from automation.audit import create_audit_log
    from automation.models import AuditLog
    create_audit_log(
        incident=incident,
        event_type=AuditLog.EventType.APPROVAL_APPROVED,
        message="Automation approval approved.",
        actor=request.user,
        metadata={"approval_id": approval.id, "runbook_id": approval.runbook.id, "notes": approval.reason}
    )

    logger.info(f"[{incident.incident_number}] Approval granted for runbook {approval.runbook.runbook_number} by {request.user.username}")

    messages.success(request, "Action approved. Automation execution will be handled by the next phase.")
    
    referer = request.META.get('HTTP_REFERER', '')
    if 'approvals' in referer:
        return redirect('approval_detail', pk=approval.pk)
    return redirect('admin_incident_detail', pk=approval.incident.pk)


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

    # Phase 8: Record audit log
    from automation.audit import create_audit_log
    from automation.models import AuditLog
    rej_msg = "Automation approval rejected."
    if reason:
        rej_msg += f" Reason: {reason}"
    create_audit_log(
        incident=incident,
        event_type=AuditLog.EventType.APPROVAL_REJECTED,
        message=rej_msg,
        actor=request.user,
        metadata={"approval_id": approval.id, "runbook_id": approval.runbook.id, "reason": reason}
    )

    logger.info(f"[{incident.incident_number}] Approval rejected for runbook {approval.runbook.runbook_number} by {request.user.username}: {reason}")

    messages.warning(request, "Automation was not approved. Manual investigation may be required.")
    
    referer = request.META.get('HTTP_REFERER', '')
    if 'approvals' in referer:
        return redirect('approval_detail', pk=approval.pk)
    return redirect('admin_incident_detail', pk=approval.incident.pk)


@login_required
@it_admin_required
def admin_approval_execute(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    approval = get_object_or_404(AutomationApproval, pk=pk)

    # 1. Verify approval is APPROVED. If not, log it as BLOCKED.
    if approval.status != AutomationApproval.ApprovalStatus.APPROVED:
        execution = execute_approved_action(approval)
        messages.error(request, f"Automation blocked: {execution.error_message}")
        referer = request.META.get('HTTP_REFERER', '')
        if 'approvals' in referer:
            return redirect('approval_detail', pk=approval.pk)
        return redirect('admin_incident_detail', pk=approval.incident.pk)

    # 2. Check if successful execution already exists (to prevent duplicate run)
    if hasattr(approval, 'execution') and approval.execution.status == AutomationExecution.ExecutionStatus.SUCCESS:
        messages.warning(request, "This approved action has already been successfully executed.")
        referer = request.META.get('HTTP_REFERER', '')
        if 'approvals' in referer:
            return redirect('approval_detail', pk=approval.pk)
        return redirect('admin_incident_detail', pk=approval.incident.pk)

    # 3. Run executor
    execution = execute_approved_action(approval)

    if execution.status == AutomationExecution.ExecutionStatus.SUCCESS:
        messages.success(request, f"Automation action completed successfully: {execution.action_name}.")
    elif execution.status == AutomationExecution.ExecutionStatus.FAILED:
        messages.error(request, f"Automation action failed: {execution.error_message or execution.output}")
    elif execution.status == AutomationExecution.ExecutionStatus.BLOCKED:
        messages.error(request, f"Automation blocked: {execution.error_message}")

    referer = request.META.get('HTTP_REFERER', '')
    if 'approvals' in referer:
        return redirect('approval_detail', pk=approval.pk)
    return redirect('admin_incident_detail', pk=approval.incident.pk)


@login_required
@it_admin_required
def execution_detail(request, pk):
    approval = get_object_or_404(AutomationApproval, pk=pk)
    execution = get_object_or_404(AutomationExecution, approval=approval)
    return render(request, 'admin_portal/execution_detail.html', {
        'approval': approval,
        'execution': execution
    })


@login_required
@it_admin_required
def admin_execution_verify(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    execution = get_object_or_404(AutomationExecution, pk=pk)

    from automation.verification import verify_execution
    is_passed, verification, msg = verify_execution(execution, actor=request.user)

    logger.info(f"[{execution.approval.incident.incident_number}] Verification performed: status={'PASSED' if is_passed else 'FAILED'}")

    if is_passed:
        messages.success(request, f"Verification PASSED: {msg} Incident marked as RESOLVED.")
    else:
        messages.warning(request, f"Verification FAILED: {msg}")

    referer = request.META.get('HTTP_REFERER', '')
    if 'execution' in referer:
        return redirect('execution_detail', pk=execution.approval.pk)
    elif 'approvals' in referer:
        return redirect('approval_detail', pk=execution.approval.pk)
    return redirect('admin_incident_detail', pk=execution.approval.incident.pk)


@login_required
@it_admin_required
def admin_approval_verify(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    approval = get_object_or_404(AutomationApproval, pk=pk)
    if not hasattr(approval, 'execution'):
        messages.error(request, "No execution record exists for this approval.")
        return redirect('approval_detail', pk=approval.pk)

    return admin_execution_verify(request, approval.execution.pk)


@login_required
@it_admin_required
def admin_audit_log_list(request):
    """
    Phase 8: Audit & Monitoring Admin Console.
    Displays a reverse-chronological list of system audit events with search, filters, and pagination.
    """
    logs_qs = AuditLog.objects.select_related('incident', 'actor').order_by('-created_at')

    # 1. Event Type filter
    event_type = request.GET.get('event_type', '').strip()
    if event_type:
        logs_qs = logs_qs.filter(event_type=event_type)

    # 2. Incident filter (number or title)
    incident_query = request.GET.get('incident', '').strip()
    if incident_query:
        logs_qs = logs_qs.filter(
            Q(incident__incident_number__icontains=incident_query) |
            Q(incident__title__icontains=incident_query)
        )

    # 3. Actor filter (username or System)
    actor_query = request.GET.get('actor', '').strip()
    if actor_query:
        if actor_query.lower() == 'system':
            logs_qs = logs_qs.filter(actor__isnull=True)
        else:
            logs_qs = logs_qs.filter(actor__username__icontains=actor_query)

    # 4. Date filter
    date_filter = request.GET.get('date', '').strip()
    if date_filter:
        now = timezone.now()
        if date_filter == 'today':
            logs_qs = logs_qs.filter(created_at__date=now.date())
        elif date_filter == 'yesterday':
            logs_qs = logs_qs.filter(created_at__date=(now - timedelta(days=1)).date())
        elif date_filter == 'week':
            logs_qs = logs_qs.filter(created_at__date__gte=(now - timedelta(days=7)).date())
        else:
            try:
                parsed_d = datetime.strptime(date_filter, '%Y-%m-%d').date()
                logs_qs = logs_qs.filter(created_at__date=parsed_d)
            except ValueError:
                pass

    # 5. Search query (across message, incident number/title, actor username)
    search_q = request.GET.get('q', '').strip()
    if search_q:
        logs_qs = logs_qs.filter(
            Q(message__icontains=search_q) |
            Q(incident__incident_number__icontains=search_q) |
            Q(incident__title__icontains=search_q) |
            Q(actor__username__icontains=search_q)
        )

    total_count = logs_qs.count()

    # Pagination: 25 items per page
    paginator = Paginator(logs_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_portal/audit_log_list.html', {
        'page_obj': page_obj,
        'event_types': AuditLog.EventType.choices,
        'current_event_type': event_type,
        'current_incident': incident_query,
        'current_actor': actor_query,
        'current_date': date_filter,
        'search_query': search_q,
        'total_count': total_count,
    })


