"""
Models for devotions and devotion series.
This handles daily devotions and special programs like "40 Days of Prayer".
"""
from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class DevotionSeries(TimeStampedModel):
    """
    Represents a series of devotions, like "40 Days of Prayer".
    Multiple devotions can belong to one series.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # Optional banner image for this series (e.g., 40 Days of Prayer hero)
    banner_image = models.ImageField(
        upload_to="devotions/series_banners/",
        blank=True,
        null=True,
        help_text="Banner image for this series (used on series pages and filtered lists)",
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Devotion(TimeStampedModel):
    """
    Represents a single daily devotion.
    Each devotion has scripture, content, reflection, prayer, and action points.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    series = models.ForeignKey(
        DevotionSeries,
        related_name="devotions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    theme = models.CharField(max_length=200, blank=True, help_text="Monthly theme (e.g., 'Theme for April: Memorials')")
    topic = models.CharField(max_length=250, blank=True, help_text="Daily topic (e.g., 'Blessings with a Charge')")
    scripture_reference = models.CharField(max_length=255, blank=True, help_text="Foundation Text (NKJV)")
    passage_text = models.TextField(blank=True, help_text="Scripture passage text")
    body = models.TextField(help_text="Devotional Message - main content")
    quote = models.TextField(blank=True, help_text="Inspirational quote")
    reflection = models.TextField(blank=True, help_text="Reflection questions or points")
    prayer = models.TextField(blank=True, help_text="Today's Prayer")
    action_point = models.TextField(blank=True, help_text="Action point or practical application")
    publish_date = models.DateField(db_index=True)
    is_published = models.BooleanField(default=False)
    image = models.ImageField(upload_to="devotions/images/", blank=True, null=True, help_text="Featured image for this devotion")
    audio_file = models.FileField(upload_to="devotions/audio/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="devotions/pdf/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-publish_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
