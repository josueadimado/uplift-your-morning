"""
Models for static pages like Home, About, Contact, etc.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    """
    Model to store contact form submissions.
    (Kept for historical records, even though the page is now used for donations.)
    """
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class Donation(TimeStampedModel):
    """
    Records donations made via the website.
    We create a record when initializing the Paystack transaction
    and update it after verification on callback.
    """

    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Successful'),
        (STATUS_FAILED, 'Failed'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    amount_ghs = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=200, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    note = models.CharField(max_length=255, blank=True)
    raw_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - GHS {self.amount_ghs} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class SiteSettings(TimeStampedModel):
    """
    Site-wide settings that should only have one instance.
    Stores general configuration like Zoom links used across all programs.
    """
    zoom_link = models.URLField(
        blank=True,
        help_text="Zoom meeting link used for all programs (Uplift Your Morning, Access Hour, Edify, 40 Days)"
    )
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion - just clear the fields instead
        self.zoom_link = ''
        self.save()
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"


class CounselingBooking(TimeStampedModel):
    """
    Model for counseling session bookings.
    Requires admin approval before confirmation.
    """
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # User information
    full_name = models.CharField(max_length=200)
    # Email is optional – some users may only want to share a phone number
    email = models.EmailField(blank=True, null=True)
    # Store phone in international format (e.g. +233201234567)
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=100, blank=True)
    
    # Booking details
    preferred_date = models.DateField(help_text="Preferred date for counseling session")
    preferred_time = models.TimeField(help_text="Preferred time for counseling session")
    duration_minutes = models.IntegerField(default=30, help_text="Session duration in minutes (fixed at 30 minutes)")
    topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Brief topic or reason for counseling"
    )
    message = models.TextField(
        blank=True,
        help_text="Additional message or details"
    )
    
    # Status and admin fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    approved_date = models.DateField(null=True, blank=True, help_text="Admin-approved date")
    approved_time = models.TimeField(null=True, blank=True, help_text="Admin-approved time")
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    
    # Google Calendar integration
    google_calendar_event_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Google Calendar event ID after creation"
    )
    
    # Notification tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Counseling Booking"
        verbose_name_plural = "Counseling Bookings"
    
    def __str__(self):
        return f"{self.full_name} - {self.preferred_date} ({self.status})"


class FortyDaysConfig(TimeStampedModel):
    """
    Configuration for the annual "40 Days of Prayer, Planning & Planting" event.
    Stores the date range and live streaming URLs for morning and evening sessions.
    Only one active configuration should exist at a time.
    """
    start_date = models.DateField(
        help_text="Start date of the 40 Days event (e.g., November 10, 2025)"
    )
    end_date = models.DateField(
        help_text="End date of the 40 Days event (e.g., December 19, 2025)"
    )
    
    # Banner/Flyer image for the 40 Days section
    banner_image = models.ImageField(
        upload_to='fortydays/banners/',
        blank=True,
        null=True,
        help_text="Banner/flyer image for the 40 Days section on the homepage"
    )
    
    # Morning session (5:00-5:30am Ghana time)
    morning_youtube_url = models.URLField(
        blank=True,
        help_text="YouTube live URL for morning sessions (5:00-5:30am Ghana time)"
    )
    morning_facebook_url = models.URLField(
        blank=True,
        help_text="Facebook live URL for morning sessions (5:00-5:30am Ghana time)"
    )
    
    # Evening session (6:00-7:00pm Ghana time)
    evening_youtube_url = models.URLField(
        blank=True,
        help_text="YouTube live URL for evening sessions (6:00-7:00pm Ghana time)"
    )
    evening_facebook_url = models.URLField(
        blank=True,
        help_text="Facebook live URL for evening sessions (6:00-7:00pm Ghana time)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Set to False to disable this configuration (useful for past years)"
    )
    
    def __str__(self):
        return f"40 Days {self.start_date.year} ({self.start_date} to {self.end_date})"
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "40 Days Configuration"
        verbose_name_plural = "40 Days Configurations"


class PageView(TimeStampedModel):
    """
    Tracks page views for analytics purposes.
    Records each visit to a page on the website.
    """
    path = models.CharField(
        max_length=500,
        help_text="The URL path that was visited (e.g., /devotions/, /events/)"
    )
    page_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Human-readable page name (e.g., 'Home', 'Devotions List')"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the visitor"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent string"
    )
    referer = models.URLField(
        blank=True,
        help_text="The page the user came from (if available)"
    )
    
    def __str__(self):
        return f"{self.page_name or self.path} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['path']),
        ]
