"""
Notification functions for community features (prayer requests and testimonies).
Sends email notifications to admin when new submissions are made.
"""
from django.core.mail import send_mail
from django.conf import settings
from .models import PrayerRequest, Testimony


ADMIN_NOTIFICATION_EMAIL = 'comecenters@gmail.com'


def send_prayer_request_notification(prayer_request):
    """
    Send email notification to admin when a new prayer request is submitted.
    """
    print(f"DEBUG: send_prayer_request_notification called for prayer request ID: {prayer_request.id}")
    
    subject = 'New Prayer Request Submitted - Uplift Your Morning'
    
    # Build the email message
    name = prayer_request.name or 'Anonymous'
    email = prayer_request.email or 'No email provided'
    is_public = 'Yes' if prayer_request.is_public else 'No'
    
    message = f"""
A new prayer request has been submitted on Uplift Your Morning.

Details:
- Name: {name}
- Email: {email}
- Public: {is_public}
- Submitted: {prayer_request.created_at.strftime('%B %d, %Y at %I:%M %p')}

Prayer Request:
{prayer_request.request}

---
You can view and manage prayer requests in the admin dashboard.
"""
    
    print(f"DEBUG: About to send email to {ADMIN_NOTIFICATION_EMAIL}")
    print(f"DEBUG: Email subject: {subject}")
    print(f"DEBUG: Email backend: {settings.EMAIL_BACKEND}")
    
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
            print(f"✓ Prayer request notification email sent successfully to {ADMIN_NOTIFICATION_EMAIL}")
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        error_msg = f"Failed to send prayer request notification email: {str(e)}"
        logger.error(error_msg)
        
        # In development, also print to console
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")
            print(f"Email notification would be sent to {ADMIN_NOTIFICATION_EMAIL}:")
            print(message)
            print(f"Email backend: {settings.EMAIL_BACKEND}")
            print(f"Email host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
            print(f"Email user: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")


def send_testimony_notification(testimony):
    """
    Send email notification to admin when a new testimony is submitted.
    """
    print(f"DEBUG: send_testimony_notification called for testimony ID: {testimony.id}")
    
    subject = 'New Testimony Submitted - Uplift Your Morning'
    
    # Build the email message
    name = testimony.name or 'Anonymous'
    country = testimony.country or 'Not specified'
    
    message = f"""
A new testimony has been submitted on Uplift Your Morning.

Details:
- Name: {name}
- Country: {country}
- Submitted: {testimony.created_at.strftime('%B %d, %Y at %I:%M %p')}
- Status: Pending Approval

Testimony:
"{testimony.testimony}"

---
You can review and approve this testimony in the admin dashboard.
"""
    
    print(f"DEBUG: About to send email to {ADMIN_NOTIFICATION_EMAIL}")
    print(f"DEBUG: Email subject: {subject}")
    print(f"DEBUG: Email backend: {settings.EMAIL_BACKEND}")
    
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
            print(f"✓ Testimony notification email sent successfully to {ADMIN_NOTIFICATION_EMAIL}")
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        error_msg = f"Failed to send testimony notification email: {str(e)}"
        logger.error(error_msg)
        
        # In development, also print to console
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")
            print(f"Email notification would be sent to {ADMIN_NOTIFICATION_EMAIL}:")
            print(message)
            print(f"Email backend: {settings.EMAIL_BACKEND}")
            print(f"Email host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
            print(f"Email user: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")

