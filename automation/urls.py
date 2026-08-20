from django.urls import path
from . import views

urlpatterns = [
    path('admin-portal/incidents/<int:pk>/request-approval/', views.admin_incident_request_approval, name='admin_incident_request_approval'),
    path('admin-portal/approvals/', views.approval_list, name='approval_list'),
    path('admin-portal/approvals/<int:pk>/', views.approval_detail, name='approval_detail'),
    path('admin-portal/approvals/<int:pk>/approve/', views.approve_action, name='approve_action'),
    path('admin-portal/approvals/<int:pk>/reject/', views.reject_action, name='reject_action'),
]
