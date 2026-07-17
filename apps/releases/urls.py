from django.urls import path

from . import views

app_name = 'releases'

urlpatterns = [
    path('', views.release_list, name='list'),
    path('create/<slug:project_slug>/', views.release_create, name='create'),
    path('<uuid:pk>/', views.release_detail, name='detail'),
]
