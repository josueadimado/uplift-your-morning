"""
API URL configuration for devotions app.
"""
from django.urls import path
from . import api_views

app_name = 'devotions'

urlpatterns = [
    path('today/', api_views.TodayDevotionAPIView.as_view(), name='today'),
    path('', api_views.DevotionListAPIView.as_view(), name='list'),
    path('<slug:slug>/', api_views.DevotionDetailAPIView.as_view(), name='detail'),
    path('series/', api_views.DevotionSeriesListAPIView.as_view(), name='series-list'),
    path('series/<slug:slug>/', api_views.DevotionSeriesDetailAPIView.as_view(), name='series-detail'),
]

