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
from apps.subscriptions.models import Subscriber
from apps.devotions.models import Devotion


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
        self.stdout.write('Daily Devotion Email Sender')
        self.stdout.write('=' * 60)
        
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
        
        total_subscribers = email_subscribers.count()
        self.stdout.write(f'\nFound {total_subscribers} active email subscribers for daily devotions')
        
        if total_subscribers == 0:
            self.stdout.write(self.style.WARNING('No subscribers to send to. Exiting.'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN MODE - No emails will be sent'))
            self.stdout.write(f'Would send to {total_subscribers} subscribers')
            if devotion:
                self.stdout.write(f'Devotion: {devotion.title}')
            return
        
        # Prepare email content
        if devotion:
            subject = f'Daily Devotion - {devotion.title}'
            message = self._build_devotion_email(devotion)
        else:
            subject = 'Daily Devotion - Uplift Your Morning'
            message = self._build_no_devotion_email()
        
        # Send emails
        sent_count = 0
        failed_count = 0
        
        self.stdout.write(f'\nSending emails...')
        
        for subscriber in email_subscribers:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
                    [subscriber.email],
                    fail_silently=False,
                )
                sent_count += 1
                if sent_count % 10 == 0:
                    self.stdout.write(f'  Sent to {sent_count} subscribers...')
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(
                    f'  Failed to send to {subscriber.email}: {str(e)}'
                ))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully sent: {sent_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {failed_count}'))
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

