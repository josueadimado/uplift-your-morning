"""
Management command to send daily devotions to subscribers.
Run this daily (e.g., via cron job) to send today's devotion to all active subscribers.

Usage:
    python manage.py send_daily_devotions
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date
from apps.subscriptions.models import Subscriber, ScheduledNotification
from apps.devotions.models import Devotion
from decouple import config
import requests
from django.utils import timezone


class Command(BaseCommand):
    help = 'Send today\'s daily devotion to all active subscribers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test run without actually sending emails',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send even if no devotion is published for today',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write('=' * 60)
        self.stdout.write('Daily Devotion Sender (Email & WhatsApp)')
        self.stdout.write('=' * 60)
        
        # First, check for scheduled notifications that are due
        self._process_scheduled_notifications(dry_run)
        
        # Then, process regular daily devotions (if no scheduled notifications override)
        # Get today's devotion
        today = date.today()
        try:
            devotion = Devotion.objects.filter(
                is_published=True,
                publish_date=today
            ).first()
            
            if not devotion:
                if force:
                    self.stdout.write(self.style.WARNING(
                        f'No devotion found for {today}. Using --force, will send to subscribers anyway.'
                    ))
                    devotion = None
                else:
                    self.stdout.write(self.style.WARNING(
                        f'No published devotion found for {today}. Exiting.'
                    ))
                    return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching devotion: {str(e)}'))
            return
        
        # Get active email subscribers who want daily devotions
        email_subscribers = Subscriber.objects.filter(
            channel=Subscriber.CHANNEL_EMAIL,
            is_active=True,
            receive_daily_devotion=True,
            email__isnull=False
        ).exclude(email='')
        
        # Get active WhatsApp subscribers who want daily devotions
        whatsapp_subscribers = Subscriber.objects.filter(
            channel=Subscriber.CHANNEL_WHATSAPP,
            is_active=True,
            receive_daily_devotion=True,
            phone__isnull=False
        ).exclude(phone='')
        
        total_email = email_subscribers.count()
        total_whatsapp = whatsapp_subscribers.count()
        total_subscribers = total_email + total_whatsapp
        
        self.stdout.write(f'\nFound {total_email} active email subscribers for daily devotions')
        self.stdout.write(f'Found {total_whatsapp} active WhatsApp subscribers for daily devotions')
        self.stdout.write(f'Total: {total_subscribers} subscribers')
        
        if total_subscribers == 0:
            self.stdout.write(self.style.WARNING('No subscribers to send to. Exiting.'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN MODE - No messages will be sent'))
            self.stdout.write(f'Would send to {total_email} email subscribers')
            self.stdout.write(f'Would send to {total_whatsapp} WhatsApp subscribers')
            if devotion:
                self.stdout.write(f'Devotion: {devotion.title}')
            return
        
        # Prepare email content
        if devotion:
            email_subject = f'Daily Devotion - {devotion.title}'
            email_message = self._build_devotion_email(devotion)
            sms_message = self._build_devotion_sms(devotion)
        else:
            email_subject = 'Daily Devotion - Uplift Your Morning'
            email_message = self._build_no_devotion_email()
            sms_message = self._build_no_devotion_sms()
        
        # Send emails
        email_sent_count = 0
        email_failed_count = 0
        
        if total_email > 0:
            self.stdout.write(f'\nSending emails to {total_email} subscribers...')
            
            for subscriber in email_subscribers:
                try:
                    send_mail(
                        email_subject,
                        email_message,
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
                        [subscriber.email],
                        fail_silently=False,
                    )
                    email_sent_count += 1
                    if email_sent_count % 10 == 0:
                        self.stdout.write(f'  Sent to {email_sent_count} email subscribers...')
                except Exception as e:
                    email_failed_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'  Failed to send to {subscriber.email}: {str(e)}'
                    ))
        
        # Send WhatsApp/SMS messages
        sms_sent_count = 0
        sms_failed_count = 0
        
        if total_whatsapp > 0:
            self.stdout.write(f'\nSending WhatsApp/SMS to {total_whatsapp} subscribers...')
            
            for subscriber in whatsapp_subscribers:
                try:
                    self._send_sms(subscriber.phone, sms_message)
                    sms_sent_count += 1
                    if sms_sent_count % 10 == 0:
                        self.stdout.write(f'  Sent to {sms_sent_count} WhatsApp subscribers...')
                except Exception as e:
                    sms_failed_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'  Failed to send to {subscriber.phone}: {str(e)}'
                    ))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✓ Email: {email_sent_count} sent, {email_failed_count} failed'))
        self.stdout.write(self.style.SUCCESS(f'✓ WhatsApp/SMS: {sms_sent_count} sent, {sms_failed_count} failed'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total: {email_sent_count + sms_sent_count} sent, {email_failed_count + sms_failed_count} failed'))
        self.stdout.write('=' * 60)
    
    def _build_devotion_email(self, devotion):
        """Build the email message for a devotion."""
        site_url = getattr(settings, 'SITE_URL', 'https://upliftyourmorning.com')
        devotion_url = f"{site_url}/devotions/{devotion.id}/"
        
        # Build the devotion content
        content_parts = []
        
        if devotion.scripture_reference:
            content_parts.append(f"Scripture: {devotion.scripture_reference}")
            if devotion.passage_text:
                content_parts.append(f"\n{devotion.passage_text}")
        
        if devotion.body:
            content_parts.append(f"\n\n{devotion.body}")
        
        if devotion.reflection:
            content_parts.append(f"\n\nReflection:\n{devotion.reflection}")
        
        if devotion.prayer:
            content_parts.append(f"\n\nPrayer:\n{devotion.prayer}")
        
        if devotion.action_point:
            content_parts.append(f"\n\nAction Point:\n{devotion.action_point}")
        
        devotion_content = "\n".join(content_parts)
        
        message = f"""
