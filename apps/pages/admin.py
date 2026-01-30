from django.contrib import admin
from django.utils import timezone
from .models import ContactMessage, Donation, FortyDaysConfig, SiteSettings, CounselingBooking, PageView, Question, CoordinatorApplication


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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False


@admin.register(FortyDaysConfig)
class FortyDaysConfigAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date']
    fieldsets = (
        ('Date Range', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Banner Image', {
            'fields': ('banner_image',)
        }),
        ('Morning Session (5:00-5:30am Ghana time)', {
            'fields': ('morning_youtube_url', 'morning_facebook_url')
        }),
        ('Evening Session (6:00-7:00pm Ghana time)', {
            'fields': ('evening_youtube_url', 'evening_facebook_url')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CounselingBooking)
class CounselingBookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'preferred_date', 'preferred_time', 'status', 'created_at']
    list_filter = ['status', 'preferred_date', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'topic', 'message']
    readonly_fields = ['created_at', 'updated_at', 'google_calendar_event_id', 'email_sent', 'sms_sent']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone', 'country')
        }),
        ('Booking Details', {
            'fields': ('preferred_date', 'preferred_time', 'duration_minutes', 'topic', 'message')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_date', 'approved_time', 'admin_notes')
        }),
        ('Integration', {
            'fields': ('google_calendar_event_id', 'email_sent', 'sms_sent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_bookings', 'reject_bookings']
    
    def approve_bookings(self, request, queryset):
        """Approve selected bookings."""
        count = 0
        for booking in queryset.filter(status=CounselingBooking.STATUS_PENDING):
            booking.status = CounselingBooking.STATUS_APPROVED
            if not booking.approved_date:
                booking.approved_date = booking.preferred_date
            if not booking.approved_time:
                booking.approved_time = booking.preferred_time
            booking.save()
            count += 1
        self.message_user(request, f'{count} booking(s) approved.')
    approve_bookings.short_description = "Approve selected bookings"
    
    def reject_bookings(self, request, queryset):
        """Reject selected bookings."""
        count = queryset.filter(status=CounselingBooking.STATUS_PENDING).update(status=CounselingBooking.STATUS_REJECTED)
        self.message_user(request, f'{count} booking(s) rejected.')
    reject_bookings.short_description = "Reject selected bookings"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'category', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['name', 'email', 'question', 'reply']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Submission', {
            'fields': ('category', 'name', 'email', 'question')
        }),
        ('Your Reply', {
            'fields': ('reply', 'replied_at', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if change and form.cleaned_data.get('reply') and not obj.replied_at:
            obj.replied_at = timezone.now()
        if change and form.cleaned_data.get('reply'):
            obj.status = Question.STATUS_ANSWERED
        super().save_model(request, obj, form, change)


@admin.register(CoordinatorApplication)
class CoordinatorApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'country', 'application_type', 'campus_or_role_display', 'status', 'created_at']
    list_filter = ['application_type', 'status', 'created_at']
    search_fields = [
        'name', 'email', 'phone', 'country',
        'campus_name', 'program_of_study', 'role_or_profession', 'organisation_name',
        'profile_message', 'additional_student_info', 'additional_professional_info',
    ]
    readonly_fields = ['created_at', 'updated_at']

    def campus_or_role_display(self, obj):
        if obj.application_type == CoordinatorApplication.TYPE_STUDENT:
            return obj.campus_name or obj.campus_or_profession or '—'
        return obj.role_or_profession or obj.organisation_name or obj.campus_or_profession or '—'
    campus_or_role_display.short_description = 'Campus / Role'

    fieldsets = (
        ('Type & Contact', {
            'fields': ('application_type', 'name', 'country', 'email', 'phone')
        }),
        ('Student Movement', {
            'fields': ('campus_name', 'program_of_study', 'year_of_study', 'additional_student_info'),
            'classes': ('collapse',)
        }),
        ('Professional', {
            'fields': ('role_or_profession', 'organisation_name', 'years_experience', 'linkedin_url', 'additional_professional_info'),
            'classes': ('collapse',)
        }),
        ('Motivation', {
            'fields': ('profile_message',)
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Legacy', {
            'fields': ('campus_or_profession',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['page_name', 'path', 'ip_address', 'created_at']
    list_filter = ['created_at', 'path']
    search_fields = ['path', 'page_name', 'ip_address']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # Prevent manual creation - views are tracked automatically
        return False
