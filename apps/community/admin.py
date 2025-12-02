from django.contrib import admin
from .models import PrayerRequest, Testimony


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for managing prayer requests.
    """
    list_display = ['request', 'name', 'email', 'is_public', 'is_prayed_for', 'created_at']
    list_filter = ['is_public', 'is_prayed_for', 'created_at']
    search_fields = ['name', 'email', 'request']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_prayed_for']

    def mark_as_prayed_for(self, request, queryset):
        """Admin action to mark prayer requests as prayed for."""
        queryset.update(is_prayed_for=True)
    mark_as_prayed_for.short_description = "Mark selected prayer requests as prayed for"


@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
    """
    Admin interface for managing testimonies.
    """
    list_display = ['testimony', 'name', 'country', 'is_approved', 'featured', 'created_at']
    list_filter = ['is_approved', 'featured', 'country', 'created_at']
    search_fields = ['name', 'country', 'testimony']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_testimonies', 'feature_testimonies']

    def approve_testimonies(self, request, queryset):
        """Admin action to approve testimonies."""
        queryset.update(is_approved=True)
    approve_testimonies.short_description = "Approve selected testimonies"

    def feature_testimonies(self, request, queryset):
        """Admin action to feature testimonies."""
        queryset.update(featured=True)
    feature_testimonies.short_description = "Feature selected testimonies"
