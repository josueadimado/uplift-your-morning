"""
Models for community features (prayer requests and testimonies).
"""
from django.db import models
from apps.core.models import TimeStampedModel


class PrayerRequest(TimeStampedModel):
    """
    Stores prayer requests submitted by community members.
    Can be public (visible on website) or private (only for admin).
    """
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    request = models.TextField()
    is_public = models.BooleanField(default=False)
    is_prayed_for = models.BooleanField(default=False)

    def __str__(self):
        return self.request[:50]

    class Meta:
        ordering = ['-created_at']


class Testimony(TimeStampedModel):
    """
    Stores testimonies shared by community members.
    Testimonies must be approved by admin before being displayed publicly.
    """
    name = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=100, blank=True)
    testimony = models.TextField()
    is_approved = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    is_public = models.BooleanField(
        default=True,
        help_text="User's preference to make testimony public to encourage community members"
    )

    def __str__(self):
        return self.testimony[:50]

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Testimonies"
