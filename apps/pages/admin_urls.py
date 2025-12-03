"""
URL configuration for custom admin management views.
"""
from django.urls import path
from . import admin_views

app_name = 'manage'

urlpatterns = [
    # Devotions
    path('devotions/', admin_views.DevotionListView.as_view(), name='devotions_list'),
    path('devotions/create/', admin_views.DevotionCreateView.as_view(), name='devotions_create'),
    path('devotions/<int:pk>/edit/', admin_views.DevotionUpdateView.as_view(), name='devotions_edit'),
    path('devotions/<int:pk>/delete/', admin_views.DevotionDeleteView.as_view(), name='devotions_delete'),
    
    # Events
    path('events/', admin_views.EventListView.as_view(), name='events_list'),
    path('events/create/', admin_views.EventCreateView.as_view(), name='events_create'),
    path('events/<int:pk>/edit/', admin_views.EventUpdateView.as_view(), name='events_edit'),
    path('events/<int:pk>/delete/', admin_views.EventDeleteView.as_view(), name='events_delete'),
    
    # Resources
    path('resources/', admin_views.ResourceListView.as_view(), name='resources_list'),
    path('resources/create/', admin_views.ResourceCreateView.as_view(), name='resources_create'),
    path('resources/<int:pk>/edit/', admin_views.ResourceUpdateView.as_view(), name='resources_edit'),
    path('resources/<int:pk>/delete/', admin_views.ResourceDeleteView.as_view(), name='resources_delete'),
    
    # Prayer Requests
    path('prayers/', admin_views.PrayerRequestListView.as_view(), name='prayers_list'),
    path('prayers/<int:pk>/mark-prayed/', admin_views.PrayerRequestMarkPrayedView.as_view(), name='prayers_mark_prayed'),
    path('prayers/<int:pk>/delete/', admin_views.PrayerRequestDeleteView.as_view(), name='prayers_delete'),
    
    # Donations
    path('donations/', admin_views.DonationListView.as_view(), name='donations_list'),
    path('donations/<int:pk>/', admin_views.DonationDetailView.as_view(), name='donations_detail'),
    path('donations/<int:pk>/verify/', admin_views.DonationVerifyView.as_view(), name='donations_verify'),
    
    # Testimonies
    path('testimonies/', admin_views.TestimonyListView.as_view(), name='testimonies_list'),
    path('testimonies/<int:pk>/approve/', admin_views.TestimonyApproveView.as_view(), name='testimonies_approve'),
    path('testimonies/<int:pk>/delete/', admin_views.TestimonyDeleteView.as_view(), name='testimonies_delete'),
    
    # 40 Days Configuration
    path('fortydays/', admin_views.FortyDaysConfigListView.as_view(), name='fortydays_list'),
    path('fortydays/create/', admin_views.FortyDaysConfigCreateView.as_view(), name='fortydays_create'),
    path('fortydays/<int:pk>/edit/', admin_views.FortyDaysConfigUpdateView.as_view(), name='fortydays_edit'),
    path('fortydays/<int:pk>/delete/', admin_views.FortyDaysConfigDeleteView.as_view(), name='fortydays_delete'),
    
    # Site Settings
    path('sitesettings/edit/', admin_views.SiteSettingsUpdateView.as_view(), name='sitesettings_edit'),
]

