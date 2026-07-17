from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.decisions.models import Decision
from apps.projects.models import Project
from apps.resources.models import Resource
from apps.tasks.models import Task

from .models import InboxItem


@login_required
def inbox_list(request):
    unprocessed = InboxItem.objects.filter(
        status=InboxItem.Status.UNPROCESSED,
    ).select_related('suggested_project')

    processed = InboxItem.objects.filter(
        status__in=[InboxItem.Status.PROCESSED, InboxItem.Status.DISCARDED],
    ).select_related(
        'suggested_project',
        'destination_project',
        'destination_task',
        'destination_decision',
        'destination_resource',
    )[:50]

    projects = Project.objects.filter(archived_at__isnull=True).order_by('name')

    return render(request, 'inbox/list.html', {
        'unprocessed': unprocessed,
        'processed': processed,
        'projects': projects,
    })


@login_required
def inbox_capture(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            InboxItem.objects.create(
                title=title,
                notes=request.POST.get('notes', ''),
                suggested_type=request.POST.get('suggested_type', ''),
                suggested_project_id=request.POST.get('suggested_project') or None,
                source_url=request.POST.get('source_url', ''),
            )
            messages.success(request, 'Élément capturé.')
        else:
            messages.error(request, 'Un titre est requis.')
    return redirect('inbox:list')


@login_required
def inbox_qualify(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'discard':
            item.status = InboxItem.Status.DISCARDED
            item.discarded_reason = request.POST.get('discarded_reason', '')
            item.processed_at = timezone.now()
            item.save()
            messages.success(request, 'Élément écarté.')

        elif action == 'to_project':
            project = Project.objects.create(
                name=item.title,
                problem_statement=item.notes,
            )
            item.status = InboxItem.Status.PROCESSED
            item.destination_project = project
            item.processed_at = timezone.now()
            item.save()
            messages.success(request, f'Projet « {project.name} » créé.')

        elif action == 'to_task':
            project_id = request.POST.get('project')
            if not project_id:
                messages.error(request, 'Un projet est requis pour créer une tâche.')
                return redirect('inbox:list')
            project = get_object_or_404(Project, pk=project_id)
            task = Task.objects.create(
                project=project,
                title=item.title,
                description=item.notes,
            )
            item.status = InboxItem.Status.PROCESSED
            item.destination_task = task
            item.processed_at = timezone.now()
            item.save()
            messages.success(request, f'Tâche créée dans « {project.name} ».')

        elif action == 'to_decision':
            project_id = request.POST.get('project')
            if not project_id:
                messages.error(request, 'Un projet est requis.')
                return redirect('inbox:list')
            project = get_object_or_404(Project, pk=project_id)
            decision = Decision.objects.create(
                project=project,
                title=item.title,
                context=item.notes,
                question=item.title,
            )
            item.status = InboxItem.Status.PROCESSED
            item.destination_decision = decision
            item.processed_at = timezone.now()
            item.save()
            messages.success(request, f'Décision créée dans « {project.name} ».')

        elif action == 'to_resource':
            project_id = request.POST.get('project') or None
            resource = Resource.objects.create(
                project_id=project_id,
                title=item.title,
                resource_type=request.POST.get('resource_type', 'note'),
                content=item.notes,
                source_url=item.source_url,
            )
            item.status = InboxItem.Status.PROCESSED
            item.destination_resource = resource
            item.processed_at = timezone.now()
            item.save()
            messages.success(request, 'Ressource créée.')

        else:
            messages.error(request, 'Action inconnue.')

        return redirect('inbox:list')

    projects = Project.objects.filter(archived_at__isnull=True).order_by('name')
    return render(request, 'inbox/qualify.html', {
        'item': item,
        'projects': projects,
    })
