from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Task


@login_required
def task_list(request):
    status = request.GET.get('status', '')
    tasks = Task.objects.filter(
        archived_at__isnull=True,
    ).select_related('project')
    if status in Task.Status.values:
        tasks = tasks.filter(status=status)
    return render(request, 'tasks/list.html', {
        'tasks': tasks,
        'current_status': status,
        'status_choices': Task.Status.choices,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task.objects.select_related('project'), pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'start':
            task.status = Task.Status.IN_PROGRESS
            task.save()
            messages.success(request, 'Tâche démarrée.')

        elif action == 'complete':
            result = request.POST.get('result_summary', '').strip()
            if not result:
                messages.error(request, 'Un résumé du résultat est requis.')
            else:
                task.status = Task.Status.COMPLETED
                task.result_summary = result
                task.evidence_url = request.POST.get('evidence_url', '')
                task.completed_at = task.completed_at or task.updated_at
                if task.is_next_action:
                    task.is_next_action = False
                task.save()
                messages.success(request, 'Tâche terminée.')
                return redirect('projects:detail', slug=task.project.slug)

        elif action == 'block':
            blocker = request.POST.get('blocker_description', '').strip()
            if not blocker:
                messages.error(request, 'Une description du blocage est requise.')
            else:
                task.status = Task.Status.BLOCKED
                task.blocker_description = blocker
                task.unblock_action = request.POST.get('unblock_action', '')
                if task.is_next_action:
                    task.is_next_action = False
                task.save()
                messages.success(request, 'Tâche bloquée.')

        elif action == 'wait':
            task.status = Task.Status.WAITING
            task.review_on = request.POST.get('review_on') or None
            if task.is_next_action:
                task.is_next_action = False
            task.save()
            messages.success(request, 'Tâche mise en attente.')

        elif action == 'unblock':
            task.status = Task.Status.TODO
            task.blocker_description = ''
            task.unblock_action = ''
            task.save()
            messages.success(request, 'Blocage levé.')

        elif action == 'reactivate':
            task.status = Task.Status.TODO
            task.review_on = None
            task.save()
            messages.success(request, 'Tâche réactivée.')

        elif action == 'cancel':
            task.status = Task.Status.CANCELED
            task.canceled_reason = request.POST.get('canceled_reason', '')
            if task.is_next_action:
                task.is_next_action = False
            task.save()
            messages.success(request, 'Tâche annulée.')

        elif action == 'toggle_next':
            task.is_next_action = not task.is_next_action
            task.save()
            label = 'prochaine action' if task.is_next_action else 'normale'
            messages.success(request, f'Tâche marquée comme {label}.')

        elif action == 'edit':
            task.title = request.POST.get('title', task.title)
            task.description = request.POST.get('description', '')
            task.priority = request.POST.get('priority', task.priority)
            task.due_on = request.POST.get('due_on') or None
            task.save()
            messages.success(request, 'Tâche mise à jour.')

        return redirect('tasks:detail', pk=task.pk)

    return render(request, 'tasks/detail.html', {'task': task})
