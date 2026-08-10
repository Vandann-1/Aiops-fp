from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from .forms import ProfileUpdateForm
from .utils import is_it_admin, is_employee
from .decorators import employee_required, it_admin_required

def home_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if is_it_admin(request.user):
        return redirect('admin_dashboard')
    return redirect('employee_dashboard')

def login_view(request):
    if request.user.is_authenticated:
        if is_it_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('employee_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if is_it_admin(user):
                return redirect('admin_dashboard')
            return redirect('employee_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'login.html')

def logout_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], "Method not allowed. Logout requires a POST request.")
    
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
@employee_required
def employee_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('employee_profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
        
    return render(request, 'employee/profile.html', {'form': form})

@login_required
@it_admin_required
def admin_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('admin_profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
        
    return render(request, 'admin_portal/profile.html', {'form': form})
