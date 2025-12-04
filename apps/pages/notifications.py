"""
Notification functions for counseling bookings.
Handles email and SMS notifications when bookings are approved.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import CounselingBooking
import requests
from decouple import config


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
    api_key = config('FASTR_API_KEY', default='')
    api_base_url = config('FASTR_API_BASE_URL', default='https://prompt.pywe.org/api/client')
    sender_id = config('FASTR_SENDER_ID', default='COME CENTRE')
    
    if not api_key:
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
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'to': phone,
            'message': message_body,
            'sender_id': sender_id,
        }
        
        # Send SMS via FastR API
        response = requests.post(
            f'{api_base_url}/sms/send',
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            response_data = response.json()
            if response_data.get('status') == 'success':
                sms_id = response_data.get('data', {}).get('sms_id')
                if settings.DEBUG:
                    print(f"SMS sent successfully. SMS ID: {sms_id}")
                return sms_id
            else:
                error_msg = response_data.get('message', 'Unknown error')
                if settings.DEBUG:
                    print(f"SMS API returned error: {error_msg}")
                raise Exception(f"SMS API error: {error_msg}")
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('message', f'HTTP {response.status_code}')
            if settings.DEBUG:
                print(f"SMS sending failed with status {response.status_code}: {error_msg}")
            raise Exception(f"SMS sending failed: {error_msg}")
            
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

