"""
Models for the resources library (PDFs, audio, videos, etc.).
"""
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import date
from apps.core.models import TimeStampedModel


class ResourceCategory(TimeStampedModel):
    """
    Categories for organizing resources (e.g., "Bible Studies", "Sermons", etc.).
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Resource(TimeStampedModel):
    """
    Represents a downloadable or viewable resource (PDF, audio, video, etc.).
    """
    TYPE_CHOICES = [
        ("pdf", "PDF Document"),
        ("audio", "Audio"),
        ("video", "Video"),
        ("image", "Image/Poster"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        ResourceCategory,
        related_name="resources",
        on_delete=models.CASCADE
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="pdf")
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/files/", blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)  # e.g. YouTube link
    is_featured = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class FortyDaysNoteCategory(TimeStampedModel):
    """
    Categories for organizing 40 Days notes/insights (e.g., "Prayer", "Planning", "Planting", etc.).
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order for displaying categories")

    class Meta:
        verbose_name = "40 Days Note Category"
        verbose_name_plural = "40 Days Note Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FortyDaysNote(TimeStampedModel):
    """
    Notes and key takeaways from 40 Days evening sessions.
    Each note contains insights shared by experts, organized by category.
    """
    title = models.CharField(max_length=200, help_text="Name/title of the insight or note")
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        FortyDaysNoteCategory,
        related_name="notes",
        on_delete=models.CASCADE,
        help_text="Category for organizing this note"
    )
    banner_image = models.ImageField(
        upload_to="fortydays/notes/banners/",
        help_text="Banner picture for this note"
    )
    content = models.TextField(help_text="Notes or key takeaways from the session")
    expert_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of the expert/speaker who shared this insight"
    )
    session_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of the evening session (optional)"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this note from public view"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this note on the main page"
    )
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "40 Days Note"
        verbose_name_plural = "40 Days Notes"
        ordering = ['-session_date', '-created_at']

    def __str__(self):
        return self.title

    def get_day_count(self):
        """
        Calculate the day count based on the session date.
        Uses the active FortyDaysConfig's start_date for the year of the session date.
        Returns empty string if session_date is not set or no matching config found.
        """
        if not self.session_date:
            return ""
        
        # Import here to avoid circular imports
        from apps.pages.models import FortyDaysConfig
        
        # Find the 40 Days configuration for the year of this note's session date
        # First try to find an active config for that year
        config = FortyDaysConfig.objects.filter(
            start_date__year=self.session_date.year,
            is_active=True
        ).first()
        
        # If no active config for that year, try any config for that year
        if not config:
            config = FortyDaysConfig.objects.filter(
                start_date__year=self.session_date.year
            ).order_by('-start_date').first()
        
        # If still no config found, return empty string
        if not config:
            return ""
        
        # Calculate the difference in days from the config's start date
        delta = self.session_date - config.start_date
        day_number = delta.days + 1  # +1 because Day 1 is the start date itself
        
        # Calculate total days in the 40 Days period
        total_days = (config.end_date - config.start_date).days + 1
        
        # Return day count if within the period
        if 1 <= day_number <= total_days:
            return f"Day {day_number}"
        else:
            # If outside the 40 Days period, still show the day number but indicate it's outside
            return f"Day {day_number} (outside 40 Days period)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
