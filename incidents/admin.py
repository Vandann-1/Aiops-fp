from django.contrib import admin
from .models import Incident, IncidentActivity

class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_number', 'title', 'created_by', 'category', 'priority', 'status', 'created_at')
    list_filter = ('category', 'priority', 'status', 'created_at')
    search_fields = ('incident_number', 'title', 'description', 'created_by__username')
    ordering = ('-created_at',)

class IncidentActivityAdmin(admin.ModelAdmin):
    list_display = ('incident', 'actor', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('incident__incident_number', 'actor__username', 'description')
    ordering = ('-created_at',)

admin.site.register(Incident, IncidentAdmin)
admin.site.register(IncidentActivity, IncidentActivityAdmin)
