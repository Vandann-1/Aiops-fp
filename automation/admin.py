from django.contrib import admin
from .models import AutomationApproval

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

admin.site.register(AutomationApproval, AutomationApprovalAdmin)
