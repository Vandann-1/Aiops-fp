from django.db import models
from django.conf import settings
from django.utils import timezone

class Incident(models.Model):
    class Category(models.TextChoices):
        SERVER = 'SERVER', 'Server'
        DATABASE = 'DATABASE', 'Database'
        NETWORK = 'NETWORK', 'Network'
        APPLICATION = 'APPLICATION', 'Application'
        STORAGE = 'STORAGE', 'Storage'
        SECURITY = 'SECURITY', 'Security'
        OTHER = 'OTHER', 'Other'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        ANALYZING = 'ANALYZING', 'Analyzing'
        RECOMMENDATION_READY = 'RECOMMENDATION_READY', 'Recommendation Ready'
        PENDING_APPROVAL = 'PENDING_APPROVAL', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        FAILED = 'FAILED', 'Failed'
        REJECTED = 'REJECTED', 'Rejected'

    incident_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Automatically generated unique identifier"
    )
    title = models.CharField(
        max_length=200,
        help_text="Brief title of the incident"
    )
    description = models.TextField(
        help_text="Detailed description of what happened"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.OPEN
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incidents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # 1. Generate sequential INC number on create
        if not self.incident_number:
            last_incident = Incident.objects.order_by('-id').first()
            if last_incident:
                try:
                    last_num = int(last_incident.incident_number.split('-')[1])
                    next_num = last_num + 1
                except (IndexError, ValueError):
                    next_num = last_incident.id + 1
            else:
                next_num = 1
            self.incident_number = f"INC-{next_num:04d}"

        # 2. Manage resolved_at timestamp
        if self.status == self.Status.RESOLVED:
            if not self.resolved_at:
                self.resolved_at = timezone.now()
        else:
            self.resolved_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.incident_number} - {self.title}"


class IncidentActivity(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incident_activities'
    )
    action = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.incident.incident_number} - {self.action} at {self.created_at}"
