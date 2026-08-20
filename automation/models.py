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
