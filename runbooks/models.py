from django.db import models
from django.conf import settings
from incidents.models import Incident

class Runbook(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    runbook_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Automatically generated unique identifier"
    )
    title = models.CharField(
        max_length=200,
        help_text="Brief title of the runbook"
    )
    description = models.TextField(
        help_text="A clear description of what problem the runbook solves"
    )
    category = models.CharField(
        max_length=20,
        choices=Incident.Category.choices,
        default=Incident.Category.OTHER,
        help_text="Service category this runbook applies to"
    )
    symptoms = models.TextField(
        help_text="Symptoms or conditions under which this runbook should be used"
    )
    steps = models.TextField(
        help_text="Step-by-step troubleshooting or resolution procedure"
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM
    )
    automation_action = models.CharField(
        max_length=100,
        blank=True,
        help_text="Associated automation action (metadata only)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Deactivate rather than delete runbooks to preserve history"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='runbooks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Generate sequential RB number on create
        if not self.runbook_number:
            last_rb = Runbook.objects.order_by('-id').first()
            if last_rb:
                try:
                    last_num = int(last_rb.runbook_number.split('-')[1])
                    next_num = last_num + 1
                except (IndexError, ValueError):
                    next_num = last_rb.id + 1
            else:
                next_num = 1
            self.runbook_number = f"RB-{next_num:04d}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.runbook_number} - {self.title}"


class RunbookRecommendation(models.Model):
    incident = models.OneToOneField(
        'incidents.Incident',
        on_delete=models.CASCADE,
        related_name='runbook_recommendation',
        help_text="The incident ticket this recommendation belongs to"
    )
    runbook = models.ForeignKey(
        Runbook,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendations',
        help_text="The recommended runbook procedure"
    )
    match_score = models.FloatField(
        help_text="Semantic matching similarity score"
    )
    retrieval_engine = models.CharField(
        max_length=50,
        default='tfidf',
        help_text="Algorithm identifier used to generate match scores"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        rb_num = self.runbook.runbook_number if self.runbook else "None"
        return f"Rec for {self.incident.incident_number}: {rb_num} ({self.match_score * 100:.2f}%)"

    @property
    def match_score_percentage(self):
        return self.match_score * 100
