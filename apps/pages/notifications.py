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
    Also sends notification emails to admin team.
    
    Returns:
        dict: {
            'success': bool,
            'email_sent': bool,
            'sms_sent': bool,
            'admin_notification_sent': bool,
            'errors': {
                'email': str or None,
                'sms': str or None,
                'admin': str or None
            }
        }
    """
    if not booking.approved_date or not booking.approved_time:
        raise ValueError("Booking must have approved_date and approved_time before sending notifications")
    
    result = {
        'success': True,
        'email_sent': False,
        'sms_sent': False,
        'admin_notification_sent': False,
        'errors': {
            'email': None,
            'sms': None,
            'admin': None
        }
    }
    
    # Send email notification to user (only if an email address was provided)
    if booking.email:
        try:
            send_booking_approval_email(booking)
            result['email_sent'] = True
        except Exception as e:
            result['success'] = False
            result['errors']['email'] = str(e)
            if settings.DEBUG:
                print(f"Email notification failed: {str(e)}")
    
    # Send SMS notification to user
    try:
        send_booking_approval_sms(booking)
        result['sms_sent'] = True
    except Exception as e:
        result['success'] = False
        result['errors']['sms'] = str(e)
        if settings.DEBUG:
            print(f"SMS notification failed: {str(e)}")
    
    # Send notification emails to admin team
    try:
        send_booking_approval_admin_notification(booking)
        result['admin_notification_sent'] = True
    except Exception as e:
        result['success'] = False
        result['errors']['admin'] = str(e)
        if settings.DEBUG:
            print(f"Admin notification failed: {str(e)}")
    
    # Mark as sent (only mark what actually succeeded)
    booking.email_sent = result['email_sent']
    booking.sms_sent = result['sms_sent']
    booking.save(update_fields=['email_sent', 'sms_sent'])
    
    return result


def send_booking_approval_admin_notification(booking):
    """Send notification email to admin team when a booking is approved."""
    admin_emails = ['godswilltk@gmail.com', 'josueadimado@gmail.com']
    
    subject = f'Counseling Session Approved - {booking.full_name}'
    
    # Format date and time
    approved_date_str = booking.approved_date.strftime('%B %d, %Y')
    approved_time_str = booking.approved_time.strftime('%I:%M %p')
    
    # Zoom meeting link
    zoom_link = 'https://us02web.zoom.us/j/6261738082?pwd=RWNTU3RsNEdGMWcxOGpxRWtNM00zdz09'
    
    message = f"""
A counseling session has been approved:

Client Information:
- Name: {booking.full_name}
- Email: {booking.email or 'No email provided'}
- Phone: {booking.phone}
- Country: {booking.country or 'Not specified'}

Session Details:
- Date: {approved_date_str}
- Time: {approved_time_str}
- Duration: {booking.duration_minutes} minutes
- Topic: {booking.topic or 'General Counseling'}

Meeting Link:
{zoom_link}

Please join the meeting at the scheduled time.

---
Uplift Your Morning Admin System
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@upliftyourmorning.com',
            admin_emails,
            fail_silently=False,
        )
        if settings.DEBUG:
            print(f"✓ Admin notification emails sent successfully to {', '.join(admin_emails)}")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        error_msg = f"Failed to send admin notification emails: {str(e)}"
        logger.error(error_msg)
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")


def send_booking_approval_email(booking):
    """Send email notification to the user."""
    subject = 'Your Counseling Session Has Been Approved - Uplift Your Morning'
    
    # Format date and time
    approved_date_str = booking.approved_date.strftime('%B %d, %Y')
    approved_time_str = booking.approved_time.strftime('%I:%M %p')
    
    # Zoom meeting link
    zoom_link = 'https://us02web.zoom.us/j/6261738082?pwd=RWNTU3RsNEdGMWcxOGpxRWtNM00zdz09'
    
    message = f"""
Dear {booking.full_name},

Your counseling session request has been approved!

Session Details:
- Date: {approved_date_str}
- Time: {approved_time_str}
- Duration: {booking.duration_minutes} minutes
- Topic: {booking.topic or 'General Counseling'}

Meeting Link:
{zoom_link}

Please join the meeting at the scheduled time using the link above. If you need to reschedule or have any questions, please contact us.

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
        
        # Zoom meeting link (shortened for SMS)
        zoom_link = 'https://us02web.zoom.us/j/6261738082?pwd=RWNTU3RsNEdGMWcxOGpxRWtNM00zdz09'
        
        # Keep SMS concise (max ~160 chars for single SMS, but can be longer if API supports concatenation)
        # Check message length
        message_body = (
            f"Session approved! {approved_date_str} at {approved_time_str}. "
            f"Join: {zoom_link}"
        )
        
        # Warn if message is very long (some carriers have limits)
        if len(message_body) > 500:
            if settings.DEBUG:
                print(f"WARNING: SMS message is {len(message_body)} characters long, which may cause issues with some carriers")
        
        # Format phone number (Ghana format: 233XXXXXXXXX - no + sign, just digits)
        phone = booking.phone.strip()
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
            'message': message_body,
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
                        message_id = response_data.get('id')
                        if settings.DEBUG:
                            print(f"SMS sent successfully. Message ID: {message_id}")
                        return message_id
                    else:
                        # Get error message from API response
                        error_msg = response_data.get('message') or response_data.get('error') or response_data.get('detail', 'Unknown error')
                        # Log full response for debugging
                        if settings.DEBUG:
                            print(f"SMS API Response (status != 'sent'): {response_data}")
                        # If the error message is the same as our message body, it's likely a parsing issue
                        if error_msg == message_body or error_msg.strip() == message_body.strip():
                            raise Exception(
                                f"SMS API rejected the message. "
                                f"Message length: {len(message_body)} characters. "
                                f"API returned the message content as error, which suggests a parsing or format issue. "
                                f"Full response: {response_data}"
                            )
                        else:
                            raise Exception(
                                f"SMS API error (HTTP 201 but status != 'sent'): {error_msg}. "
                                f"Full response: {response_data}"
                            )
                except ValueError:
                    # Response might not be JSON, but status code is OK
                    if settings.DEBUG:
                        print(f"SMS response was not JSON but status code is 201. Response: {response.text[:200]}")
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

