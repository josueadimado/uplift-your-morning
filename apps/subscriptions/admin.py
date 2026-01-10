from django.contrib import admin
from .models import Subscriber, ScheduledNotification


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """
    Admin interface for managing email and WhatsApp subscribers.
    """
    list_display = ['email', 'phone', 'channel', 'is_active', 'receive_daily_devotion', 'receive_special_programs', 'created_at']
    list_filter = ['channel', 'is_active', 'receive_daily_devotion', 'receive_special_programs', 'created_at']
    search_fields = ['email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['deactivate_subscribers', 'activate_subscribers']

    def deactivate_subscribers(self, request, queryset):
        """Admin action to deactivate subscribers."""
        queryset.update(is_active=False)
    deactivate_subscribers.short_description = "Deactivate selected subscribers"

    def activate_subscribers(self, request, queryset):
        """Admin action to activate subscribers."""
        queryset.update(is_active=True)
    activate_subscribers.short_description = "Activate selected subscribers"


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing scheduled notifications.
    """
    list_display = ['title', 'scheduled_date', 'scheduled_time', 'status', 'is_paused', 'send_to_email', 'send_to_sms', 'send_to_whatsapp', 'created_at']
    list_filter = ['status', 'is_paused', 'send_to_email', 'send_to_sms', 'send_to_whatsapp', 'scheduled_date', 'created_at']
    search_fields = ['title', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'email_sent_count', 'email_failed_count', 'sms_sent_count', 'sms_failed_count']
    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'devotion', 'custom_message', 'notes')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time', 'is_paused', 'status')
        }),
        ('Recipients', {
            'fields': ('send_to_email', 'send_to_sms', 'send_to_whatsapp', 'only_daily_devotion_subscribers')
        }),
        ('Statistics', {
            'fields': ('sent_at', 'email_sent_count', 'email_failed_count', 'sms_sent_count', 'sms_failed_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
