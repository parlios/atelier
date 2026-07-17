from apps.inbox.models import InboxItem


def navigation_context(request):
    """Expose uniquement les données légères nécessaires au shell global."""
    if not request.user.is_authenticated:
        return {'navigation_inbox_count': 0}

    return {
        'navigation_inbox_count': InboxItem.objects.filter(
            status=InboxItem.Status.UNPROCESSED,
            archived_at__isnull=True,
        ).count(),
    }
