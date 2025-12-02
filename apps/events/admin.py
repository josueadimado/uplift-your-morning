from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for managing events and programs.
    """
    list_display = ['title', 'start_datetime', 'end_datetime', 'location', 'registration_open', 'is_online']
    list_filter = ['registration_open', 'is_online', 'start_datetime']
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_datetime'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing event registrations.
    """
    list_display = ['full_name', 'email', 'event', 'phone', 'country', 'created_at']
    list_filter = ['event', 'country', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'event__title']
    readonly_fields = ['created_at', 'updated_at']
