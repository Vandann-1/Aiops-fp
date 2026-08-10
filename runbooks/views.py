from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from accounts.decorators import it_admin_required
from incidents.models import Incident
from .models import Runbook
from .forms import RunbookForm

@login_required
@it_admin_required
def runbook_list(request):
    runbooks_list = Runbook.objects.all()

    # Search: checks runbook_number, title, description, symptoms
    q = request.GET.get('search', request.GET.get('q', '')).strip()
    if q:
        runbooks_list = runbooks_list.filter(
            Q(runbook_number__icontains=q) |
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(symptoms__icontains=q)
        )

    # Category Filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        runbooks_list = runbooks_list.filter(category=category_filter)

    # Risk Level Filter
    risk_filter = request.GET.get('risk', '').strip()
    if risk_filter:
        runbooks_list = runbooks_list.filter(risk_level=risk_filter)

    # Active Status Filter
    active_filter = request.GET.get('active', '').strip()
    if active_filter == 'true':
        runbooks_list = runbooks_list.filter(is_active=True)
    elif active_filter == 'false':
        runbooks_list = runbooks_list.filter(is_active=False)

    # Pagination: 10 runbooks per page
    paginator = Paginator(runbooks_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Choices context for filtering dropdowns
    categories = Incident.Category.choices
    risks = Runbook.RiskLevel.choices

    return render(request, 'admin_portal/runbook_list.html', {
        'page_obj': page_obj,
        'q': q,
        'category_filter': category_filter,
        'risk_filter': risk_filter,
        'active_filter': active_filter,
        'categories': categories,
        'risks': risks
    })

@login_required
@it_admin_required
def runbook_create(request):
    if request.method == 'POST':
        form = RunbookForm(request.POST)
        if form.is_valid():
            runbook = form.save(commit=False)
            runbook.created_by = request.user
            runbook.save()
            messages.success(request, f"Runbook {runbook.runbook_number} created successfully.")
            return redirect('runbook_detail', pk=runbook.pk)
    else:
        form = RunbookForm()

    return render(request, 'admin_portal/runbook_create.html', {'form': form})

@login_required
@it_admin_required
def runbook_detail(request, pk):
    runbook = get_object_or_404(Runbook, pk=pk)
    return render(request, 'admin_portal/runbook_detail.html', {'runbook': runbook})

@login_required
@it_admin_required
def runbook_edit(request, pk):
    runbook = get_object_or_404(Runbook, pk=pk)
    if request.method == 'POST':
        form = RunbookForm(request.POST, instance=runbook)
        if form.is_valid():
            form.save()
            messages.success(request, f"Runbook {runbook.runbook_number} updated successfully.")
            return redirect('runbook_detail', pk=runbook.pk)
    else:
        form = RunbookForm(instance=runbook)

    return render(request, 'admin_portal/runbook_edit.html', {
        'form': form,
        'runbook': runbook
    })

@login_required
@it_admin_required
def runbook_toggle_active(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    runbook = get_object_or_404(Runbook, pk=pk)
    runbook.is_active = not runbook.is_active
    runbook.save()

    if runbook.is_active:
        messages.success(request, f"Runbook {runbook.runbook_number} activated successfully.")
    else:
        messages.warning(request, f"Runbook {runbook.runbook_number} deactivated successfully. It will not be queryable for future AI runbook retrieval.")

    return redirect('runbook_detail', pk=runbook.pk)
