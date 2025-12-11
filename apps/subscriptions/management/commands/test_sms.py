"""
Django management command to test SMS sending to a specific phone number.
Usage: python manage.py test_sms +22872039785
"""
from django.core.management.base import BaseCommand, CommandError
from decouple import config
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Test sending an SMS to a specific phone number'

    def add_arguments(self, parser):
        parser.add_argument(
            'phone',
            type=str,
            help='Phone number to send test SMS to (e.g., +22872039785)',
        )
        parser.add_argument(
            '--message',
            type=str,
            default='Test message from Uplift Your Morning. This is a test SMS to verify the API is working correctly.',
            help='Custom message to send (optional)',
        )

    def handle(self, *args, **options):
        phone = options['phone']
        message = options['message']
        
        secret_key = config('FASTR_API_KEY', default='')
        public_key = config('FASTR_API_PUBLIC_KEY', default='DJbhctlognNbQuEhPMTB9A')
        api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org/api/client')
        sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
        
        self.stdout.write("=" * 60)
        self.stdout.write("SMS Sending Test")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Phone Number: {phone}")
        self.stdout.write(f"Message: {message}")
        self.stdout.write(f"API Base URL: {api_base_url}")
        self.stdout.write(f"Sender ID: {sender_id}")
        self.stdout.write(f"Secret Key: {secret_key[:10]}..." if secret_key else "Secret Key: NOT SET")
        self.stdout.write(f"Public Key: {public_key}")
        self.stdout.write("=" * 60)
        self.stdout.write("")
        
        if not secret_key:
            self.stdout.write(self.style.ERROR(
                "❌ ERROR: FASTR_API_KEY is not set in .env file"
            ))
            self.stdout.write(self.style.WARNING(
                "Please add: FASTR_API_KEY=9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8"
            ))
            return
        
        # Ensure phone number starts with +
        if not phone.startswith('+'):
            phone = '+' + phone.lstrip('+')
        
        # Try different endpoints
        endpoints_to_try = [
            f'{api_base_url}/sms/send',
            f'{api_base_url}/send',
            f'{api_base_url}/sms',
        ]
        
        # Prepare different authentication methods
        methods = [
            {
                'name': 'Method 1: Bearer token (secret key)',
                'headers': {'Content-Type': 'application/json', 'Authorization': f'Bearer {secret_key}'},
                'data': {'to': phone, 'message': message, 'sender_id': sender_id},
            },
            {
                'name': 'Method 2: Secret key in body as api_key',
                'headers': {'Content-Type': 'application/json'},
                'data': {'to': phone, 'message': message, 'sender_id': sender_id, 'api_key': secret_key},
            },
            {
                'name': 'Method 3: Both keys in body',
                'headers': {'Content-Type': 'application/json'},
                'data': {'to': phone, 'message': message, 'sender_id': sender_id, 'public_key': public_key, 'secret_key': secret_key},
            },
            {
                'name': 'Method 4: Public key in header, secret in body',
                'headers': {'Content-Type': 'application/json', 'Authorization': f'Bearer {public_key}'},
                'data': {'to': phone, 'message': message, 'sender_id': sender_id, 'secret_key': secret_key},
            },
            {
                'name': 'Method 5: Secret key as X-API-Key header',
                'headers': {'Content-Type': 'application/json', 'X-API-Key': secret_key},
                'data': {'to': phone, 'message': message, 'sender_id': sender_id},
            },
            {
                'name': 'Method 6: Public key as X-API-Key header, secret in body',
                'headers': {'Content-Type': 'application/json', 'X-API-Key': public_key},
                'data': {'to': phone, 'message': message, 'sender_id': sender_id, 'secret_key': secret_key},
            },
        ]
        
        # Try each endpoint with each method
        for endpoint in endpoints_to_try:
            self.stdout.write(f"\n--- Trying endpoint: {endpoint} ---")
            for method in methods:
                self.stdout.write(f"Trying {method['name']}...")
                try:
                    response = requests.post(
                        endpoint,
                        json=method['data'],
                        headers=method['headers'],
                        timeout=30
                    )
                    
                    self.stdout.write(f"  Status Code: {response.status_code}")
                    
                    try:
                        response_data = response.json()
                        self.stdout.write(f"  Response: {response_data}")
                        
                        if response.status_code in [200, 201]:
                            if response_data.get('status') == 'success' or response_data.get('success'):
                                self.stdout.write(self.style.SUCCESS(
                                    f"✅ SUCCESS! SMS sent successfully using {method['name']}"
                                ))
                                if 'data' in response_data:
                                    sms_id = response_data.get('data', {}).get('sms_id', 'N/A')
                                    self.stdout.write(f"   SMS ID: {sms_id}")
                                return
                    except ValueError:
                        self.stdout.write(f"  Response (text): {response.text[:200]}")
                        if response.status_code in [200, 201]:
                            self.stdout.write(self.style.SUCCESS(
                                f"✅ SUCCESS! SMS sent (status {response.status_code})"
                            ))
                            return
                    
                    if response.status_code == 401:
                        self.stdout.write(self.style.ERROR("  ❌ Authentication failed (401)"))
                    elif response.status_code == 403:
                        self.stdout.write(self.style.ERROR("  ❌ Access forbidden (403)"))
                    elif response.status_code == 405:
                        self.stdout.write(self.style.WARNING("  ⚠️  Method not allowed (405) - wrong endpoint"))
                    else:
                        self.stdout.write(self.style.ERROR(f"  ❌ Error: HTTP {response.status_code}"))
                    
                except requests.exceptions.Timeout:
                    self.stdout.write(self.style.ERROR("  ❌ Request timed out"))
                except requests.exceptions.ConnectionError:
                    self.stdout.write(self.style.ERROR("  ❌ Connection error"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Error: {str(e)}"))
                
                self.stdout.write("")
        
        self.stdout.write(self.style.ERROR(
            "❌ All authentication methods failed. Please check your API credentials and endpoint."
        ))
        self.stdout.write(self.style.WARNING(
            "\nPossible issues:"
        ))
        self.stdout.write("  1. API credentials may be incorrect")
        self.stdout.write("  2. API endpoint may have changed")
        self.stdout.write("  3. Account may need activation or verification")
        self.stdout.write("  4. Phone number format may not be accepted")
        self.stdout.write("\nPlease contact FastR API support or check their documentation.")
