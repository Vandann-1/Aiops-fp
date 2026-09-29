import logging
from django.db import models
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

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

    # Part 1 & 2: Ticket Ingestion, Normalization & AI-assisted Triage fields
    intent = models.CharField(
        max_length=50,
        default='Unknown',
        blank=True,
        help_text="Normalized intent classification (e.g. Service Degradation)"
    )
    service = models.CharField(
        max_length=50,
        default='Unknown',
        blank=True,
        help_text="Classified infrastructure service (e.g. Web Server)"
    )
    classified_priority = models.CharField(
        max_length=10,
        default='P3',
        blank=True,
        help_text="Suggested triage priority (P1, P2, P3, P4)"
    )
    normalized_description = models.TextField(
        blank=True,
        default='',
        help_text="Deterministic normalized problem description"
    )
    classification_method = models.CharField(
        max_length=80,
        default='Rule-based local classification',
        blank=True,
        help_text="Triage classification algorithm description"
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

        # 2. Normalize and classify if intent is not yet populated
        normalized_now = False
        if not self.intent or self.intent == 'Unknown':
            try:
                from incidents.normalization import normalize_incident_data
                norm = normalize_incident_data(self.title, self.description, category=self.category)
                self.intent = norm['intent']
                self.service = norm['service']
                self.classified_priority = norm['classified_priority']
                if not self.normalized_description:
                    self.normalized_description = norm['normalized_description']
                self.classification_method = norm['classification_method']
                normalized_now = True
            except Exception:
                pass

        # 3. Manage resolved_at timestamp
        if self.status == self.Status.RESOLVED:
            if not self.resolved_at:
                self.resolved_at = timezone.now()
        else:
            self.resolved_at = None

        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            logger.info(f"[{self.incident_number}] Incident created: {self.title}")
        if normalized_now:
            logger.info(f"[{self.incident_number}] Incident normalized: Intent={self.intent}, Service={self.service}, Priority={self.classified_priority}")

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


class IncidentFeedback(models.Model):
    """
    Phase 9 & 10: Feedback workflow for resolved incidents.
    One feedback record per incident from the reporter.
    """
    incident = models.OneToOneField(
        Incident,
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text="The incident ticket this feedback belongs to"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incident_feedbacks',
        help_text="Employee who provided feedback"
    )
    rating = models.IntegerField(
        choices=[(1, '1 ★'), (2, '2 ★'), (3, '3 ★'), (4, '4 ★'), (5, '5 ★')],
        help_text="Runbook usefulness rating (1-5)"
    )
    comment = models.TextField(
        blank=True,
        help_text="Suggestions or comments on runbook improvement"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.incident.incident_number}: {self.rating}/5 by {self.user.username}"
