"""
Central Audit Creation Service for Phase 8: Audit & Monitoring.

Provides a unified helper to log system-wide audit entries across
incidents, AI retrievals, approvals, automation executions, and verifications.
"""

from automation.models import AuditLog


def create_audit_log(incident, event_type, message, actor=None, metadata=None):
    """
    Creates an AuditLog entry.

    Args:
        incident (Incident): The associated incident ticket.
        event_type (str): EventType choice code (e.g. AuditLog.EventType.APPROVAL_APPROVED).
        message (str): Explanatory human-readable summary of the event.
        actor (User, optional): The user who initiated the event (or None for system).
        metadata (dict, optional): Structured context details (runbook id, match score, etc).

    Returns:
        AuditLog: The created audit log instance.
    """
    if metadata is None:
        metadata = {}

    return AuditLog.objects.create(
        incident=incident,
        event_type=event_type,
        message=message,
        actor=actor,
        metadata=metadata
    )
