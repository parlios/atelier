from django.urls import path

from . import views

app_name = 'registry'

urlpatterns = [
    path('', views.asset_list, name='list'),
    path('create/', views.asset_create, name='create'),
    path('<uuid:pk>/', views.asset_detail, name='detail'),
]
