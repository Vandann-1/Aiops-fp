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
