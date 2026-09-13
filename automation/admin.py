from django.contrib import admin
from .models import AutomationApproval, AutomationExecution, VerificationResult

class AutomationApprovalAdmin(admin.ModelAdmin):
    list_display = (
        'incident',
        'runbook',
        'status',
        'requested_by',
        'reviewed_by',
        'created_at',
        'reviewed_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'incident__incident_number',
        'incident__title',
        'runbook__runbook_number',
        'runbook__title'
    )

class AutomationExecutionAdmin(admin.ModelAdmin):
    list_display = (
        'approval',
        'action_name',
        'status',
        'started_at',
        'completed_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'approval__incident__incident_number',
        'approval__runbook__title',
        'action_name'
    )

class VerificationResultAdmin(admin.ModelAdmin):
    list_display = (
        'execution',
        'status',
        'checked_at'
    )
    list_filter = ('status', 'checked_at')
    search_fields = (
        'execution__approval__incident__incident_number',
        'execution__action_name',
        'message'
    )

admin.site.register(AutomationApproval, AutomationApprovalAdmin)
admin.site.register(AutomationExecution, AutomationExecutionAdmin)
admin.site.register(VerificationResult, VerificationResultAdmin)

