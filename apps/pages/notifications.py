"""
Notification functions for counseling bookings.
Handles email and SMS notifications when bookings are approved.
Also sends admin notifications when new bookings are submitted.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import CounselingBooking
import requests
from decouple import config


ADMIN_NOTIFICATION_EMAIL = 'comecenters@gmail.com'


def send_booking_submission_notification(booking):
    """
    Send email notification to admin when a new counseling booking is submitted.
    """
    subject = 'New Counseling Booking Request - Uplift Your Morning'
    
    # Format date and time
    preferred_date_str = booking.preferred_date.strftime('%B %d, %Y')
    preferred_time_str = booking.preferred_time.strftime('%I:%M %p')
    
    # Build the email message
    email = booking.email or 'No email provided'
    phone = booking.phone or 'No phone provided'
    country = booking.country or 'Not specified'
    topic = booking.topic or 'Not specified'
    message_text = booking.message or 'No additional message'
    
    message = f"""
A new counseling booking request has been submitted on Uplift Your Morning.

Contact Information:
- Name: {booking.full_name}
- Email: {email}
- Phone: {phone}
- Country: {country}

Booking Details:
- Preferred Date: {preferred_date_str}
- Preferred Time: {preferred_time_str}
- Duration: {booking.duration_minutes} minutes
- Topic: {topic}

Additional Message:
{message_text}

Submitted: {booking.created_at.strftime('%B %d, %Y at %I:%M %p')}
Status: Pending Approval

---
You can review and approve this booking in the admin dashboard.
"""
    
    try:
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
            [ADMIN_NOTIFICATION_EMAIL],
            fail_silently=False,
        )
        # Log success in development
        if settings.DEBUG:
            print(f"✓ Booking submission notification email sent successfully to {ADMIN_NOTIFICATION_EMAIL}")
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        error_msg = f"Failed to send booking submission notification email: {str(e)}"
        logger.error(error_msg)
        
        # In development, also print to console
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")
            print(f"Email notification would be sent to {ADMIN_NOTIFICATION_EMAIL}:")
            print(message)
            print(f"Email backend: {settings.EMAIL_BACKEND}")
            print(f"Email host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
            print(f"Email user: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")


def send_booking_approval_notifications(booking):
    """
    Send email and SMS notifications when a booking is approved.
    """
    if not booking.approved_date or not booking.approved_time:
        raise ValueError("Booking must have approved_date and approved_time before sending notifications")
    
    # Send email notification (only if an email address was provided)
    if booking.email:
        send_booking_approval_email(booking)
    
    # Send SMS notification
    send_booking_approval_sms(booking)
    
    # Mark as sent
    booking.email_sent = bool(booking.email)
    booking.sms_sent = True
    booking.save(update_fields=['email_sent', 'sms_sent'])


def send_booking_approval_email(booking):
    """Send email notification to the user."""
    subject = 'Your Counseling Session Has Been Approved - Uplift Your Morning'
    
    # Format date and time
    approved_date_str = booking.approved_date.strftime('%B %d, %Y')
    approved_time_str = booking.approved_time.strftime('%I:%M %p')
    
    message = f"""
Dear {booking.full_name},

Your counseling session request has been approved!

Session Details:
- Date: {approved_date_str}
- Time: {approved_time_str}
- Duration: {booking.duration_minutes} minutes
- Topic: {booking.topic or 'General Counseling'}

Please make sure to be available at the scheduled time. If you need to reschedule or have any questions, please contact us.

We look forward to meeting with you.

