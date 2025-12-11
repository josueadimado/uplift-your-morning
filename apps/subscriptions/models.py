"""
Models for managing email and WhatsApp subscriptions.
"""
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.devotions.models import Devotion


class Subscriber(TimeStampedModel):
    """
    Stores subscribers who want to receive daily devotions via email, SMS, or WhatsApp.
    """
    CHANNEL_EMAIL = "email"
    CHANNEL_SMS = "sms"
    CHANNEL_WHATSAPP = "whatsapp"

    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_SMS, "SMS"),
        (CHANNEL_WHATSAPP, "WhatsApp"),
    ]

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    is_active = models.BooleanField(default=True)
    receive_daily_devotion = models.BooleanField(default=True)
    receive_special_programs = models.BooleanField(default=True)

    class Meta:
        unique_together = ("email", "phone", "channel")

    def clean(self):
        """
        Normalize email and phone before saving.
        """
        from django.core.exceptions import ValidationError
        
        if self.channel == self.CHANNEL_EMAIL:
            if not self.email:
                raise ValidationError({'email': 'Email is required for email subscriptions.'})
            # Normalize email (lowercase)
            self.email = self.email.lower().strip()
        
        if self.channel in [self.CHANNEL_SMS, self.CHANNEL_WHATSAPP]:
            if not self.phone:
                channel_name = "SMS" if self.channel == self.CHANNEL_SMS else "WhatsApp"
                raise ValidationError({'phone': f'Phone number is required for {channel_name} subscriptions.'})
            # Normalize phone number (remove spaces and common separators, but keep +)
            self.phone = self.phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').strip()
            # Validate that phone number includes country code (must start with +)
            if not self.phone.startswith('+'):
                raise ValidationError({'phone': 'Phone number must include country code starting with + (e.g., +233 for Ghana, +1 for USA).'})
            # Validate minimum length (country code + at least 7 digits)
            if len(self.phone) < 8:  # +1 (country code) + 7 digits minimum
                raise ValidationError({'phone': 'Please enter a valid phone number with country code.'})

    def save(self, *args, **kwargs):
        """
        Override save to run clean() and normalize data.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.channel == self.CHANNEL_EMAIL:
            return self.email or "Email subscriber"
        elif self.channel == self.CHANNEL_SMS:
            return self.phone or "SMS subscriber"
        else:  # CHANNEL_WHATSAPP
            return self.phone or "WhatsApp subscriber"


class ScheduledNotification(TimeStampedModel):
    """
    Stores scheduled notifications to be sent to subscribers.
    Allows scheduling, previewing, and pausing notifications.
    """
    STATUS_SCHEDULED = 'scheduled'
    STATUS_PAUSED = 'paused'
    STATUS_SENT = 'sent'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_SENT, 'Sent'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # Notification details
    title = models.CharField(max_length=200, help_text="Title/Subject of the notification")
    devotion = models.ForeignKey(
        Devotion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: Link to a specific devotion. If not set, will use today's devotion."
    )
    custom_message = models.TextField(
        blank=True,
        help_text="Optional: Custom message to include. If devotion is set, this will be added to the devotion content."
    )
    
    # Scheduling
    scheduled_date = models.DateField(help_text="Date to send the notification")
    scheduled_time = models.TimeField(help_text="Time to send the notification")
    is_paused = models.BooleanField(default=False, help_text="Pause this notification from being sent")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was actually sent")
    
    # Recipients
    send_to_email = models.BooleanField(default=True, help_text="Send to email subscribers")
    send_to_sms = models.BooleanField(default=True, help_text="Send to SMS subscribers")
    send_to_whatsapp = models.BooleanField(default=True, help_text="Send to WhatsApp subscribers")
    only_daily_devotion_subscribers = models.BooleanField(
        default=True,
        help_text="Only send to subscribers who opted in for daily devotions"
    )
    
    # Statistics (populated after sending)
    email_sent_count = models.IntegerField(default=0, help_text="Number of emails sent")
    email_failed_count = models.IntegerField(default=0, help_text="Number of emails that failed")
    sms_sent_count = models.IntegerField(default=0, help_text="Number of SMS sent")
    sms_failed_count = models.IntegerField(default=0, help_text="Number of SMS that failed")
    whatsapp_sent_count = models.IntegerField(default=0, help_text="Number of WhatsApp messages sent")
    whatsapp_failed_count = models.IntegerField(default=0, help_text="Number of WhatsApp messages that failed")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes about this notification")
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
        verbose_name = "Scheduled Notification"
        verbose_name_plural = "Scheduled Notifications"
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date} at {self.scheduled_time}"
    
    @property
    def scheduled_datetime(self):
        """Return the scheduled date and time as a datetime object."""
        from django.utils import timezone
        from datetime import datetime
        return timezone.make_aware(
            datetime.combine(self.scheduled_date, self.scheduled_time)
        )
    
    @property
    def is_due(self):
        """Check if the notification is due to be sent."""
        if self.is_paused or self.status != self.STATUS_SCHEDULED:
            return False
        return timezone.now() >= self.scheduled_datetime
    
    def pause(self):
        """Pause this notification."""
        self.is_paused = True
        self.status = self.STATUS_PAUSED
        self.save()
    
    def resume(self):
        """Resume this notification."""
        self.is_paused = False
        self.status = self.STATUS_SCHEDULED
        self.save()
    
    def mark_as_sent(self):
        """Mark this notification as sent."""
        self.status = self.STATUS_SENT
        self.sent_at = timezone.now()
        self.save()
