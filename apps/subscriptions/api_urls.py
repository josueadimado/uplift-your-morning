"""
API URL configuration for subscriptions app.
"""
from django.urls import path
from . import api_views

app_name = 'subscriptions'

urlpatterns = [
    path('subscribe/', api_views.SubscribeAPIView.as_view(), name='subscribe'),
    path('unsubscribe/', api_views.UnsubscribeAPIView.as_view(), name='unsubscribe'),
]

