"""
Views for community features (prayer requests and testimonies).
"""
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django_countries import countries
from .models import PrayerRequest, Testimony


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
        Save the prayer request and show success message.
        """
        messages.success(
            self.request,
            'Thank you for sharing your prayer request. We will be praying for you!'
        )
        return super().form_valid(form)


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
        Get only approved testimonies.
        """
        return Testimony.objects.filter(is_approved=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured testimonies separately
        context['featured_testimonies'] = Testimony.objects.filter(
            is_approved=True,
            featured=True
        )[:5]
        return context


class TestimonyCreateView(CreateView):
    """
    View for submitting testimonies.
    """
    model = Testimony
    template_name = 'community/testimony_form.html'
    fields = ['name', 'country', 'testimony']
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
        Save the testimony (needs admin approval before being displayed).
        """
        messages.success(
            self.request,
            'Thank you for sharing your testimony! It will be reviewed and published soon.'
        )
        return super().form_valid(form)
