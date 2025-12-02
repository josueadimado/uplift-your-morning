"""
URL configuration for community app.
"""
from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('prayer-request/', views.PrayerRequestCreateView.as_view(), name='prayer-request'),
    path('testimonies/', views.TestimonyListView.as_view(), name='testimonies'),
    path('testimonies/submit/', views.TestimonyCreateView.as_view(), name='testimony-submit'),
]

