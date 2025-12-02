"""
Models for events and programs (conferences, Bible studies, etc.).
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Event(TimeStampedModel):
    """
    Represents an event or program (conference, Bible study, Youth Academy, etc.).
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    # Legacy single livestream URL (kept for backwards compatibility)
    livestream_url = models.URLField(blank=True)

    # New fields for richer event presentation
    poster_image = models.ImageField(
        upload_to='events/posters/',
        blank=True,
        null=True,
        help_text="Optional poster or flyer image for this event."
    )

    # Optional platform-specific live URLs
    youtube_url = models.URLField(
        blank=True,
        help_text="Optional YouTube live/stream URL for this event."
    )
    facebook_url = models.URLField(
        blank=True,
        help_text="Optional Facebook live/stream URL for this event."
    )
    zoom_url = models.URLField(
        blank=True,
        help_text="Optional Zoom meeting/webinar URL for this event."
    )
    registration_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['start_datetime']


class EventRegistration(TimeStampedModel):
    """
    Stores registrations for events.
    When someone registers for an event, their information is saved here.
    """
    event = models.ForeignKey(
        Event,
        related_name="registrations",
        on_delete=models.CASCADE
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    class Meta:
        ordering = ['-created_at']