Blessings,
Uplift Your Morning Team
"""
    
    # Try to use configured email backend, fallback to console in development
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
            [booking.email],
            fail_silently=False,
        )
    except Exception as e:
        # In development, print to console
        if settings.DEBUG:
            print(f"Email would be sent to {booking.email}:")
            print(message)
        else:
            raise


def send_booking_approval_sms(booking):
    """Send SMS notification using FastR API (prompt.pywe.org)."""
    secret_key = config('FASTR_API_KEY', default='')
    public_key = config('FASTR_API_PUBLIC_KEY', default='DJbhctlognNbQuEhPMTB9A')
    api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org/api/client')
    sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
    
    if not secret_key:
        # SMS not configured, skip silently
        if settings.DEBUG:
            print(f"SMS not configured. Would send SMS to {booking.phone}")
        return
    
    try:
        approved_date_str = booking.approved_date.strftime('%B %d, %Y')
        approved_time_str = booking.approved_time.strftime('%I:%M %p')
        
        message_body = (
            f"Your counseling session has been approved! "
            f"Date: {approved_date_str} at {approved_time_str}. "
            f"Duration: {booking.duration_minutes} minutes. "
            f"Uplift Your Morning"
        )
        
        # Format phone number (ensure it starts with +, but do not assume a specific country)
        phone = booking.phone.strip()
        if not phone.startswith('+'):
            # If user omitted the +, just add it in front of the digits they provided
            phone = '+' + phone.lstrip(' +0')
        
        # Prepare request to FastR API
        # Try different authentication methods based on API requirements
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Method 1: Try Bearer token with secret key
        if secret_key:
            headers['Authorization'] = f'Bearer {secret_key}'
        
        data = {
            'to': phone,
            'message': message_body,
            'sender_id': sender_id,
        }
        
        # Method 2: Try with secret key in body
        alt_data_1 = {
            'to': phone,
            'message': message_body,
            'sender_id': sender_id,
            'api_key': secret_key,
        }
        
        # Method 3: Try with both public and secret keys
        alt_data_2 = {
            'to': phone,
            'message': message_body,
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
            'message': message_body,
            'sender_id': sender_id,
            'secret_key': secret_key,
        }
        
        # Send SMS via FastR API
        try:
            # Method 1: Try with Bearer token (secret key)
            response = requests.post(
                f'{api_base_url}/sms/send',
                json=data,
                headers=headers,
                timeout=30
            )
            
            # Method 2: If 401, try with secret key in body
            if response.status_code == 401:
                headers_no_auth = {'Content-Type': 'application/json'}
                response = requests.post(
                    f'{api_base_url}/sms/send',
                    json=alt_data_1,
                    headers=headers_no_auth,
                    timeout=30
                )
            
            # Method 3: If still 401, try with both public and secret keys
            if response.status_code == 401:
                headers_no_auth = {'Content-Type': 'application/json'}
                response = requests.post(
                    f'{api_base_url}/sms/send',
                    json=alt_data_2,
                    headers=headers_no_auth,
                    timeout=30
                )
            
            # Method 4: If still 401, try public key in header, secret in body
            if response.status_code == 401:
                response = requests.post(
                    f'{api_base_url}/sms/send',
                    json=alt_data_3,
                    headers=alt_headers,
                    timeout=30
                )
            
            # Check response
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    if response_data.get('status') == 'success' or response_data.get('success'):
                        sms_id = response_data.get('data', {}).get('sms_id')
                        if settings.DEBUG:
                            print(f"SMS sent successfully. SMS ID: {sms_id}")
                        return sms_id
                    else:
                        error_msg = response_data.get('message') or response_data.get('error', 'Unknown error')
                        raise Exception(f"API returned error: {error_msg}")
                except ValueError:
                    # Response might not be JSON, but status code is OK
                    return True
            elif response.status_code == 401:
                error_detail = ""
                try:
                    error_data = response.json() if response.content else {}
                    error_detail = error_data.get('message') or error_data.get('error', '')
                except:
                    pass
                raise Exception(
                    f"Authentication failed (HTTP 401). "
                    f"Please verify your FASTR_API_KEY in .env file. "
                    f"Make sure you're using the SECRET key (9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8), "
                    f"not the public key (DJbhctlognNbQuEhPMTB9A). "
                    f"{'API message: ' + error_detail if error_detail else ''}"
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
            
    except requests.exceptions.RequestException as e:
        # Network or request error
        if settings.DEBUG:
            print(f"SMS sending failed (network error): {str(e)}")
        raise
    except Exception as e:
        # Other errors
        if settings.DEBUG:
            print(f"SMS sending failed: {str(e)}")
        raise


def create_google_calendar_event(booking):
    """
    Create a Google Calendar event for the approved booking.
    Requires Google Calendar API credentials.
    """
    # This is a placeholder - actual implementation requires Google Calendar API setup
    # You'll need to:
    # 1. Set up Google Cloud project
    # 2. Enable Calendar API
    # 3. Create OAuth2 credentials
    # 4. Store refresh token
    
    google_calendar_enabled = config('GOOGLE_CALENDAR_ENABLED', default=False, cast=bool)
    
    if not google_calendar_enabled:
        if settings.DEBUG:
            print(f"Google Calendar not enabled. Would create event for {booking.full_name}")
        return None
    
    # TODO: Implement Google Calendar API integration
    # This requires:
    # - google-api-python-client
    # - google-auth-httplib2
    # - google-auth-oauthlib
    # - OAuth2 credentials for godswilltk@gmail.com
    
    # Example structure:
    # from google.oauth2.credentials import Credentials
    # from googleapiclient.discovery import build
    # 
    # event = {
    #     'summary': f'Counseling Session - {booking.full_name}',
    #     'description': f'Topic: {booking.topic or "General Counseling"}\n\n{booking.message}',
    #     'start': {
    #         'dateTime': f'{booking.approved_date}T{booking.approved_time}',
    #         'timeZone': 'Africa/Accra',
    #     },
    #     'end': {
    #         'dateTime': calculate_end_time(booking),
    #         'timeZone': 'Africa/Accra',
    #     },
    #     'attendees': [
    #         {'email': booking.email},
    #         {'email': 'godswilltk@gmail.com'},
    #     ],
    # }
    # 
    # service.events().insert(calendarId='primary', body=event).execute()
    
    return None

