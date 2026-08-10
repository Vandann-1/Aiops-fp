from django.urls import path
from . import views

urlpatterns = [
    # Admin Portal Runbook Management URLs
    path('admin-portal/runbooks/', views.runbook_list, name='runbook_list'),
    path('admin-portal/runbooks/create/', views.runbook_create, name='runbook_create'),
    path('admin-portal/runbooks/<int:pk>/', views.runbook_detail, name='runbook_detail'),
    path('admin-portal/runbooks/<int:pk>/edit/', views.runbook_edit, name='runbook_edit'),
    path('admin-portal/runbooks/<int:pk>/toggle/', views.runbook_toggle_active, name='runbook_toggle_active'),
]
