#!/usr/bin/env python
"""
Test script to send an SMS to a specific phone number.
Usage: python test_sms.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uplift_afrika.settings')
django.setup()

from decouple import config
from django.conf import settings
import requests

def test_sms():
    """Test sending SMS to a specific phone number."""
    phone = "+22872039785"
    message = "Test message from Uplift Your Morning. This is a test SMS to verify the API is working correctly."
    
    secret_key = config('FASTR_API_KEY', default='')
    public_key = config('FASTR_API_PUBLIC_KEY', default='DJbhctlognNbQuEhPMTB9A')
    api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org/api/client')
    sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
    
    print("=" * 60)
    print("SMS Sending Test")
    print("=" * 60)
    print(f"Phone Number: {phone}")
    print(f"Message: {message}")
    print(f"API Base URL: {api_base_url}")
    print(f"Sender ID: {sender_id}")
    print(f"Secret Key: {secret_key[:10]}..." if secret_key else "Secret Key: NOT SET")
    print(f"Public Key: {public_key}")
    print("=" * 60)
    print()
    
    if not secret_key:
        print("❌ ERROR: FASTR_API_KEY is not set in .env file")
        print("Please add: FASTR_API_KEY=9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8")
        return False
    
    # Prepare request to FastR API
    # Try different authentication methods
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Method 1: Try Bearer token with secret key
    if secret_key:
        headers['Authorization'] = f'Bearer {secret_key}'
    
    data = {
        'to': phone,
        'message': message,
        'sender_id': sender_id,
    }
    
    # Method 2: Try with secret key in body
    alt_data_1 = {
        'to': phone,
        'message': message,
        'sender_id': sender_id,
        'api_key': secret_key,
    }
    
    # Method 3: Try with both public and secret keys
    alt_data_2 = {
        'to': phone,
        'message': message,
        'sender_id': sender_id,
        'public_key': public_key,
        'secret_key': secret_key,
    }
    
    # Method 4: Try with public key in header, secret in body
    alt_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {public_key}',
    }
    alt_data_3 = {
        'to': phone,
        'message': message,
        'sender_id': sender_id,
        'secret_key': secret_key,
    }
    
    methods = [
        ("Method 1: Bearer token (secret key)", data, headers),
        ("Method 2: Secret key in body", alt_data_1, {'Content-Type': 'application/json'}),
        ("Method 3: Both keys in body", alt_data_2, {'Content-Type': 'application/json'}),
        ("Method 4: Public key in header, secret in body", alt_data_3, alt_headers),
    ]
    
    for method_name, payload, method_headers in methods:
        print(f"Trying {method_name}...")
        try:
            response = requests.post(
                f'{api_base_url}/sms/send',
                json=payload,
                headers=method_headers,
                timeout=30
            )
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"  Response Body: {response_data}")
            except:
                print(f"  Response Body (text): {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    if response_data.get('status') == 'success' or response_data.get('success'):
                        print(f"✅ SUCCESS! SMS sent successfully using {method_name}")
                        if 'data' in response_data:
                            print(f"   SMS ID: {response_data.get('data', {}).get('sms_id', 'N/A')}")
                        return True
                except ValueError:
                    print(f"✅ SUCCESS! SMS sent (status {response.status_code})")
                    return True
            elif response.status_code == 401:
                print(f"  ❌ Authentication failed (401)")
            elif response.status_code == 403:
                print(f"  ❌ Access forbidden (403)")
            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
            
            print()
            
        except requests.exceptions.Timeout:
            print(f"  ❌ Request timed out")
            print()
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error")
            print()
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            print()
    
    print("❌ All authentication methods failed. Please check your API credentials.")
    return False

if __name__ == '__main__':
    success = test_sms()
    sys.exit(0 if success else 1)

