"""
Models for managing email and WhatsApp subscriptions.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class Subscriber(TimeStampedModel):
    """
    Stores subscribers who want to receive daily devotions via email or WhatsApp.
    """
    CHANNEL_EMAIL = "email"
    CHANNEL_WHATSAPP = "whatsapp"

    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
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

    def __str__(self):
        if self.channel == self.CHANNEL_EMAIL:
            return self.email or "Email subscriber"
        return self.phone or "WhatsApp subscriber"
