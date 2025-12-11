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
        sms_subscribers = Subscriber.objects.filter(
            channel=Subscriber.CHANNEL_SMS,
            is_active=True,
            phone__isnull=False
        ).exclude(phone='')
        
        whatsapp_subscribers = Subscriber.objects.filter(
            channel=Subscriber.CHANNEL_WHATSAPP,
            is_active=True,
            receive_daily_devotion=True,
            phone__isnull=False
        ).exclude(phone='')
        
        total_email = email_subscribers.count()
        total_sms = sms_subscribers.count()
        total_whatsapp = whatsapp_subscribers.count()
        total_subscribers = total_email + total_sms + total_whatsapp
        
        self.stdout.write(f'\nFound {total_email} active email subscribers for daily devotions')
        self.stdout.write(f'Found {total_sms} active SMS subscribers for daily devotions')
        self.stdout.write(f'Found {total_whatsapp} active WhatsApp subscribers for daily devotions')
        self.stdout.write(f'Total: {total_subscribers} subscribers')
        
        if total_subscribers == 0:
            self.stdout.write(self.style.WARNING('No subscribers to send to. Exiting.'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN MODE - No messages will be sent'))
            self.stdout.write(f'Would send to {total_email} email subscribers')
            self.stdout.write(f'Would send to {total_sms} SMS subscribers')
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
        
        # Send SMS messages (via FastR API - short messages)
        sms_sent_count = 0
        sms_failed_count = 0
        
        if total_sms > 0:
            self.stdout.write(f'\nSending SMS to {total_sms} subscribers...')
            
            for subscriber in sms_subscribers:
                try:
                    self._send_sms(subscriber.phone, sms_message)
                    sms_sent_count += 1
                    if sms_sent_count % 10 == 0:
                        self.stdout.write(f'  Sent to {sms_sent_count} SMS subscribers...')
                except Exception as e:
                    sms_failed_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'  Failed to send SMS to {subscriber.phone}: {str(e)}'
                    ))
        
        # Send WhatsApp messages (via Twilio API)
        whatsapp_sent_count = 0
        whatsapp_failed_count = 0
        
        if total_whatsapp > 0:
            self.stdout.write(f'\nSending WhatsApp to {total_whatsapp} subscribers...')
            from apps.subscriptions.whatsapp import send_whatsapp_message
            for subscriber in whatsapp_subscribers:
                try:
                    send_whatsapp_message(subscriber.phone, sms_message)
                    whatsapp_sent_count += 1
                    if whatsapp_sent_count % 10 == 0:
                        self.stdout.write(f'  Sent to {whatsapp_sent_count} WhatsApp subscribers...')
                except Exception as e:
                    whatsapp_failed_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'  Failed to send WhatsApp to {subscriber.phone}: {str(e)}'
                    ))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✓ Email: {email_sent_count} sent, {email_failed_count} failed'))
        self.stdout.write(self.style.SUCCESS(f'✓ SMS: {sms_sent_count} sent, {sms_failed_count} failed'))
        self.stdout.write(self.style.SUCCESS(f'✓ WhatsApp: {whatsapp_sent_count} sent, {whatsapp_failed_count} failed'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total: {email_sent_count + sms_sent_count + whatsapp_sent_count} sent, {email_failed_count + sms_failed_count + whatsapp_failed_count} failed'))
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
        secret_key = config('FASTR_API_KEY', default='')
        public_key = config('FASTR_API_PUBLIC_KEY', default='DJbhctlognNbQuEhPMTB9A')
        api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org/api/client')
        sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
        
        if not secret_key:
            # SMS not configured, skip silently
            if settings.DEBUG:
                self.stdout.write(self.style.WARNING(f'SMS not configured. Would send SMS to {phone}'))
            return
        
        # Format phone number (Ghana format: 233XXXXXXXXX - no + sign, just digits)
        phone = phone.strip()
        # Remove + sign and any spaces/dashes
        phone = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Prepare request to FastR API
        # According to actual API documentation: Both keys go in request body
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Request body according to FastR API documentation
        data = {
            'api_key_public': public_key,
            'api_key_secret': secret_key,
            'message': message,
            'recipients': [phone],  # Array of phone numbers
            'sender_id': sender_id,
            'scheduled': False,
            'time_scheduled': None,
        }
        
        # Send SMS via FastR API
        try:
            response = requests.post(
                f'{api_base_url}/sms/send-sms',
                json=data,
                headers=headers,
                timeout=30
            )
            
            # Check response according to FastR API documentation
            if response.status_code == 201:  # FastR returns 201 Created for successful sends
                try:
                    response_data = response.json()
                    if response_data.get('status') == 'sent':
                        return True
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        raise Exception(f"API returned error: {error_msg}")
                except ValueError:
                    # Response might not be JSON, but status code is OK
                    return True
            elif response.status_code == 400:
                # Bad Request - invalid parameters
                try:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message', 'Invalid request parameters')
                except:
                    error_msg = 'Invalid request parameters'
                raise Exception(f"Bad Request: {error_msg}")
            elif response.status_code == 401:
                # Unauthorized - invalid API key
                try:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message', 'Authentication failed')
                except:
                    error_msg = 'Authentication failed'
                raise Exception(
                    f"Authentication failed (HTTP 401). "
                    f"Please verify your FASTR_API_KEY in .env file. "
                    f"Make sure you're using the SECRET key (9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8). "
                    f"API message: {error_msg}"
                )
            elif response.status_code == 403:
                raise Exception("Access forbidden. Please verify your API key has proper permissions")
            else:
                try:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message') or error_data.get('error', f'HTTP {response.status_code}')
                except ValueError:
                    error_msg = f'HTTP {response.status_code}'
                raise Exception(f"API error: {error_msg}")
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again later")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error. Please check your internet connection")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
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
            # WhatsApp gets the full email content (same as email)
            whatsapp_message = self._build_devotion_email(devotion)
            if notification.custom_message:
                whatsapp_message += f"\n\n{notification.custom_message}"
        else:
            email_subject = notification.title
            email_message = self._build_no_devotion_email()
            if notification.custom_message:
                email_message += f"\n\n{notification.custom_message}"
            sms_message = self._build_no_devotion_sms()
            if notification.custom_message:
                sms_message += f"\n\n{notification.custom_message[:100]}..."
            # WhatsApp gets the full email content (same as email)
            whatsapp_message = self._build_no_devotion_email()
            if notification.custom_message:
                whatsapp_message += f"\n\n{notification.custom_message}"
        
        # Get recipients
        email_subscribers = []
        sms_subscribers = []
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
        
        if notification.send_to_sms:
            sms_qs = Subscriber.objects.filter(
                channel=Subscriber.CHANNEL_SMS,
                is_active=True,
                phone__isnull=False
            ).exclude(phone='')
            if notification.only_daily_devotion_subscribers:
                sms_qs = sms_qs.filter(receive_daily_devotion=True)
            sms_subscribers = list(sms_qs)
        
        if notification.send_to_whatsapp:
            whatsapp_qs = Subscriber.objects.filter(
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=True,
                phone__isnull=False
            ).exclude(phone='')
            if notification.only_daily_devotion_subscribers:
                whatsapp_qs = whatsapp_qs.filter(receive_daily_devotion=True)
            whatsapp_subscribers = list(whatsapp_qs)
        
        total_recipients = len(email_subscribers) + len(sms_subscribers) + len(whatsapp_subscribers)
        self.stdout.write(f'  Recipients: {len(email_subscribers)} email, {len(sms_subscribers)} SMS, {len(whatsapp_subscribers)} WhatsApp')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('  DRY RUN: Would send notification'))
            return
        
        # Send emails
        email_sent = 0
        email_failed = 0
        email_errors = {}
        if email_subscribers:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Check email configuration first
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                self.stdout.write(self.style.WARNING(
                    '  ⚠️  Email backend is set to console. Emails will only print to console, not actually send.'
                ))
            
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                self.stdout.write(self.style.WARNING(
                    '  ⚠️  Email credentials not configured. Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env'
                ))
            
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
                    error_msg = str(e)
                    # Group errors by type
                    if error_msg not in email_errors:
                        email_errors[error_msg] = []
                    email_errors[error_msg].append(subscriber.email)
        
        # Display grouped email errors
        if email_errors:
            for error_msg, emails in email_errors.items():
                if len(emails) > 3:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ Email Error ({len(emails)} recipients): {error_msg}'
                    ))
                else:
                    for email in emails:
                        self.stdout.write(self.style.ERROR(
                            f'  ❌ Failed to send email to {email}: {error_msg}'
                        ))
        
        # Send SMS (via FastR API - short messages)
        sms_sent = 0
        sms_failed = 0
        sms_errors = {}
        if sms_subscribers:
            for subscriber in sms_subscribers:
                try:
                    self._send_sms(subscriber.phone, sms_message)
                    sms_sent += 1
                except Exception as e:
                    sms_failed += 1
                    error_msg = str(e)
                    if error_msg not in sms_errors:
                        sms_errors[error_msg] = []
                    sms_errors[error_msg].append(subscriber.phone)
        
        # Send WhatsApp (via Twilio API - full email content)
        whatsapp_sent = 0
        whatsapp_failed = 0
        whatsapp_errors = {}
        if whatsapp_subscribers:
            from apps.subscriptions.whatsapp import send_whatsapp_message
            for subscriber in whatsapp_subscribers:
                try:
                    # WhatsApp gets the full devotion email content
                    send_whatsapp_message(subscriber.phone, whatsapp_message)
                    whatsapp_sent += 1
                except Exception as e:
                    whatsapp_failed += 1
                    error_msg = str(e)
                    if error_msg not in whatsapp_errors:
                        whatsapp_errors[error_msg] = []
                    whatsapp_errors[error_msg].append(subscriber.phone)
        
        # Display grouped SMS errors
        if sms_errors:
            for error_msg, phones in sms_errors.items():
                if len(phones) > 3:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ SMS Error ({len(phones)} recipients): {error_msg}'
                    ))
                else:
                    for phone in phones:
                        self.stdout.write(self.style.ERROR(
                            f'  ❌ Failed to send SMS to {phone}: {error_msg}'
                        ))
        
        # Display grouped WhatsApp errors
        if whatsapp_errors:
            for error_msg, phones in whatsapp_errors.items():
                if len(phones) > 3:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ WhatsApp Error ({len(phones)} recipients): {error_msg}'
                    ))
                else:
                    for phone in phones:
                        self.stdout.write(self.style.ERROR(
                            f'  ❌ Failed to send WhatsApp to {phone}: {error_msg}'
                        ))
        
        # Update notification statistics
        notification.email_sent_count = email_sent
        notification.email_failed_count = email_failed
        notification.sms_sent_count = sms_sent
        notification.sms_failed_count = sms_failed
        notification.whatsapp_sent_count = whatsapp_sent
        notification.whatsapp_failed_count = whatsapp_failed
        notification.mark_as_sent()
        notification.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Sent: {email_sent} email, {sms_sent} SMS, {whatsapp_sent} WhatsApp | '
            f'Failed: {email_failed} email, {sms_failed} SMS, {whatsapp_failed} WhatsApp'
        ))
