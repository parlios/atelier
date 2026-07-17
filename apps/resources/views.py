from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.projects.models import Project
from .models import Resource


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(
        Resource.objects.select_related('project'), pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'edit':
            resource.title = request.POST.get('title', resource.title)
            resource.resource_type = request.POST.get('resource_type', resource.resource_type)
            resource.content = request.POST.get('content', '')
            resource.source_url = request.POST.get('source_url', '')
            resource.source_path = request.POST.get('source_path', '')
            resource.project_id = request.POST.get('project') or None
            resource.save()
            messages.success(request, 'Ressource mise à jour.')

        return redirect('resources:detail', pk=resource.pk)

    projects = Project.objects.filter(archived_at__isnull=True).order_by('name')
    return render(request, 'resources/detail.html', {
        'resource': resource,
        'projects': projects,
    })


@login_required
def resource_create(request):
    if request.method == 'POST':
        resource = Resource.objects.create(
            project_id=request.POST.get('project') or None,
            title=request.POST.get('title', '').strip(),
            resource_type=request.POST.get('resource_type', 'note'),
            content=request.POST.get('content', ''),
            source_url=request.POST.get('source_url', ''),
            source_path=request.POST.get('source_path', ''),
        )
        messages.success(request, 'Ressource créée.')
        return redirect('resources:detail', pk=resource.pk)

    projects = Project.objects.filter(archived_at__isnull=True).order_by('name')
    return render(request, 'resources/create.html', {'projects': projects})


@login_required
def resource_list(request):
    resources = Resource.objects.select_related('project').order_by(
        '-updated_at',
    )[:50]
    return render(request, 'resources/list.html', {'resources': resources})
