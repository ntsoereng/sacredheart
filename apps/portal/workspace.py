"""Personal data is always scoped to the session user, never model permissions."""
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import PersonalPlan, PersonalTask


class TaskForm(forms.ModelForm):
    class Meta:
        model = PersonalTask
        fields = ['title', 'due_date', 'priority', 'status', 'notes']
        widgets = {
            'due_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class PlanForm(forms.ModelForm):
    class Meta:
        model = PersonalPlan
        fields = ['notes']
        labels = {'notes': 'My planning notes'}
        widgets = {'notes': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Goals, meeting preparation, ideas and plans…'})}


@never_cache
@login_required
@require_http_methods(['GET', 'POST'])
def workspace(request):
    tasks = PersonalTask.objects.filter(owner=request.user)
    plan = PersonalPlan.objects.filter(owner=request.user).first()
    plan_form = PlanForm(instance=plan)
    if request.method == 'POST':
        plan_form = PlanForm(request.POST, instance=plan)
        if plan_form.is_valid():
            saved = plan_form.save(commit=False)
            saved.owner = request.user
            saved.save()
            messages.success(request, 'Planning notes saved.')
            return redirect('workspace')
    today = timezone.localdate()
    active = tasks.exclude(status='done')
    counts = {'open': active.count(), 'today': active.filter(due_date=today).count(), 'overdue': active.filter(due_date__lt=today).count(), 'done': tasks.filter(status='done').count()}
    selected = request.GET.get('filter', 'open')
    filters = {'open': active, 'today': active.filter(due_date=today), 'overdue': active.filter(due_date__lt=today), 'done': tasks.filter(status='done'), 'all': tasks}
    if selected not in filters:
        selected = 'open'
    from django.core.paginator import Paginator
    page = Paginator(filters[selected], 20).get_page(request.GET.get('page'))
    return render(request, 'portal/workspace.html', {'page_obj': page, 'counts': counts, 'selected': selected, 'plan_form': plan_form})


@never_cache
@login_required
@require_http_methods(['GET', 'POST'])
def task_form(request, pk=None):
    task = get_object_or_404(PersonalTask, pk=pk, owner=request.user) if pk is not None else None
    form = TaskForm(request.POST if request.method == 'POST' else None, instance=task)
    if request.method == 'POST' and form.is_valid():
        saved = form.save(commit=False)
        saved.owner = request.user
        saved.save()
        messages.success(request, 'Task saved.')
        return redirect('workspace')
    return render(request, 'portal/workspace_task.html', {'form': form, 'task': task})


@never_cache
@login_required
@require_http_methods(['POST'])
def task_action(request, pk, action):
    task = get_object_or_404(PersonalTask, pk=pk, owner=request.user)
    if action == 'delete':
        task.delete()
        messages.success(request, 'Task deleted.')
    else:
        task.status = 'done' if action == 'complete' else 'todo'
        task.save(update_fields=['status'])
    return redirect('workspace')
