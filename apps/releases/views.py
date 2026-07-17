from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.projects.models import Project
from .models import Release


@login_required
def release_list(request):
    status = request.GET.get('status', '')
    releases = Release.objects.filter(
        archived_at__isnull=True,
    ).select_related('project', 'asset')
    if status in Release.Status.values:
        releases = releases.filter(status=status)
    return render(request, 'releases/list.html', {
        'releases': releases,
        'current_status': status,
        'status_choices': Release.Status.choices,
    })


@login_required
def release_detail(request, pk):
    release = get_object_or_404(
        Release.objects.select_related('project', 'asset'), pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'release':
            release.status = Release.Status.RELEASED
            release.released_at = timezone.now()
            release.save()
            messages.success(request, 'Version livrée.')

        elif action == 'validate':
            result = request.POST.get('validation_result', '').strip()
            if not result:
                messages.error(request, 'Un résultat de validation est requis.')
            else:
                release.status = Release.Status.VALIDATED
                release.validation_result = result
                release.validated_at = timezone.now()
                if not release.released_at:
                    release.released_at = timezone.now()
                release.save()
                messages.success(request, 'Version validée.')

        elif action == 'fail':
            result = request.POST.get('validation_result', '').strip()
            if not result:
                messages.error(request, 'Un résultat de validation est requis.')
            else:
                release.status = Release.Status.FAILED
                release.validation_result = result
                release.validated_at = timezone.now()
                release.save()
                messages.success(request, 'Échec enregistré.')

        elif action == 'withdraw':
            release.status = Release.Status.WITHDRAWN
            release.save()
            messages.success(request, 'Version retirée.')

        elif action == 'edit':
            release.version_label = request.POST.get(
                'version_label', release.version_label,
            )
            release.summary = request.POST.get('summary', '')
            release.reference_url = request.POST.get('reference_url', '')
            release.asset_id = request.POST.get('asset') or None
            release.save()
            messages.success(request, 'Version mise à jour.')

        return redirect('releases:detail', pk=release.pk)

    return render(request, 'releases/detail.html', {'release': release})


@login_required
def release_create(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)

    if request.method == 'POST':
        release = Release.objects.create(
            project=project,
            asset_id=request.POST.get('asset') or None,
            version_label=request.POST.get('version_label', '').strip(),
            summary=request.POST.get('summary', ''),
            reference_url=request.POST.get('reference_url', ''),
        )
        messages.success(request, 'Version créée.')
        return redirect('releases:detail', pk=release.pk)

    return render(request, 'releases/create.html', {'project': project})
