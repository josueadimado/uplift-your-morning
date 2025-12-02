"""
URL configuration for resources app.
"""
from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.ResourceListView.as_view(), name='list'),
    path('<slug:slug>/', views.ResourceDetailView.as_view(), name='detail'),
    path('<slug:slug>/download/', views.download_resource, name='download'),
]

