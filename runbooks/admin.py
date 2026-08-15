from django.contrib import admin
from .models import Runbook, RunbookRecommendation

class RunbookAdmin(admin.ModelAdmin):
    list_display = (
        'runbook_number',
        'title',
        'category',
        'risk_level',
        'is_active',
        'created_by',
        'created_at'
    )
    list_filter = (
        'category',
        'risk_level',
        'is_active',
        'created_at'
    )
    search_fields = (
        'runbook_number',
        'title',
        'description',
        'symptoms',
        'created_by__username'
    )
    ordering = ('-created_at',)

admin.site.register(Runbook, RunbookAdmin)


class RunbookRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'incident',
        'runbook',
        'match_score',
        'retrieval_method',
        'created_at'
    )
    list_filter = (
        'created_at',
        'runbook__category'
    )
    search_fields = (
        'incident__incident_number',
        'incident__title',
        'runbook__runbook_number',
        'runbook__title'
    )
    ordering = ('-created_at',)

admin.site.register(RunbookRecommendation, RunbookRecommendationAdmin)
