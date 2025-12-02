"""
API URL configuration.
This file routes all API endpoints.
"""
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Devotions API
    path('devotions/', include('apps.devotions.api_urls', namespace='devotions')),
    # Subscriptions API
    path('subscriptions/', include('apps.subscriptions.api_urls', namespace='subscriptions')),
    # Community API
    path('community/', include('apps.community.api_urls', namespace='community')),
]

