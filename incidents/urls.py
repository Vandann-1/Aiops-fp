from django.urls import path
from . import views

urlpatterns = [
    # Employee Incident Portal URLs
    path('employee/incidents/', views.employee_incident_list, name='employee_incident_list'),
    path('employee/incidents/create/', views.employee_incident_create, name='employee_incident_create'),
    path('employee/incidents/<int:pk>/', views.employee_incident_detail, name='employee_incident_detail'),
    
    # IT Admin Incident Portal URLs
    path('admin-portal/incidents/', views.admin_incident_list, name='admin_incident_list'),
    path('admin-portal/incidents/critical/', views.admin_critical_incidents, name='admin_critical_incidents'),
    path('admin-portal/incidents/<int:pk>/', views.admin_incident_detail, name='admin_incident_detail'),
    path('admin-portal/incidents/<int:pk>/update/', views.admin_incident_update, name='admin_incident_update'),
    path('admin-portal/incidents/<int:pk>/analyze/', views.admin_incident_analyze, name='admin_incident_analyze'),
]
