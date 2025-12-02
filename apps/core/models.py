"""
Core models for the UPLIFT Afrika platform.
This app contains base models and utilities used across the project.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at timestamps.
    All other models in the project will inherit from this to automatically
    track when records are created and updated.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
