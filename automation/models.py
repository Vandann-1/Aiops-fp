from django.db import models
from django.conf import settings
from incidents.models import Incident
from runbooks.models import Runbook

class AutomationApproval(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='approvals',
        help_text="The incident ticket associated with this approval request"
    )
    runbook = models.ForeignKey(
        Runbook,
        on_delete=models.CASCADE,
        related_name='approvals',
        help_text="The recommended runbook procedure to be approved"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_approvals',
        help_text="The IT Admin who requested approval"
    )
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        help_text="Current state of the human approval workflow"
    )
    reason = models.TextField(
        blank=True,
        help_text="Notes for approval or reason for rejection"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_approvals',
        help_text="The IT Admin who reviewed the request"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request was approved or rejected"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Approval {self.id} for {self.incident.incident_number}: {self.status}"


class AutomationExecution(models.Model):
    class ExecutionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        BLOCKED = 'BLOCKED', 'Blocked'

    approval = models.OneToOneField(
        AutomationApproval,
        on_delete=models.CASCADE,
        related_name='execution',
        help_text="The approval request this execution record belongs to"
    )
    action_name = models.CharField(
        max_length=100,
        help_text="Predefined action hook name being executed"
    )
    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING
    )
    output = models.TextField(
        blank=True,
        help_text="Standard output from simulated execution"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if execution failed or was blocked"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the execution started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the execution completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Execution for Approval #{self.approval.id}: {self.status}"


class VerificationResult(models.Model):
    class Status(models.TextChoices):
        PASSED = 'PASSED', 'Passed'
        FAILED = 'FAILED', 'Failed'

    execution = models.OneToOneField(
        AutomationExecution,
        on_delete=models.CASCADE,
        related_name='verification',
        help_text="The automation execution record being verified"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        help_text="Outcome of the simulated verification check"
    )
    message = models.TextField(
        blank=True,
        help_text="Detailed output message from the verification simulation"
    )
    checked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when verification was performed"
    )

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        return f"Verification for Execution #{self.execution.id}: {self.status}"


class AuditLog(models.Model):
    class EventType(models.TextChoices):
        INCIDENT_CREATED = 'INCIDENT_CREATED', 'Incident Created'
        AI_ANALYSIS_COMPLETED = 'AI_ANALYSIS_COMPLETED', 'AI Analysis Completed'
        RUNBOOK_RECOMMENDED = 'RUNBOOK_RECOMMENDED', 'Runbook Recommended'
        APPROVAL_REQUESTED = 'APPROVAL_REQUESTED', 'Approval Requested'
        APPROVAL_APPROVED = 'APPROVAL_APPROVED', 'Approval Approved'
        APPROVAL_REJECTED = 'APPROVAL_REJECTED', 'Approval Rejected'
        AUTOMATION_STARTED = 'AUTOMATION_STARTED', 'Automation Started'
        AUTOMATION_COMPLETED = 'AUTOMATION_COMPLETED', 'Automation Completed'
        AUTOMATION_FAILED = 'AUTOMATION_FAILED', 'Automation Failed'
        AUTOMATION_BLOCKED = 'AUTOMATION_BLOCKED', 'Automation Blocked'
        VERIFICATION_STARTED = 'VERIFICATION_STARTED', 'Verification Started'
        VERIFICATION_PASSED = 'VERIFICATION_PASSED', 'Verification Passed'
        VERIFICATION_FAILED = 'VERIFICATION_FAILED', 'Verification Failed'
        INCIDENT_RESOLVED = 'INCIDENT_RESOLVED', 'Incident Resolved'
        INCIDENT_ESCALATED = 'INCIDENT_ESCALATED', 'Incident Escalated'

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text="The incident ticket associated with this audit entry"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="The user who triggered this event (or NULL for automated system actions)"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        help_text="Type of audit event"
    )
    message = models.TextField(
        help_text="Human-readable audit message describing what occurred"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured event metadata (e.g., match score, action name, error reason)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the audit log entry was generated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.incident.incident_number} - {self.event_type} by {actor_name}"

    @property
    def badge_class(self):
        mapping = {
            self.EventType.INCIDENT_CREATED: 'bg-info text-dark',
            self.EventType.AI_ANALYSIS_COMPLETED: 'bg-info text-dark',
            self.EventType.RUNBOOK_RECOMMENDED: 'bg-primary text-white',
            self.EventType.APPROVAL_REQUESTED: 'bg-warning text-dark',
            self.EventType.APPROVAL_APPROVED: 'bg-success text-white',
            self.EventType.APPROVAL_REJECTED: 'bg-danger text-white',
            self.EventType.AUTOMATION_STARTED: 'bg-info text-dark',
            self.EventType.AUTOMATION_COMPLETED: 'bg-success text-white',
            self.EventType.AUTOMATION_FAILED: 'bg-danger text-white',
            self.EventType.AUTOMATION_BLOCKED: 'bg-warning text-dark',
            self.EventType.VERIFICATION_STARTED: 'bg-info text-dark',
            self.EventType.VERIFICATION_PASSED: 'bg-success text-white',
            self.EventType.VERIFICATION_FAILED: 'bg-danger text-white',
            self.EventType.INCIDENT_RESOLVED: 'bg-success text-white',
            self.EventType.INCIDENT_ESCALATED: 'bg-warning text-dark',
        }
        return mapping.get(self.event_type, 'bg-secondary text-white')

    @property
    def actor_display(self):
        if self.actor:
            return self.actor.username
        return "System"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Incident)
def log_incident_creation_audit(sender, instance, created, **kwargs):
    """
    Automatically records INCIDENT_CREATED audit event upon Incident insertion.
    """
    if created:
        if not AuditLog.objects.filter(incident=instance, event_type=AuditLog.EventType.INCIDENT_CREATED).exists():
            AuditLog.objects.create(
                incident=instance,
                event_type=AuditLog.EventType.INCIDENT_CREATED,
                message=f"Incident {instance.incident_number} was created.",
                actor=instance.created_by,
                metadata={"incident_number": instance.incident_number, "title": instance.title}
            )


