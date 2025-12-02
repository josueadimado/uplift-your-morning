from django.contrib import admin
from .models import Subscriber


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
