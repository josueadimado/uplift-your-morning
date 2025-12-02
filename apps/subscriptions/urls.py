"""
URL configuration for subscriptions app.
"""
from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
]

