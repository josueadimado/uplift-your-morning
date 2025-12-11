"""
WhatsApp messaging using Twilio API.
"""
from django.conf import settings
from decouple import config
from twilio.rest import Client
from twilio.base.exceptions import TwilioException


def send_whatsapp_message(phone, message):
    """
    Send a WhatsApp message using Twilio API.
    
    Args:
        phone: Phone number in international format (e.g., +233598158589)
        message: Message content to send
        
    Returns:
        str: Message SID if successful, None if not configured
        
    Raises:
        Exception: If sending fails
    """
    account_sid = config('TWILIO_ACCOUNT_SID', default='')
    auth_token = config('TWILIO_AUTH_TOKEN', default='')
    from_number = config('TWILIO_WHATSAPP_FROM', default='whatsapp:+14155238886')
    
    if not account_sid or not auth_token:
        if settings.DEBUG:
            print(f"WhatsApp not configured. Would send WhatsApp to {phone}")
        return None
    
    try:
        # Format phone number for WhatsApp (must include country code with +)
        phone = phone.strip()
        if not phone.startswith('+'):
            phone = '+' + phone.lstrip(' +0')
        
        # Ensure phone number is in WhatsApp format
        if not phone.startswith('whatsapp:'):
            phone = f'whatsapp:{phone}'
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send WhatsApp message
        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=phone
        )
        
        if settings.DEBUG:
            print(f"WhatsApp sent successfully. Message SID: {message_obj.sid}")
        
        return message_obj.sid
        
    except TwilioException as e:
        raise Exception(f"WhatsApp sending failed: {str(e)}")
    except Exception as e:
        raise Exception(f"WhatsApp sending failed: {str(e)}")

