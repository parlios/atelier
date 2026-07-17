from django.urls import path

from . import views

app_name = 'inbox'

urlpatterns = [
    path('', views.inbox_list, name='list'),
    path('capture/', views.inbox_capture, name='capture'),
    path('<uuid:pk>/qualify/', views.inbox_qualify, name='qualify'),
]
