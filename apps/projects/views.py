from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Project


@login_required
def project_list(request):
    status = request.GET.get('status', '')
    projects = Project.objects.select_related().order_by('status', '-priority')

    if status:
        projects = projects.filter(status=status)

    # Annotate next action
    for project in projects:
        project.next_action = project.tasks.filter(
            is_next_action=True,
        ).first()

    return render(request, 'projects/list.html', {
        'projects': projects,
        'current_status': status,
        'status_choices': Project.Status.choices,
    })


@login_required
def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'tasks', 'decisions', 'resources', 'assets', 'releases',
        ),
        slug=slug,
    )
    project.next_action = project.tasks.filter(is_next_action=True).first()

    return render(request, 'projects/detail.html', {
        'project': project,
    })
