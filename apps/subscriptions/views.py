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
        Supports multiple channels in one submission.
        """
        channels = request.POST.getlist('channels')  # Get all selected channels
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        receive_daily = request.POST.get('receive_daily_devotion') == 'on'
        receive_special = request.POST.get('receive_special_programs') == 'on'
        
        # Validate that at least one channel is selected
        if not channels:
            messages.error(request, 'Please select at least one notification channel.')
            return redirect('subscriptions:subscribe')
        
        success_messages = []
        error_messages = []
        
        # Process each selected channel
        for channel in channels:
            if channel == Subscriber.CHANNEL_EMAIL:
                if not email:
                    error_messages.append('Email address is required for email subscription.')
                    continue
                
                # Validate email format
                try:
                    validate_email(email)
                except ValidationError:
                    error_messages.append('Please enter a valid email address.')
                    continue
                
                # Normalize email (lowercase)
                email_normalized = email.lower()
                
                # Check if already subscribed (active)
                existing_subscriber = Subscriber.objects.filter(
                    email=email_normalized,
                    channel=Subscriber.CHANNEL_EMAIL,
                    is_active=True
                ).first()
                
                if existing_subscriber:
                    error_messages.append('This email address is already subscribed. If you want to update your preferences, please contact us or unsubscribe first.')
                    continue
                
                # Check if exists but inactive (reactivate)
                inactive_subscriber = Subscriber.objects.filter(
                    email=email_normalized,
                    channel=Subscriber.CHANNEL_EMAIL,
                    is_active=False
                ).first()
                
                if inactive_subscriber:
                    # Reactivate and update preferences
                    inactive_subscriber.is_active = True
                    inactive_subscriber.receive_daily_devotion = receive_daily
                    inactive_subscriber.receive_special_programs = receive_special
                    inactive_subscriber.save()
                    success_messages.append('Email subscription reactivated!')
                else:
                    # Create new subscriber
                    Subscriber.objects.create(
                        email=email_normalized,
                        channel=Subscriber.CHANNEL_EMAIL,
                        receive_daily_devotion=receive_daily,
                        receive_special_programs=receive_special,
                        is_active=True
                    )
                    success_messages.append('Email subscription successful!')

            elif channel == Subscriber.CHANNEL_SMS:
                if not phone:
                    error_messages.append('Phone number is required for SMS subscription.')
                    continue
                
                # Normalize phone number (remove spaces and common separators, but preserve +)
                phone_normalized = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                
                # Validate that phone number includes country code (must start with +)
                if not phone_normalized.startswith('+'):
                    error_messages.append('Please include your country code starting with + for SMS subscription (e.g., +233 for Ghana, +1 for USA).')
                    continue
                
                # Validate minimum length (country code + at least 7 digits)
                if len(phone_normalized) < 8:  # +1 (country code) + 7 digits minimum
                    error_messages.append('Please enter a valid phone number with country code for SMS subscription.')
                    continue
                
                # Check if already subscribed (active)
                existing_subscriber = Subscriber.objects.filter(
                    phone=phone_normalized,
                    channel=Subscriber.CHANNEL_SMS,
                    is_active=True
                ).first()
                
                if existing_subscriber:
                    error_messages.append('This phone number is already subscribed for SMS. If you want to update your preferences, please contact us or unsubscribe first.')
                    continue
                
                # Check if exists but inactive (reactivate)
                inactive_subscriber = Subscriber.objects.filter(
                    phone=phone_normalized,
                    channel=Subscriber.CHANNEL_SMS,
                    is_active=False
                ).first()
                
                if inactive_subscriber:
                    # Reactivate and update preferences
                    inactive_subscriber.is_active = True
                    inactive_subscriber.receive_daily_devotion = receive_daily
                    inactive_subscriber.receive_special_programs = receive_special
                    inactive_subscriber.save()
                    success_messages.append('SMS subscription reactivated!')
                else:
                    # Create new subscriber
                    Subscriber.objects.create(
                        phone=phone_normalized,
                        channel=Subscriber.CHANNEL_SMS,
                        receive_daily_devotion=receive_daily,
                        receive_special_programs=receive_special,
                        is_active=True
                    )
                    success_messages.append('SMS subscription successful!')

            elif channel == Subscriber.CHANNEL_WHATSAPP:
                if not phone:
                    error_messages.append('Phone number is required for WhatsApp subscription.')
                    continue
                
                # Normalize phone number (remove spaces and common separators, but preserve +)
                phone_normalized = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                
                # Validate that phone number includes country code (must start with +)
                if not phone_normalized.startswith('+'):
                    error_messages.append('Please include your country code starting with + for WhatsApp subscription (e.g., +233 for Ghana, +1 for USA).')
                    continue
                
                # Validate minimum length (country code + at least 7 digits)
                if len(phone_normalized) < 8:  # +1 (country code) + 7 digits minimum
                    error_messages.append('Please enter a valid phone number with country code for WhatsApp subscription.')
                    continue
                
                # Check if already subscribed (active)
                existing_subscriber = Subscriber.objects.filter(
                    phone=phone_normalized,
                    channel=Subscriber.CHANNEL_WHATSAPP,
                    is_active=True
                ).first()
                
                if existing_subscriber:
                    error_messages.append('This phone number is already subscribed for WhatsApp. If you want to update your preferences, please contact us or unsubscribe first.')
                    continue
                
                # Check if exists but inactive (reactivate)
                inactive_subscriber = Subscriber.objects.filter(
                    phone=phone_normalized,
                    channel=Subscriber.CHANNEL_WHATSAPP,
                    is_active=False
                ).first()
                
                if inactive_subscriber:
                    # Reactivate and update preferences
                    inactive_subscriber.is_active = True
                    inactive_subscriber.receive_daily_devotion = receive_daily
                    inactive_subscriber.receive_special_programs = receive_special
                    inactive_subscriber.save()
                    success_messages.append('WhatsApp subscription reactivated!')
                else:
                    # Create new subscriber
                    Subscriber.objects.create(
                        phone=phone_normalized,
                        channel=Subscriber.CHANNEL_WHATSAPP,
                        receive_daily_devotion=receive_daily,
                        receive_special_programs=receive_special,
                        is_active=True
                    )
                    success_messages.append('WhatsApp subscription successful!')
        
        # Display success and error messages
        for msg in success_messages:
            messages.success(request, msg)
        
        for msg in error_messages:
            messages.error(request, msg)
        
        # If there were any successes, show a summary
        if success_messages and not error_messages:
            channel_names = []
            if Subscriber.CHANNEL_EMAIL in channels:
                channel_names.append('Email')
            if Subscriber.CHANNEL_SMS in channels:
                channel_names.append('SMS')
            if Subscriber.CHANNEL_WHATSAPP in channels:
                channel_names.append('WhatsApp')
            
            if len(channel_names) > 1:
                messages.success(request, f'Thank you for subscribing! You will receive daily devotions via {", ".join(channel_names)}.')
        
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
            # Try to find subscriber by phone (could be SMS or WhatsApp)
            subscriber = Subscriber.objects.filter(
                phone=phone
            ).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.save()
                channel_name = "SMS" if subscriber.channel == Subscriber.CHANNEL_SMS else "WhatsApp"
                messages.success(request, f'You have been unsubscribed from {channel_name} notifications.')
            else:
                messages.error(request, 'Phone number not found in our subscription list.')
        else:
            messages.error(request, 'Please provide your email or phone number.')
    
    return render(request, 'subscriptions/unsubscribe.html')
