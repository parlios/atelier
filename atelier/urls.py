from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('apps.core.urls')),
    path('projects/', include('apps.projects.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('inbox/', include('apps.inbox.urls')),
    path('decisions/', include('apps.decisions.urls')),
    path('resources/', include('apps.resources.urls')),
    path('registry/', include('apps.registry.urls')),
    path('releases/', include('apps.releases.urls')),
    path('admin/', admin.site.urls),
]
