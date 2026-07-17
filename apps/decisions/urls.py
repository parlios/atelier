from django.urls import path

from . import views

app_name = 'decisions'

urlpatterns = [
    path('', views.decision_list, name='list'),
    path('create/<slug:project_slug>/', views.decision_create, name='create'),
    path('<uuid:pk>/', views.decision_detail, name='detail'),
]
