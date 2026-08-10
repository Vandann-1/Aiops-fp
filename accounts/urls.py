from django.urls import path
from . import views
from incidents import views as incident_views

urlpatterns = [
    path('', views.home_redirect_view, name='home_redirect'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Employee Portal
    path('employee/dashboard/', incident_views.employee_dashboard, name='employee_dashboard'),
    path('employee/profile/', views.employee_profile, name='employee_profile'),
    
    # Admin Portal
    path('admin-portal/dashboard/', incident_views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/profile/', views.admin_profile, name='admin_profile'),
]
