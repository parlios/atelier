from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.activity.models import Activity
from apps.decisions.models import Decision
from apps.inbox.models import InboxItem
from apps.projects.models import Project
from apps.registry.models import Asset
from apps.releases.models import Release
from apps.resources.models import Resource
from apps.tasks.models import Task


def home(request):
    return render(request, 'core/home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('core:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('core:home')


@login_required
def dashboard(request):
    active_projects = list(Project.objects.filter(
        status=Project.Status.ACTIVE,
        archived_at__isnull=True,
    ).prefetch_related('tasks').order_by('-priority', '-updated_at'))

    projects_without_next = []
    for project in active_projects:
        project.next_action = project.tasks.filter(
            is_next_action=True,
        ).first()
        if project.next_action is None:
            projects_without_next.append(project)

    unprocessed_count = InboxItem.objects.filter(
        status=InboxItem.Status.UNPROCESSED,
        archived_at__isnull=True,
    ).count()
    next_actions = Task.objects.filter(
        is_next_action=True,
        archived_at__isnull=True,
    ).select_related('project')[:8]
    priority_tasks = Task.objects.filter(
        priority=Task.Priority.HIGH,
        is_next_action=False,
        archived_at__isnull=True,
    ).exclude(
        status__in=[Task.Status.COMPLETED, Task.Status.CANCELED],
    ).select_related('project')[:6]
    blocked_tasks = Task.objects.filter(
        status=Task.Status.BLOCKED,
        archived_at__isnull=True,
    ).select_related('project')[:6]
    proposed_decisions = Decision.objects.filter(
        status=Decision.Status.PROPOSED,
        archived_at__isnull=True,
    ).select_related('project')[:5]
    recent_releases = Release.objects.filter(
        archived_at__isnull=True,
    ).select_related('project', 'asset')[:5]
    recent_activity = Activity.objects.select_related('project')[:10]
    projects_to_review = Project.objects.filter(
        review_due_on__lte=timezone.localdate(),
        archived_at__isnull=True,
    ).exclude(
        status__in=[Project.Status.COMPLETED, Project.Status.ABANDONED],
    )[:5]

    return render(request, 'core/dashboard.html', {
        'active_projects': active_projects,
        'projects_without_next': projects_without_next,
        'projects_to_review': projects_to_review,
        'next_actions': next_actions,
        'priority_tasks': priority_tasks,
        'blocked_tasks': blocked_tasks,
        'unprocessed_count': unprocessed_count,
        'proposed_decisions': proposed_decisions,
        'recent_releases': recent_releases,
        'recent_activity': recent_activity,
    })


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    results = {}

    if query:
        # Projects
        projects = Project.objects.filter(
            Q(name__icontains=query)
            | Q(problem_statement__icontains=query)
            | Q(expected_outcome__icontains=query)
            | Q(description__icontains=query),
        ).order_by('-updated_at')[:10]
        results['Projets'] = [
            {
                'title': p.name,
                'detail': p.get_status_display(),
                'url': f'/projects/{p.slug}/',
            }
            for p in projects
        ]

        # Tasks
        tasks = Task.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(result_summary__icontains=query),
        ).select_related('project').order_by('-updated_at')[:10]
        results['Tâches'] = [
            {
                'title': t.title,
                'detail': f'{t.get_status_display()} → {t.project.name}',
                'url': f'/tasks/{t.pk}/',
            }
            for t in tasks
        ]

        # Decisions
        decisions = Decision.objects.filter(
            Q(title__icontains=query)
            | Q(context__icontains=query)
            | Q(choice__icontains=query),
        ).select_related('project').order_by('-updated_at')[:10]
        results['Décisions'] = [
            {
                'title': d.title,
                'detail': f'{d.get_status_display()} → {d.project.name}',
                'url': f'/decisions/{d.pk}/',
            }
            for d in decisions
        ]

        # Resources
        resources = Resource.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query),
        ).select_related('project').order_by('-updated_at')[:10]
        results['Ressources'] = [
            {
                'title': r.title,
                'detail': f'{r.get_resource_type_display()}'
                + (f' → {r.project.name}' if r.project else ''),
                'url': f'/resources/{r.pk}/',
            }
            for r in resources
        ]

        # Assets
        assets = Asset.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query),
        ).select_related('owner_project').order_by('-updated_at')[:10]
        results['Actifs'] = [
            {
                'title': a.name,
                'detail': f'{a.get_asset_type_display()} ({a.get_status_display()})',
                'url': f'/registry/{a.pk}/',
            }
            for a in assets
        ]

        # Releases
        releases = Release.objects.filter(
            Q(version_label__icontains=query)
            | Q(summary__icontains=query),
        ).select_related('project').order_by('-updated_at')[:10]
        results['Versions'] = [
            {
                'title': f'{r.project.name} — {r.version_label}',
                'detail': r.get_status_display(),
                'url': f'/releases/{r.pk}/',
            }
            for r in releases
        ]

    return render(request, 'core/search.html', {
        'query': query,
        'results': results,
        'has_results': any(results.values()),
    })
