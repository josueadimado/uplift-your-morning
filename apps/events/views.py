"""
Views for events and programs.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
from .models import Event, EventRegistration


class EventListView(ListView):
    """
    Display a list of events.
    """
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        """
        Get events, optionally filtered by upcoming/past.
        """
        queryset = Event.objects.all()
        
        filter_type = self.request.GET.get('filter', 'upcoming')
        now = timezone.now()
        
        if filter_type == 'upcoming':
            queryset = queryset.filter(start_datetime__gte=now)
        elif filter_type == 'past':
            queryset = queryset.filter(start_datetime__lt=now)
        
        return queryset.order_by('start_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_type'] = self.request.GET.get('filter', 'upcoming')
        return context


class EventDetailView(DetailView):
    """
    Display a single event in detail with registration form.
    """
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        """
        Handle event registration form submission.
        """
        self.object = self.get_object()
        
        if not self.object.registration_open:
            messages.error(request, 'Registration for this event is currently closed.')
            return redirect('events:detail', slug=self.object.slug)
        
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        country = request.POST.get('country', '')
        notes = request.POST.get('notes', '')

        if full_name and email:
            # Check if already registered
            existing = EventRegistration.objects.filter(
                event=self.object,
                email=email
            ).first()
            
            if existing:
                messages.info(request, 'You are already registered for this event.')
            else:
                EventRegistration.objects.create(
                    event=self.object,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    country=country,
                    notes=notes
                )
                messages.success(request, 'Thank you for registering! We will contact you with more details.')
            
            return redirect('events:detail', slug=self.object.slug)
        else:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('events:detail', slug=self.object.slug)
