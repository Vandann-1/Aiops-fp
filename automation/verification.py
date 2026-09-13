"""
Simulated Verification Engine for Phase 7: Execution & Verification.

This module provides safe, deterministic simulated verification functions
to confirm whether an approved automation action achieved its intended outcome.
NO real OS commands, subprocesses, subshells, exec, or eval are used.
"""

from django.utils import timezone
from incidents.models import Incident, IncidentActivity
from automation.models import AutomationExecution, VerificationResult

def verify_nginx():
    return {
        "success": True,
        "message": "Simulated verification: Nginx service is responding normally."
    }

def verify_apache():
    return {
        "success": True,
        "message": "Simulated verification: Apache service is responding normally."
    }

def verify_disk_space():
    return {
        "success": True,
        "message": "Simulated verification: Disk space is within acceptable limits."
    }

def verify_network():
    return {
        "success": True,
        "message": "Simulated verification: Network connectivity is healthy."
    }

def verify_postgresql():
    return {
        "success": True,
        "message": "Simulated verification: PostgreSQL database connectivity verified."
    }

def verify_mysql():
    return {
        "success": True,
        "message": "Simulated verification: MySQL service connectivity verified."
    }

def verify_dns():
    return {
        "success": True,
        "message": "Simulated verification: DNS resolution is functioning properly."
    }

def verify_restart_application():
    return {
        "success": True,
        "message": "Simulated verification: Application service health check passed."
    }

def verify_clear_application_cache():
    return {
        "success": True,
        "message": "Simulated verification: Application cache invalidated and regenerated."
    }

def verify_check_ssl_certificate():
    return {
        "success": True,
        "message": "Simulated verification: SSL certificate is valid and trusted."
    }

def verify_check_cpu_usage():
    return {
        "success": True,
        "message": "Simulated verification: CPU usage has returned to normal operational limits."
    }

def verify_check_memory_usage():
    return {
        "success": True,
        "message": "Simulated verification: Memory usage has normalized within safe thresholds."
    }

def verify_simulate_failure():
    return {
        "success": False,
        "message": "Simulated verification failed: Service response check failed."
    }

SAFE_VERIFICATIONS = {
    "restart_nginx": verify_nginx,
    "restart_apache": verify_apache,
    "check_disk_space": verify_disk_space,
    "check_network": verify_network,
    "restart_postgresql": verify_postgresql,
    "restart_mysql": verify_mysql,
    "check_dns": verify_dns,
    "restart_application": verify_restart_application,
    "clear_application_cache": verify_clear_application_cache,
    "check_ssl_certificate": verify_check_ssl_certificate,
    "check_cpu_usage": verify_check_cpu_usage,
    "check_memory_usage": verify_check_memory_usage,
    "simulate_failure": verify_simulate_failure,
    "simulate_verification_failure": verify_simulate_failure,
}

def verify_execution(execution, actor=None):
    """
    Validates and performs a safe simulated verification on a completed, successful execution.
    Transitions incident to RESOLVED if PASSED, or keeps it IN_PROGRESS if FAILED.
    Returns: (is_passed, verification_result, message)
    """
    # 1. Confirm execution exists
    if not execution:
        return False, None, "Execution record does not exist."

    # 2. Confirm execution status is strictly SUCCESS
    if execution.status != AutomationExecution.ExecutionStatus.SUCCESS:
        return False, None, f"Only successful executions can be verified. Current status: {execution.status}."

    # 3. Confirm execution has completed
    if not execution.completed_at:
        return False, None, "Execution has not yet completed."

    # 4. Confirm approval relationship
    approval = getattr(execution, 'approval', None)
    if not approval:
        return False, None, "Execution approval relationship is missing or invalid."

    # 5. Confirm incident relationship
    incident = getattr(approval, 'incident', None)
    if not incident:
        return False, None, "Incident associated with approval is missing."

    # 6. Confirm runbook relationship
    runbook = getattr(approval, 'runbook', None)
    if not runbook:
        return False, None, "Runbook associated with approval is missing."

    # 7. Check if runbook is active
    if not runbook.is_active:
        return False, None, "The runbook is no longer active. Verification cannot proceed."

    # 8. Check if incident is already resolved
    if incident.status == Incident.Status.RESOLVED:
        return False, None, "Incident is already resolved."

    # 9. Prevent duplicate successful verification
    if hasattr(execution, 'verification') and execution.verification.status == VerificationResult.Status.PASSED:
        return False, execution.verification, "This execution has already been successfully verified."

    # 10. Perform simulated verification lookup
    action_name = execution.action_name
    verification_func = SAFE_VERIFICATIONS.get(action_name)
    if not verification_func:
        # Fallback safe simulation check if action is not explicitly listed in verifications
        result = {
            "success": False,
            "message": f"Simulated verification failed: No verification procedure defined for '{action_name}'."
        }
    else:
        try:
            result = verification_func()
        except Exception as e:
            result = {
                "success": False,
                "message": f"Simulated verification error: {str(e)}"
            }

    is_passed = result.get("success", False)
    verification_status = VerificationResult.Status.PASSED if is_passed else VerificationResult.Status.FAILED
    verification_msg = result.get("message", "Simulated verification complete.")

    # 11. Create or update VerificationResult
    verification, created = VerificationResult.objects.update_or_create(
        execution=execution,
        defaults={
            "status": verification_status,
            "message": verification_msg,
            "checked_at": timezone.now()
        }
    )

    # 12. Handle Incident Resolution & Timeline Logging
    if is_passed:
        # Resolve incident
        incident.status = Incident.Status.RESOLVED
        incident.save()

        # Log timeline event
        IncidentActivity.objects.create(
            incident=incident,
            actor=actor or approval.reviewed_by or approval.requested_by,
            action='AUTOMATION_VERIFIED',
            description="Automation execution verified successfully. Incident resolved."
        )
    else:
        # Keep incident open / in progress
        incident.status = Incident.Status.IN_PROGRESS
        incident.save()

        # Log timeline event
        IncidentActivity.objects.create(
            incident=incident,
            actor=actor or approval.reviewed_by or approval.requested_by,
            action='VERIFICATION_FAILED',
            description="Automation verification failed. Manual investigation required."
        )

    return is_passed, verification, verification_msg
