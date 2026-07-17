from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.projects.models import Project
from .models import Asset


@login_required
def asset_list(request):
    assets = Asset.objects.select_related('owner_project').order_by('asset_type', 'name')
    return render(request, 'registry/list.html', {'assets': assets})


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(
        Asset.objects.select_related('owner_project'), pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'verify':
            asset.last_verified_at = timezone.now()
            asset.save()
            messages.success(request, 'Actif marqué comme vérifié.')

        elif action == 'edit':
            asset.name = request.POST.get('name', asset.name)
            asset.asset_type = request.POST.get('asset_type', asset.asset_type)
            asset.status = request.POST.get('status', asset.status)
            asset.environment = request.POST.get('environment', '')
            asset.url = request.POST.get('url', '')
            asset.path = request.POST.get('path', '')
            asset.description = request.POST.get('description', '')
            asset.owner_project_id = request.POST.get('owner_project') or None
            asset.save()
            messages.success(request, 'Actif mis à jour.')

        return redirect('registry:detail', pk=asset.pk)

    projects = Project.objects.filter(archived_at__isnull=True).order_by('name')
    return render(request, 'registry/detail.html', {
        'asset': asset,
        'projects': projects,
    })


@login_required
def asset_create(request):
    if request.method == 'POST':
        asset = Asset.objects.create(
            owner_project_id=request.POST.get('owner_project') or None,
            name=request.POST.get('name', '').strip(),
            asset_type=request.POST.get('asset_type', 'application'),
            status=request.POST.get('status', 'planned'),
            environment=request.POST.get('environment', ''),
            url=request.POST.get('url', ''),
            path=request.POST.get('path', ''),
            description=request.POST.get('description', ''),
        )
        messages.success(request, 'Actif créé.')
        return redirect('registry:detail', pk=asset.pk)

    projects = Project.objects.filter(archived_at__isnull=True).order_by('name')
    return render(request, 'registry/create.html', {'projects': projects})
