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
    Automatically splits messages that exceed 1600 characters.
    
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
        
        # Twilio WhatsApp has a 1600 character limit per message
        # But we're keeping messages short (300 chars), so splitting is rarely needed
        # Still check in case custom messages push it over
        MAX_LENGTH = 1600
        
        if len(message) <= MAX_LENGTH:
            # Message fits in one send
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            
            if settings.DEBUG:
                print(f"WhatsApp sent successfully. Message SID: {message_obj.sid}")
            
            return message_obj.sid
        else:
            # Split message into chunks
            # Reserve some space for continuation indicator
            chunk_size = MAX_LENGTH - 50  # Leave room for "... (continued)"
            chunks = []
            remaining = message
            
            chunk_num = 1
            total_chunks = (len(message) // chunk_size) + (1 if len(message) % chunk_size > 0 else 0)
            
            while remaining:
                if len(remaining) <= chunk_size:
                    # Last chunk
                    chunks.append(remaining)
                    break
                else:
                    # Find a good break point (prefer newline or space)
                    chunk = remaining[:chunk_size]
                    # Try to break at a newline
                    last_newline = chunk.rfind('\n')
                    if last_newline > chunk_size * 0.8:  # If newline is in last 20% of chunk
                        chunk = remaining[:last_newline]
                        remaining = remaining[last_newline + 1:]
                    else:
                        # Break at space if possible
                        last_space = chunk.rfind(' ')
                        if last_space > chunk_size * 0.8:
                            chunk = remaining[:last_space]
                            remaining = remaining[last_space + 1:]
                        else:
                            # Hard break
                            remaining = remaining[chunk_size:]
                    
                    chunks.append(chunk)
                    chunk_num += 1
            
            # Send all chunks
            message_sids = []
            for i, chunk in enumerate(chunks, 1):
                if len(chunks) > 1:
                    # Add continuation indicator
                    chunk_text = f"{chunk}\n\n[Part {i} of {len(chunks)}]"
                else:
                    chunk_text = chunk
                
                message_obj = client.messages.create(
                    body=chunk_text,
                    from_=from_number,
                    to=phone
                )
                message_sids.append(message_obj.sid)
                
                if settings.DEBUG:
                    print(f"WhatsApp chunk {i}/{len(chunks)} sent. Message SID: {message_obj.sid}")
            
            return message_sids[0]  # Return first message SID
        
    except TwilioException as e:
        error_msg = str(e)
        # Extract more specific error if available
        if '400' in error_msg or 'character limit' in error_msg.lower():
            raise Exception(f"WhatsApp sending failed: HTTP 400 error: {error_msg}")
        raise Exception(f"WhatsApp sending failed: {str(e)}")
    except Exception as e:
        raise Exception(f"WhatsApp sending failed: {str(e)}")