Good Morning!

Here's today's daily devotion from Uplift Your Morning:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{devotion.title}

{devotion_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read the full devotion online: {devotion_url}

Have a blessed day!

---
Uplift Your Morning
Start Your Day Right. Uplift Your Morning.

To unsubscribe, visit: {site_url}/subscriptions/unsubscribe/
"""
        return message.strip()
    
    def _build_no_devotion_email(self):
        """Build email message when no devotion is available."""
        site_url = getattr(settings, 'SITE_URL', 'https://upliftyourmorning.com')
        
        message = f"""
Good Morning!

Thank you for subscribing to Uplift Your Morning daily devotions.

We don't have a devotion published for today, but we wanted to let you know we're thinking of you!

Visit our website for previous devotions and resources: {site_url}/devotions/

Have a blessed day!

---
Uplift Your Morning
Start Your Day Right. Uplift Your Morning.

To unsubscribe, visit: {site_url}/subscriptions/unsubscribe/
"""
        return message.strip()
    
    def _build_devotion_sms(self, devotion):
        """Build SMS/WhatsApp message for a devotion."""
        site_url = getattr(settings, 'SITE_URL', 'https://upliftyourmorning.com')
        devotion_url = f"{site_url}/devotions/{devotion.id}/"
        
        # Build a concise SMS message (SMS has character limits)
        message_parts = [f"Daily Devotion: {devotion.title}"]
        
        if devotion.scripture_reference:
            message_parts.append(f"Scripture: {devotion.scripture_reference}")
        
        if devotion.body:
            # Truncate body to fit SMS (max ~150 chars for body)
            body_text = devotion.body[:150] + "..." if len(devotion.body) > 150 else devotion.body
            message_parts.append(f"\n{body_text}")
        
        message_parts.append(f"\nRead more: {devotion_url}")
        message_parts.append("\nUplift Your Morning")
        
        return "\n".join(message_parts)
    
    def _build_no_devotion_sms(self):
        """Build SMS message when no devotion is available."""
        site_url = getattr(settings, 'SITE_URL', 'https://upliftyourmorning.com')
        
        message = (
            "Good Morning! No devotion for today, but visit us: "
            f"{site_url}/devotions/ - Uplift Your Morning"
        )
        return message
    
    def _send_sms(self, phone, message):
        """Send SMS via FastR API."""
        api_key = config('FASTR_API_KEY', default='')
        api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org/api/client')
        sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
        
        if not api_key:
            # SMS not configured, skip silently
            if settings.DEBUG:
                self.stdout.write(self.style.WARNING(f'SMS not configured. Would send SMS to {phone}'))
            return
        
        # Format phone number (ensure it starts with +)
        phone = phone.strip()
        if not phone.startswith('+'):
            phone = '+' + phone.lstrip(' +0')
        
        # Prepare request to FastR API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'to': phone,
            'message': message,
            'sender_id': sender_id,
        }
        
        # Send SMS via FastR API
        try:
            response = requests.post(
                f'{api_base_url}/sms/send',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                response_data = response.json()
                if response_data.get('status') == 'success':
                    return True
                else:
                    error_msg = response_data.get('message', 'Unknown error')
                    raise Exception(f"SMS API error: {error_msg}")
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('message', f'HTTP {response.status_code}')
                raise Exception(f"SMS sending failed: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"SMS sending failed (network error): {str(e)}")
    
    def _process_scheduled_notifications(self, dry_run=False):
        """Process scheduled notifications that are due to be sent."""
        now = timezone.now()
        
        # Get all scheduled notifications that are due and not paused
        due_notifications = ScheduledNotification.objects.filter(
            status=ScheduledNotification.STATUS_SCHEDULED,
            is_paused=False,
            scheduled_date__lte=now.date()
        )
        
        # Filter by time (check if scheduled time has passed today)
        notifications_to_send = []
        for notification in due_notifications:
            scheduled_datetime = notification.scheduled_datetime
            if now >= scheduled_datetime:
                notifications_to_send.append(notification)
        
        if not notifications_to_send:
            self.stdout.write('\nNo scheduled notifications due to be sent.')
            return
        
        self.stdout.write(f'\nFound {len(notifications_to_send)} scheduled notification(s) due to be sent.')
        
        for notification in notifications_to_send:
            self.stdout.write(f'\nProcessing: {notification.title}')
            self._send_scheduled_notification(notification, dry_run)
    
    def _send_scheduled_notification(self, notification, dry_run=False):
        """Send a scheduled notification."""
        # Get the devotion to use
        devotion = notification.devotion
        if not devotion:
            from apps.devotions.models import Devotion
            devotion = Devotion.objects.filter(
                is_published=True,
                publish_date=notification.scheduled_date
            ).first()
        
        # IMPORTANT: Check if there's a fresh devotion for the scheduled date
        # If no devotion exists, skip sending (don't send placeholder)
        if not devotion:
            self.stdout.write(self.style.WARNING(
                f'  ⚠️  No published devotion found for {notification.scheduled_date}. Skipping notification.'
            ))
            # Update notification status to indicate it was skipped
            notification.status = ScheduledNotification.STATUS_CANCELLED
            notification.notes = (notification.notes or '') + f'\n[Skipped: No devotion found for {notification.scheduled_date}]'
            notification.save()
            return
        
        # Build messages
        if devotion:
            email_subject = f'{notification.title} - {devotion.title}'
            email_message = self._build_devotion_email(devotion)
            if notification.custom_message:
                email_message += f"\n\n{notification.custom_message}"
            sms_message = self._build_devotion_sms(devotion)
            if notification.custom_message:
                sms_message += f"\n\n{notification.custom_message[:100]}..."
        else:
            email_subject = notification.title
            email_message = self._build_no_devotion_email()
            if notification.custom_message:
                email_message += f"\n\n{notification.custom_message}"
            sms_message = self._build_no_devotion_sms()
            if notification.custom_message:
                sms_message += f"\n\n{notification.custom_message[:100]}..."
        
        # Get recipients
        email_subscribers = []
        whatsapp_subscribers = []
        
        if notification.send_to_email:
            email_qs = Subscriber.objects.filter(
                channel=Subscriber.CHANNEL_EMAIL,
                is_active=True,
                email__isnull=False
            ).exclude(email='')
            if notification.only_daily_devotion_subscribers:
                email_qs = email_qs.filter(receive_daily_devotion=True)
            email_subscribers = list(email_qs)
        
        if notification.send_to_whatsapp:
            whatsapp_qs = Subscriber.objects.filter(
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=True,
                phone__isnull=False
            ).exclude(phone='')
            if notification.only_daily_devotion_subscribers:
                whatsapp_qs = whatsapp_qs.filter(receive_daily_devotion=True)
            whatsapp_subscribers = list(whatsapp_qs)
        
        total_recipients = len(email_subscribers) + len(whatsapp_subscribers)
        self.stdout.write(f'  Recipients: {len(email_subscribers)} email, {len(whatsapp_subscribers)} WhatsApp')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('  DRY RUN: Would send notification'))
            return
        
        # Send emails
        email_sent = 0
        email_failed = 0
        if email_subscribers:
            from django.core.mail import send_mail
            from django.conf import settings
            for subscriber in email_subscribers:
                try:
                    send_mail(
                        email_subject,
                        email_message,
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
                        [subscriber.email],
                        fail_silently=False,
                    )
                    email_sent += 1
                except Exception as e:
                    email_failed += 1
                    self.stdout.write(self.style.ERROR(f'  Failed to send email to {subscriber.email}: {str(e)}'))
        
        # Send SMS
        sms_sent = 0
        sms_failed = 0
        if whatsapp_subscribers:
            for subscriber in whatsapp_subscribers:
                try:
                    self._send_sms(subscriber.phone, sms_message)
                    sms_sent += 1
                except Exception as e:
                    sms_failed += 1
                    self.stdout.write(self.style.ERROR(f'  Failed to send SMS to {subscriber.phone}: {str(e)}'))
        
        # Update notification
        notification.email_sent_count = email_sent
        notification.email_failed_count = email_failed
        notification.sms_sent_count = sms_sent
        notification.sms_failed_count = sms_failed
        notification.mark_as_sent()
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Sent: {email_sent} email, {sms_sent} SMS | Failed: {email_failed} email, {sms_failed} SMS'
        ))
