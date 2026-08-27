from django.contrib import admin
from .models import AutomationApproval, AutomationExecution

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

admin.site.register(AutomationApproval, AutomationApprovalAdmin)
admin.site.register(AutomationExecution, AutomationExecutionAdmin)
