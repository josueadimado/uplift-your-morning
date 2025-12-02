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
