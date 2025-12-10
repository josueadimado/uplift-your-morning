"""
Views for email and WhatsApp subscriptions.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Subscriber


class SubscribeView(TemplateView):
    """
    View for subscription page with email and WhatsApp subscription forms.
    """
    template_name = 'subscriptions/subscribe.html'

    def post(self, request, *args, **kwargs):
        """
        Handle subscription form submission.
        """
        channel = request.POST.get('channel')
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        receive_daily = request.POST.get('receive_daily_devotion') == 'on'
        receive_special = request.POST.get('receive_special_programs') == 'on'

        if channel == Subscriber.CHANNEL_EMAIL:
            if not email:
                messages.error(request, 'Please provide your email address.')
                return redirect('subscriptions:subscribe')
            
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('subscriptions:subscribe')
            
            # Normalize email (lowercase)
            email = email.lower()
            
            # Check if already subscribed (active)
            existing_subscriber = Subscriber.objects.filter(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL,
                is_active=True
            ).first()
            
            if existing_subscriber:
                messages.warning(request, 'This email address is already subscribed. If you want to update your preferences, please contact us or unsubscribe first.')
                return redirect('subscriptions:subscribe')
            
            # Check if exists but inactive (reactivate)
            inactive_subscriber = Subscriber.objects.filter(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL,
                is_active=False
            ).first()
            
            if inactive_subscriber:
                # Reactivate and update preferences
                inactive_subscriber.is_active = True
                inactive_subscriber.receive_daily_devotion = receive_daily
                inactive_subscriber.receive_special_programs = receive_special
                inactive_subscriber.save()
                messages.success(request, 'Your subscription has been reactivated! You will receive daily devotions via email.')
            else:
                # Create new subscriber
                Subscriber.objects.create(
                    email=email,
                    channel=Subscriber.CHANNEL_EMAIL,
                    receive_daily_devotion=receive_daily,
                    receive_special_programs=receive_special,
                    is_active=True
                )
                messages.success(request, 'Thank you for subscribing! You will receive daily devotions via email.')

        elif channel == Subscriber.CHANNEL_WHATSAPP:
            if not phone:
                messages.error(request, 'Please provide your phone number.')
                return redirect('subscriptions:subscribe')
            
            # Normalize phone number (remove spaces and common separators)
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Validate that phone number includes country code (must start with +)
            if not phone.startswith('+'):
                messages.error(request, 'Please include your country code starting with + (e.g., +233 for Ghana, +1 for USA).')
                return redirect('subscriptions:subscribe')
            
            # Validate minimum length (country code + at least 7 digits)
            if len(phone) < 8:  # +1 (country code) + 7 digits minimum
                messages.error(request, 'Please enter a valid phone number with country code.')
                return redirect('subscriptions:subscribe')
            
            # Check if already subscribed (active)
            existing_subscriber = Subscriber.objects.filter(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=True
            ).first()
            
            if existing_subscriber:
                messages.warning(request, 'This phone number is already subscribed. If you want to update your preferences, please contact us or unsubscribe first.')
                return redirect('subscriptions:subscribe')
            
            # Check if exists but inactive (reactivate)
            inactive_subscriber = Subscriber.objects.filter(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=False
            ).first()
            
            if inactive_subscriber:
                # Reactivate and update preferences
                inactive_subscriber.is_active = True
                inactive_subscriber.receive_daily_devotion = receive_daily
                inactive_subscriber.receive_special_programs = receive_special
                inactive_subscriber.save()
                messages.success(request, 'Your subscription has been reactivated! You will receive daily devotions via WhatsApp.')
            else:
                # Create new subscriber
                Subscriber.objects.create(
                    phone=phone,
                    channel=Subscriber.CHANNEL_WHATSAPP,
                    receive_daily_devotion=receive_daily,
                    receive_special_programs=receive_special,
                    is_active=True
                )
                messages.success(request, 'Thank you for subscribing! You will receive daily devotions via WhatsApp.')

        return redirect('subscriptions:subscribe')


def unsubscribe(request):
    """
    Handle unsubscribe requests.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        if email:
            subscriber = Subscriber.objects.filter(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL
            ).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.save()
                messages.success(request, 'You have been unsubscribed from email notifications.')
            else:
                messages.error(request, 'Email address not found in our subscription list.')
        
        elif phone:
            subscriber = Subscriber.objects.filter(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP
            ).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.save()
                messages.success(request, 'You have been unsubscribed from WhatsApp notifications.')
            else:
                messages.error(request, 'Phone number not found in our subscription list.')
        else:
            messages.error(request, 'Please provide your email or phone number.')
    
    return render(request, 'subscriptions/unsubscribe.html')
