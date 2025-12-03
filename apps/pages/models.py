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
