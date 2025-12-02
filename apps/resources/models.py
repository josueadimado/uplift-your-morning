"""
Models for the resources library (PDFs, audio, videos, etc.).
"""
from django.db import models
from django.utils.text import slugify
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
