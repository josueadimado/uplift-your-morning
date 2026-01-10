"""
Views for community features (prayer requests and testimonies).
"""
import logging
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django_countries import countries
from .models import PrayerRequest, Testimony
from .notifications import send_prayer_request_notification, send_testimony_notification

logger = logging.getLogger(__name__)


class PrayerRequestCreateView(CreateView):
    """
    View for submitting prayer requests.
    """
    model = PrayerRequest
    template_name = 'community/prayer_request_form.html'
    fields = ['name', 'email', 'request', 'is_public']
    success_url = '/community/prayer-request/'

    def form_valid(self, form):
        """
        Save the prayer request, send notification, and show success message.
        """
        response = super().form_valid(form)
        # Send email notification to admin
        try:
            send_prayer_request_notification(self.object)
            logger.info(f"Prayer request notification sent successfully for ID: {self.object.id}")
        except Exception as e:
            # Don't break the submission if notification fails, but log the error
            logger.error(
                f"Failed to send prayer request notification for ID: {self.object.id}",
                exc_info=True
            )
        messages.success(
            self.request,
            'Thank you for sharing your prayer request. We will be praying for you!'
        )
        return response


class TestimonyListView(ListView):
    """
    Display a list of approved testimonies.
    """
    model = Testimony
    template_name = 'community/testimonies.html'
    context_object_name = 'testimonies'
    paginate_by = 10

    def get_queryset(self):
        """
        Get only approved and public testimonies (respect user preference).
        """
        return Testimony.objects.filter(
            is_approved=True,
            is_public=True
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured testimonies separately
        context['featured_testimonies'] = Testimony.objects.filter(
            is_approved=True,
            is_public=True,
            featured=True
        )[:5]
        return context


class TestimonyCreateView(CreateView):
    """
    View for submitting testimonies.
    """
    model = Testimony
    template_name = 'community/testimony_form.html'
    fields = ['name', 'country', 'testimony', 'is_public']
    success_url = '/community/testimonies/'

    def get_context_data(self, **kwargs):
        """
        Add full list of countries for the country dropdown.
        """
        context = super().get_context_data(**kwargs)
        context['countries'] = countries
        return context

    def form_valid(self, form):
        """
        Save the testimony, send notification, and show success message.
        """
        response = super().form_valid(form)
        # Send email notification to admin
        try:
            send_testimony_notification(self.object)
            logger.info(f"Testimony notification sent successfully for ID: {self.object.id}")
        except Exception as e:
            # Don't break the submission if notification fails, but log the error
            logger.error(
                f"Failed to send testimony notification for ID: {self.object.id}",
                exc_info=True
            )
        
        # Customize success message based on public preference
        if self.object.is_public:
            messages.success(
                self.request,
                'Thank you for sharing your testimony! Your willingness to make it public will encourage others. It will be reviewed and published soon.'
            )
        else:
            messages.success(
                self.request,
                'Thank you for sharing your testimony! It will be reviewed and kept private as requested.'
            )
        return response