"""
Views for email and WhatsApp subscriptions.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
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
            
            # Check if already subscribed
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL,
                defaults={
                    'receive_daily_devotion': receive_daily,
                    'receive_special_programs': receive_special,
                    'is_active': True
                }
            )
            
            if not created:
                # Update existing subscriber
                subscriber.is_active = True
                subscriber.receive_daily_devotion = receive_daily
                subscriber.receive_special_programs = receive_special
                subscriber.save()
                messages.info(request, 'Your subscription preferences have been updated.')
            else:
                messages.success(request, 'Thank you for subscribing! You will receive daily devotions via email.')

        elif channel == Subscriber.CHANNEL_WHATSAPP:
            if not phone:
                messages.error(request, 'Please provide your phone number.')
                return redirect('subscriptions:subscribe')
            
            # Check if already subscribed
            subscriber, created = Subscriber.objects.get_or_create(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP,
                defaults={
                    'receive_daily_devotion': receive_daily,
                    'receive_special_programs': receive_special,
                    'is_active': True
                }
            )
            
            if not created:
                # Update existing subscriber
                subscriber.is_active = True
                subscriber.receive_daily_devotion = receive_daily
                subscriber.receive_special_programs = receive_special
                subscriber.save()
                messages.info(request, 'Your subscription preferences have been updated.')
            else:
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
