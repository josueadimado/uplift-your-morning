"""
URL configuration for resources app.
"""
from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.ResourceListView.as_view(), name='list'),
    # 40 Days Notes - must come before generic slug patterns
    path('40days/', views.FortyDaysNoteListView.as_view(), name='fortydays_list'),
    path('40days/<slug:slug>/', views.FortyDaysNoteDetailView.as_view(), name='fortydays_detail'),
    # Resource detail and download - must come after specific patterns
    path('<slug:slug>/', views.ResourceDetailView.as_view(), name='detail'),
    path('<slug:slug>/download/', views.download_resource, name='download'),
]

