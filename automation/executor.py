from django.utils import timezone
from incidents.models import Incident, IncidentActivity
from automation.models import AutomationApproval, AutomationExecution
from automation.actions import SAFE_ACTIONS

def validate_automation(approval):
    """
    Perform all Phase 6 safety validations on the given approval request.
    Returns: (is_valid, error_reason)
    """
    # 1. Approval exists
    if not approval:
        return False, "Approval object does not exist."
    
    # 2. Approval status must be APPROVED
    if approval.status != AutomationApproval.ApprovalStatus.APPROVED:
        return False, "Approval status must be APPROVED."
        
    # 3. Incident exists
    if not hasattr(approval, 'incident') or not approval.incident:
        return False, "Incident does not exist."
        
    # 4. Runbook exists
    if not hasattr(approval, 'runbook') or not approval.runbook:
        return False, "Runbook does not exist."
        
    # 5. Runbook is active
    if not approval.runbook.is_active:
        return False, "Runbook is no longer active."
        
    # 6. automation_action exists
    action_name = approval.runbook.automation_action
    if not action_name:
        return False, "Runbook does not have an associated automation action."
        
    # 7. automation_action exists in SAFE_ACTIONS
    if action_name not in SAFE_ACTIONS:
        return False, "Action is not present in the approved automation allowlist."
        
    # 8. Incident is not already resolved
    if approval.incident.status == Incident.Status.RESOLVED:
        return False, "Incident is already resolved."
        
    # 9. No previous successful execution exists
    if AutomationExecution.objects.filter(approval=approval, status=AutomationExecution.ExecutionStatus.SUCCESS).exists():
        return False, "This approved action has already been successfully executed."
        
    return True, None

def execute_approved_action(approval):
    """
    Validates and executes the mock automation action associated with the approval request.
    Stores results in AutomationExecution and logs activity to the incident timeline.
    """
    # Prevent duplicate successful execution first
    if approval:
        existing_success = AutomationExecution.objects.filter(
            approval=approval,
            status=AutomationExecution.ExecutionStatus.SUCCESS
        ).first()
        if existing_success:
            return existing_success

    is_valid, reason = validate_automation(approval)
    action_name = approval.runbook.automation_action if (approval and approval.runbook and approval.runbook.automation_action) else "unknown"
    
    # Check if an execution already exists for this approval
    execution, created = AutomationExecution.objects.get_or_create(
        approval=approval,
        defaults={
            "action_name": action_name,
            "status": AutomationExecution.ExecutionStatus.PENDING
        }
    )
    
    if not is_valid:
        execution.status = AutomationExecution.ExecutionStatus.BLOCKED
        execution.error_message = reason
        execution.completed_at = timezone.now()
        execution.save()
        
        # Log to activity history
        IncidentActivity.objects.create(
            incident=approval.incident,
            action='AUTOMATION_BLOCKED',
            description="Automation action blocked by safety validation.",
            actor=approval.reviewed_by or approval.requested_by
        )
        return execution
        
    # Transition to RUNNING
    execution.status = AutomationExecution.ExecutionStatus.RUNNING
    execution.started_at = timezone.now()
    execution.action_name = action_name
    execution.error_message = ""
    execution.output = ""
    execution.save()
    
    # Log execution start
    IncidentActivity.objects.create(
        incident=approval.incident,
        action='AUTOMATION_STARTED',
        description=f"Approved automation action started: {action_name}.",
        actor=approval.reviewed_by or approval.requested_by
    )
    
    try:
        # Retrieve the mock executor function from allowlist
        executor_func = SAFE_ACTIONS[action_name]
        result = executor_func()
        
        if result.get("success", False):
            execution.status = AutomationExecution.ExecutionStatus.SUCCESS
            execution.output = result.get("message", "Simulated execution completed successfully.")
            execution.completed_at = timezone.now()
            execution.save()
            
            # Log success
            IncidentActivity.objects.create(
                incident=approval.incident,
                action='AUTOMATION_SUCCESS',
                description=f"Automation action completed successfully: {action_name}.",
                actor=approval.reviewed_by or approval.requested_by
            )
        else:
            execution.status = AutomationExecution.ExecutionStatus.FAILED
            execution.error_message = result.get("message", "Simulation failed.")
            execution.completed_at = timezone.now()
            execution.save()
            
            # Log failure
            IncidentActivity.objects.create(
                incident=approval.incident,
                action='AUTOMATION_FAILED',
                description=f"Automation action failed: {action_name}.",
                actor=approval.reviewed_by or approval.requested_by
            )
    except Exception as e:
        execution.status = AutomationExecution.ExecutionStatus.FAILED
        execution.error_message = str(e)
        execution.completed_at = timezone.now()
        execution.save()
        
        # Log failure
        IncidentActivity.objects.create(
            incident=approval.incident,
            action='AUTOMATION_FAILED',
            description=f"Automation action failed: {action_name}.",
            actor=approval.reviewed_by or approval.requested_by
        )
        
    return execution
