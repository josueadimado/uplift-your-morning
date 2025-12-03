from django.contrib import admin
from .models import ContactMessage, Donation, FortyDaysConfig


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'amount_ghs', 'status', 'paystack_reference', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'paystack_reference', 'note']
    readonly_fields = ['created_at', 'updated_at', 'raw_response']


@admin.register(FortyDaysConfig)
class FortyDaysConfigAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date']
    fieldsets = (
        ('Date Range', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Morning Session (5:00-5:30am Ghana time)', {
            'fields': ('morning_youtube_url', 'morning_facebook_url')
        }),
        ('Evening Session (6:00-7:00pm Ghana time)', {
            'fields': ('evening_youtube_url', 'evening_facebook_url')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
