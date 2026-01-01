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
    # Devotion Series AJAX
    path('devotions/series/create/', admin_views.DevotionSeriesCreateAjaxView.as_view(), name='devotions_series_create_ajax'),
    
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
    
    # Resource Categories
    path('resource-categories/', admin_views.ResourceCategoryListView.as_view(), name='resource_categories_list'),
    path('resource-categories/create/', admin_views.ResourceCategoryCreateView.as_view(), name='resource_categories_create'),
    path('resource-categories/<int:pk>/edit/', admin_views.ResourceCategoryUpdateView.as_view(), name='resource_categories_edit'),
    path('resource-categories/<int:pk>/delete/', admin_views.ResourceCategoryDeleteView.as_view(), name='resource_categories_delete'),
    
    # Prayer Requests
    path('prayers/', admin_views.PrayerRequestListView.as_view(), name='prayers_list'),
    path('prayers/<int:pk>/mark-prayed/', admin_views.PrayerRequestMarkPrayedView.as_view(), name='prayers_mark_prayed'),
    path('prayers/<int:pk>/delete/', admin_views.PrayerRequestDeleteView.as_view(), name='prayers_delete'),
    path('prayers/export/csv/', admin_views.PrayerRequestExportCSVView.as_view(), name='prayers_export_csv'),
    path('prayers/export/excel/', admin_views.PrayerRequestExportExcelView.as_view(), name='prayers_export_excel'),
    path('prayers/export/pdf/', admin_views.PrayerRequestExportPDFView.as_view(), name='prayers_export_pdf'),
    path('prayers/export/cards/', admin_views.PrayerRequestExportCardsView.as_view(), name='prayers_export_cards'),
    
    # Donations
    path('donations/', admin_views.DonationListView.as_view(), name='donations_list'),
    path('donations/<int:pk>/', admin_views.DonationDetailView.as_view(), name='donations_detail'),
    path('donations/<int:pk>/verify/', admin_views.DonationVerifyView.as_view(), name='donations_verify'),
    
    # Pledges
    path('pledges/', admin_views.PledgeListView.as_view(), name='pledges_list'),
    path('pledges/<int:pk>/', admin_views.PledgeDetailView.as_view(), name='pledges_detail'),
    path('pledges/<int:pk>/update-status/', admin_views.PledgeUpdateStatusView.as_view(), name='pledges_update_status'),
    path('pledges/<int:pk>/delete/', admin_views.PledgeDeleteView.as_view(), name='pledges_delete'),
    path('pledges/export/csv/', admin_views.PledgeExportCSVView.as_view(), name='pledges_export_csv'),
    path('pledges/export/excel/', admin_views.PledgeExportExcelView.as_view(), name='pledges_export_excel'),
    path('pledges/find-duplicates/', admin_views.PledgeFindDuplicatesView.as_view(), name='pledges_find_duplicates'),
    path('pledges/remove-duplicates/', admin_views.PledgeRemoveDuplicatesView.as_view(), name='pledges_remove_duplicates'),
    path('pledges/convert-to-usd/', admin_views.PledgeConvertToUSDView.as_view(), name='pledges_convert_to_usd'),
    
    # Testimonies
    path('testimonies/', admin_views.TestimonyListView.as_view(), name='testimonies_list'),
    path('testimonies/<int:pk>/', admin_views.TestimonyDetailView.as_view(), name='testimonies_detail'),
    path('testimonies/<int:pk>/approve/', admin_views.TestimonyApproveView.as_view(), name='testimonies_approve'),
    path('testimonies/<int:pk>/delete/', admin_views.TestimonyDeleteView.as_view(), name='testimonies_delete'),
    path('testimonies/export/csv/', admin_views.TestimonyExportCSVView.as_view(), name='testimonies_export_csv'),
    path('testimonies/export/excel/', admin_views.TestimonyExportExcelView.as_view(), name='testimonies_export_excel'),
    path('testimonies/export/pdf/', admin_views.TestimonyExportPDFView.as_view(), name='testimonies_export_pdf'),
    
    # 40 Days Configuration
    path('fortydays/', admin_views.FortyDaysConfigListView.as_view(), name='fortydays_list'),
    path('fortydays/create/', admin_views.FortyDaysConfigCreateView.as_view(), name='fortydays_create'),
    path('fortydays/<int:pk>/edit/', admin_views.FortyDaysConfigUpdateView.as_view(), name='fortydays_edit'),
    path('fortydays/<int:pk>/delete/', admin_views.FortyDaysConfigDeleteView.as_view(), name='fortydays_delete'),
    
    # 40 Days Notes
    path('fortydays/notes/', admin_views.FortyDaysNoteListView.as_view(), name='fortydays_notes_list'),
    path('fortydays/notes/create/', admin_views.FortyDaysNoteCreateView.as_view(), name='fortydays_notes_create'),
    path('fortydays/notes/<int:pk>/edit/', admin_views.FortyDaysNoteUpdateView.as_view(), name='fortydays_notes_edit'),
    path('fortydays/notes/<int:pk>/delete/', admin_views.FortyDaysNoteDeleteView.as_view(), name='fortydays_notes_delete'),
    
    # 40 Days Note Categories
    path('fortydays/note-categories/', admin_views.FortyDaysNoteCategoryListView.as_view(), name='fortydays_note_categories_list'),
    path('fortydays/note-categories/create/', admin_views.FortyDaysNoteCategoryCreateView.as_view(), name='fortydays_note_categories_create'),
    path('fortydays/note-categories/<int:pk>/edit/', admin_views.FortyDaysNoteCategoryUpdateView.as_view(), name='fortydays_note_categories_edit'),
    path('fortydays/note-categories/<int:pk>/delete/', admin_views.FortyDaysNoteCategoryDeleteView.as_view(), name='fortydays_note_categories_delete'),
    
    # Site Settings
    path('sitesettings/edit/', admin_views.SiteSettingsUpdateView.as_view(), name='sitesettings_edit'),
    
    # Counseling Bookings
    path('counseling/', admin_views.CounselingBookingListView.as_view(), name='counseling_list'),
    path('counseling/<int:pk>/', admin_views.CounselingBookingDetailView.as_view(), name='counseling_detail'),
    path('counseling/<int:pk>/approve/', admin_views.CounselingBookingApproveView.as_view(), name='counseling_approve'),
    path('counseling/<int:pk>/reject/', admin_views.CounselingBookingRejectView.as_view(), name='counseling_reject'),
    
    # Subscribers
    path('subscribers/', admin_views.SubscriberListView.as_view(), name='subscribers_list'),
    path('subscribers/<int:pk>/activate/', admin_views.SubscriberActivateView.as_view(), name='subscribers_activate'),
    path('subscribers/<int:pk>/deactivate/', admin_views.SubscriberDeactivateView.as_view(), name='subscribers_deactivate'),
    path('subscribers/<int:pk>/delete/', admin_views.SubscriberDeleteView.as_view(), name='subscribers_delete'),
    
    # Notifications
    path('notifications/', admin_views.NotificationScheduleListView.as_view(), name='notifications_list'),
    path('notifications/create/', admin_views.NotificationScheduleCreateView.as_view(), name='notifications_create'),
    path('notifications/<int:pk>/', admin_views.NotificationScheduleDetailView.as_view(), name='notifications_detail'),
    path('notifications/<int:pk>/pause/', admin_views.NotificationPauseView.as_view(), name='notifications_pause'),
    path('notifications/<int:pk>/resume/', admin_views.NotificationResumeView.as_view(), name='notifications_resume'),
    path('notifications/<int:pk>/send-now/', admin_views.NotificationSendNowView.as_view(), name='notifications_send_now'),
    path('notifications/<int:pk>/delete/', admin_views.NotificationDeleteView.as_view(), name='notifications_delete'),
]

