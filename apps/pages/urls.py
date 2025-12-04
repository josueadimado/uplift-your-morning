"""
URL configuration for pages app.
"""
from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('donate/', views.DonationView.as_view(), name='donate'),
    path('donate/checkout/', views.DonationCheckoutView.as_view(), name='donate-checkout'),
    path('donate/thanks/', views.DonationThanksView.as_view(), name='donate-thanks'),
    path('counseling/', views.CounselingBookingView.as_view(), name='counseling_booking'),
]

