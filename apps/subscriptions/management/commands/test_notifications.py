"""
Django management command to test sending notifications via Email, SMS, and WhatsApp.
Usage: 
    python manage.py test_notifications --email test@example.com
    python manage.py test_notifications --sms +22872039785
    python manage.py test_notifications --whatsapp +22872039785
    python manage.py test_notifications --all --email test@example.com --sms +22872039785 --whatsapp +22872039785
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from decouple import config
import requests


class Command(BaseCommand):
    help = 'Test sending notifications via Email, SMS, and WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--sms',
            type=str,
            help='Phone number to send test SMS to (e.g., +22872039785)',
        )
        parser.add_argument(
            '--whatsapp',
            type=str,
            help='Phone number to send test WhatsApp to (e.g., +22872039785)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Test all channels (requires --email, --sms, and --whatsapp)',
        )
        parser.add_argument(
            '--message',
            type=str,
            default='Test message from Uplift Your Morning notification system. This is a test to verify the channel is working correctly.',
            help='Custom message to send (optional)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        sms_phone = options.get('sms')
        whatsapp_phone = options.get('whatsapp')
        test_all = options.get('all')
        message = options.get('message')
        
        if not email and not sms_phone and not whatsapp_phone:
            self.stdout.write(self.style.ERROR(
                'Please specify at least one channel to test:\n'
                '  --email test@example.com\n'
                '  --sms +22872039785\n'
                '  --whatsapp +22872039785\n'
                '  --all --email test@example.com --sms +22872039785 --whatsapp +22872039785'
            ))
            return
        
        if test_all and (not email or not sms_phone or not whatsapp_phone):
            self.stdout.write(self.style.ERROR(
                'When using --all, you must provide --email, --sms, and --whatsapp'
            ))
            return
        
        self.stdout.write("=" * 70)
        self.stdout.write("Notification System Test")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        results = {
            'email': {'success': False, 'error': None},
            'sms': {'success': False, 'error': None},
            'whatsapp': {'success': False, 'error': None},
        }
        
        # Test Email
        if email:
            self.stdout.write("📧 Testing Email...")
            self.stdout.write(f"   To: {email}")
            try:
                result = self._test_email(email, message)
                results['email'] = result
                if result['success']:
                    self.stdout.write(self.style.SUCCESS("   ✅ Email sent successfully!"))
                else:
                    self.stdout.write(self.style.ERROR(f"   ❌ Email failed: {result['error']}"))
            except Exception as e:
                results['email'] = {'success': False, 'error': str(e)}
                self.stdout.write(self.style.ERROR(f"   ❌ Email error: {str(e)}"))
            self.stdout.write("")
        
        # Test SMS
        if sms_phone:
            self.stdout.write("📱 Testing SMS...")
            self.stdout.write(f"   To: {sms_phone}")
            try:
                result = self._test_sms(sms_phone, message)
                results['sms'] = result
                if result['success']:
                    self.stdout.write(self.style.SUCCESS("   ✅ SMS sent successfully!"))
                else:
                    self.stdout.write(self.style.ERROR(f"   ❌ SMS failed: {result['error']}"))
            except Exception as e:
                results['sms'] = {'success': False, 'error': str(e)}
                self.stdout.write(self.style.ERROR(f"   ❌ SMS error: {str(e)}"))
            self.stdout.write("")
        
        # Test WhatsApp
        if whatsapp_phone:
            self.stdout.write("💬 Testing WhatsApp (via Twilio)...")
            self.stdout.write(f"   To: {whatsapp_phone}")
            try:
                result = self._test_whatsapp(whatsapp_phone, message)
                results['whatsapp'] = result
                if result['success']:
                    self.stdout.write(self.style.SUCCESS("   ✅ WhatsApp message sent successfully!"))
                else:
                    self.stdout.write(self.style.ERROR(f"   ❌ WhatsApp failed: {result['error']}"))
            except Exception as e:
                results['whatsapp'] = {'success': False, 'error': str(e)}
                self.stdout.write(self.style.ERROR(f"   ❌ WhatsApp error: {str(e)}"))
            self.stdout.write("")
        
        # Summary
        self.stdout.write("=" * 70)
        self.stdout.write("Test Summary")
        self.stdout.write("=" * 70)
        
        if email:
            status = "✅ PASS" if results['email']['success'] else "❌ FAIL"
            self.stdout.write(f"Email:   {status}")
            if not results['email']['success']:
                self.stdout.write(f"         Error: {results['email']['error']}")
        
        if sms_phone:
            status = "✅ PASS" if results['sms']['success'] else "❌ FAIL"
            self.stdout.write(f"SMS:     {status}")
            if not results['sms']['success']:
                self.stdout.write(f"         Error: {results['sms']['error']}")
        
        if whatsapp_phone:
            status = "✅ PASS" if results['whatsapp']['success'] else "❌ FAIL"
            self.stdout.write(f"WhatsApp: {status}")
            if not results['whatsapp']['success']:
                self.stdout.write(f"         Error: {results['whatsapp']['error']}")
        
        self.stdout.write("=" * 70)
    
    def _test_email(self, email, message):
        """Test sending an email."""
        # Check email configuration
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            return {
                'success': False,
                'error': 'Email backend is set to console. Emails will only print to console, not actually send. Please configure EMAIL_BACKEND in .env file.'
            }
        
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            return {
                'success': False,
                'error': 'Email credentials not configured. Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file.'
            }
        
        try:
            send_mail(
                subject='Test Email - Uplift Your Morning',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return {'success': True, 'error': None}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_sms(self, phone, message):
        """Test sending an SMS via FastR API."""
        secret_key = config('FASTR_API_KEY', default='')
        public_key = config('FASTR_API_PUBLIC_KEY', default='DJbhctlognNbQuEhPMTB9A')
        api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org')
        sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
        
        if not secret_key:
            return {
                'success': False,
                'error': 'FASTR_API_KEY is not set in .env file. Please add: FASTR_API_KEY=9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8'
            }
        
        # Format phone number (Ghana format: 233XXXXXXXXX - no + sign, just digits)
        phone = phone.strip()
        # Remove + sign and any spaces/dashes
        phone = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Prepare request to FastR API according to actual documentation
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
        
        try:
            response = requests.post(
                f'{api_base_url}/sms/send-sms',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:  # FastR returns 201 Created
                try:
                    response_data = response.json()
                    if response_data.get('status') == 'sent':
                        return {'success': True, 'error': None}
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        return {'success': False, 'error': f'SMS sending failed: {error_msg}'}
                except ValueError:
                    return {'success': True, 'error': None}
            elif response.status_code == 400:
                try:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message', 'Invalid request parameters')
                except:
                    error_msg = 'Invalid request parameters'
                return {'success': False, 'error': f'Bad Request: {error_msg}'}
            elif response.status_code == 401:
                try:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message') or error_data.get('error', 'Authentication failed')
                except:
                    error_msg = 'Authentication failed'
                return {'success': False, 'error': f'Authentication failed: {error_msg}'}
            else:
                try:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message') or error_data.get('error', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}'
                return {'success': False, 'error': f'SMS sending failed: {error_msg}'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'SMS sending failed: Request timed out'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'SMS sending failed: Connection error'}
        except Exception as e:
            return {'success': False, 'error': f'SMS sending failed: {str(e)}'}
    
    def _test_whatsapp(self, phone, message):
        """Test sending a WhatsApp message using Twilio API."""
        from apps.subscriptions.whatsapp import send_whatsapp_message
        
        account_sid = config('TWILIO_ACCOUNT_SID', default='')
        auth_token = config('TWILIO_AUTH_TOKEN', default='')
        
        if not account_sid or not auth_token:
            return {
                'success': False,
                'error': 'Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env file.'
            }
        
        try:
            message_sid = send_whatsapp_message(phone, message)
            if message_sid:
                return {'success': True, 'error': None}
            else:
                return {'success': False, 'error': 'WhatsApp message not sent (configuration issue)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

