"""
URL configuration for uplift_afrika project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.pages import views as pages_views

urlpatterns = [
    # Custom Admin Login/Logout (must come before Django admin to override it)
    path('admin/login/', pages_views.AdminLoginView.as_view(), name='admin_login'),
    path('admin/logout/', pages_views.AdminLogoutView.as_view(), name='admin_logout'),
    # Django Admin
    path('admin/', admin.site.urls),
    # Custom Admin Management (for staff users)
    path('manage/', include('apps.pages.admin_urls', namespace='manage')),
    # App URLs
    path('', include('apps.pages.urls', namespace='pages')),
    path('devotions/', include('apps.devotions.urls', namespace='devotions')),
    path('resources/', include('apps.resources.urls', namespace='resources')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('community/', include('apps.community.urls', namespace='community')),
    path('subscriptions/', include('apps.subscriptions.urls', namespace='subscriptions')),
    # API URLs
    path('api/', include('apps.api.urls', namespace='api')),
]

# Serve media files in development
# Skip during management commands to avoid file scanning
import sys
IS_MANAGEMENT_CMD = len(sys.argv) > 1 and sys.argv[1] not in ['runserver', 'collectstatic', 'shell_plus']
if settings.DEBUG and not IS_MANAGEMENT_CMD:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
