"""
URL configuration for devotions app.
"""
from django.urls import path
from . import views

app_name = 'devotions'

urlpatterns = [
    path('', views.DevotionListView.as_view(), name='list'),
    path('today/', views.TodayDevotionView.as_view(), name='today'),
    path('<slug:slug>/', views.DevotionDetailView.as_view(), name='detail'),
    path('series/<slug:slug>/', views.DevotionSeriesDetailView.as_view(), name='series-detail'),
]

