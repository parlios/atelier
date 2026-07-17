from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.projects.models import Project
from .models import Decision


@login_required
def decision_list(request):
    status = request.GET.get('status', '')
    decisions = Decision.objects.filter(
        archived_at__isnull=True,
    ).select_related('project')
    if status in Decision.Status.values:
        decisions = decisions.filter(status=status)
    return render(request, 'decisions/list.html', {
        'decisions': decisions,
        'current_status': status,
        'status_choices': Decision.Status.choices,
    })


@login_required
def decision_detail(request, pk):
    decision = get_object_or_404(
        Decision.objects.select_related('project', 'superseded_by'), pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'accept':
            choice = request.POST.get('choice', '').strip()
            consequences = request.POST.get('consequences', '').strip()
            if not choice or not consequences:
                messages.error(request, 'Le choix et les conséquences sont requis.')
            else:
                decision.status = Decision.Status.ACCEPTED
                decision.choice = choice
                decision.consequences = consequences
                decision.decided_at = timezone.now()
                decision.save()
                messages.success(request, 'Décision acceptée.')

        elif action == 'reject':
            decision.status = Decision.Status.REJECTED
            decision.decided_at = timezone.now()
            decision.save()
            messages.success(request, 'Décision rejetée.')

        elif action == 'supersede':
            new_choice = request.POST.get('new_choice', '').strip()
            consequences = request.POST.get('consequences', '').strip()
            if not new_choice or not consequences:
                messages.error(request, 'Le nouveau choix et ses conséquences sont requis.')
            else:
                new_decision = Decision.objects.create(
                    project=decision.project,
                    title=f'{decision.title} (révisée)',
                    context=decision.context,
                    question=decision.question,
                    choice=new_choice,
                    consequences=consequences,
                    status=Decision.Status.ACCEPTED,
                    decided_at=timezone.now(),
                )
                decision.status = Decision.Status.SUPERSEDED
                decision.superseded_by = new_decision
                decision.save()
                messages.success(request, 'Décision remplacée.')
                return redirect('decisions:detail', pk=new_decision.pk)

        elif action == 'edit':
            decision.title = request.POST.get('title', decision.title)
            decision.context = request.POST.get('context', '')
            decision.question = request.POST.get('question', '')
            decision.alternatives = request.POST.get('alternatives', '')
            decision.save()
            messages.success(request, 'Décision mise à jour.')

        return redirect('decisions:detail', pk=decision.pk)

    return render(request, 'decisions/detail.html', {'decision': decision})


@login_required
def decision_create(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)

    if request.method == 'POST':
        decision = Decision.objects.create(
            project=project,
            title=request.POST.get('title', '').strip(),
            context=request.POST.get('context', ''),
            question=request.POST.get('question', ''),
            alternatives=request.POST.get('alternatives', ''),
        )
        messages.success(request, 'Décision créée.')
        return redirect('decisions:detail', pk=decision.pk)

    return render(request, 'decisions/create.html', {'project': project})
