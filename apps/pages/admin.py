from django.contrib import admin
from .models import ContactMessage, Donation


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
