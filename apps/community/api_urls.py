"""
API URL configuration for community app.
"""
from django.urls import path
from . import api_views

app_name = 'community'

urlpatterns = [
    path('prayer-requests/', api_views.PrayerRequestCreateAPIView.as_view(), name='prayer-requests'),
    path('testimonies/', api_views.TestimonyListAPIView.as_view(), name='testimonies'),
    path('testimonies/submit/', api_views.TestimonyCreateAPIView.as_view(), name='testimony-submit'),
]

