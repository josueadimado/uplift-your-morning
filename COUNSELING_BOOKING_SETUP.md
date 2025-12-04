# Counseling Booking System Setup Guide

This guide explains how to set up the counseling booking system with email notifications, SMS notifications, and Google Calendar integration.

## Features

- ✅ Users can submit counseling booking requests via `/counseling/`
- ✅ Admin dashboard to view, approve, and reject bookings
- ✅ Email notifications when bookings are approved
- ✅ SMS notifications when bookings are approved (via FastR API)
- ✅ Google Calendar integration (creates events in godswilltk@gmail.com calendar)

## Database Setup

Run the migration to create the `CounselingBooking` model:

```bash
python manage.py migrate
```

## Email Configuration

### Option 1: Gmail SMTP (Recommended for Development)

Add these to your `.env` file:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Use App Password, not regular password
DEFAULT_FROM_EMAIL=noreply@upliftyourmorning.com
```

**Note:** For Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an "App Password" (not your regular password)
3. Use the App Password in `EMAIL_HOST_PASSWORD`

### Option 2: SendGrid (Recommended for Production)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@upliftyourmorning.com
```

### Option 3: Console Backend (Development Only)

For testing without sending real emails:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## SMS Configuration (FastR API)

1. **Add to `.env` file**:

```env
FASTR_API_KEY=9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8
FASTR_API_BASE_URL=https://prompt.pywe.org/api/client
FASTR_SENDER_ID=COME CENTRE
```

**Note:** 
- Use your **secret key** (not the public key) for `FASTR_API_KEY`
- Your public key: `DJbhctlognNbQuEhPMTB9A` (for reference only)
- Your secret key: `9fzban1DkdoJUbOfOrzvD-H-7BUc6QP96uf0gYSKUn8` (use this for authentication)
- The sender ID is set to "COME CENTRE" by default
- SMS notifications will be skipped if `FASTR_API_KEY` is not configured
- The system will work without SMS, but users won't receive SMS confirmations
- Phone numbers should be in international format (e.g., +2341234567890)

## Google Calendar Integration

### Setup Steps

1. **Create a Google Cloud Project**:
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" or "Web application"
   - Download the JSON file

4. **Authorize the Application**:
   - You'll need to run a one-time authorization script to get a refresh token
   - This allows the app to create calendar events on behalf of godswilltk@gmail.com

5. **Add to `.env` file**:

```env
GOOGLE_CALENDAR_ENABLED=True
GOOGLE_CALENDAR_EMAIL=godswilltk@gmail.com
GOOGLE_CALENDAR_CREDENTIALS_FILE=/path/to/credentials.json
GOOGLE_CALENDAR_REFRESH_TOKEN=your_refresh_token
```

### Implementation Note

The Google Calendar integration is currently a placeholder in `apps/pages/notifications.py`. To fully implement it, you'll need to:

1. Install Google API libraries (already in requirements.txt):
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. Complete the `create_google_calendar_event()` function in `apps/pages/notifications.py`

3. Set up OAuth2 flow to get refresh token for godswilltk@gmail.com

**For now, the system will work without Google Calendar integration.** Bookings will still be created and notifications sent, but calendar events won't be automatically created.

## Admin Access

1. **View Bookings**: Navigate to `/manage/counseling/` in the admin dashboard
2. **Approve/Reject**: Click on a booking to view details and approve or reject
3. **When Approved**:
   - Email notification is sent to the user
   - SMS notification is sent (if FastR API is configured)
   - Google Calendar event is created (if configured)

## User Flow

1. User visits `/counseling/` and fills out the booking form
2. Booking is created with status "Pending"
3. Admin reviews booking in dashboard
4. Admin approves booking
5. System automatically:
   - Sends email confirmation
   - Sends SMS confirmation (if configured)
   - Creates Google Calendar event (if configured)
   - Updates booking status to "Approved"

## Testing

### Test Email (Development)

With console backend, emails will print to terminal:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Test SMS

SMS will be skipped if FastR API is not configured. To test:
1. Get your FastR API key
2. Add `FASTR_API_KEY` to `.env`
3. Submit a booking and approve it
4. Check your FastR dashboard for sent messages

### Test Calendar

Calendar integration requires full OAuth2 setup. For now, it will log a message in development mode.

## Troubleshooting

### Email Not Sending

- Check `EMAIL_BACKEND` in settings
- Verify SMTP credentials
- Check spam folder
- For Gmail: Make sure you're using an App Password, not your regular password

### SMS Not Sending

- Verify `FASTR_API_KEY` in `.env`
- Check FastR account balance
- Ensure phone number format is correct (include country code, e.g., +234...)
- Verify `FASTR_API_BASE_URL` is set to `https://prompt.pywe.org/api/client`
- Check FastR dashboard for error logs
- Verify sender ID "COME CENTRE" is registered/approved

### Calendar Not Creating Events

- Verify `GOOGLE_CALENDAR_ENABLED=True`
- Check OAuth2 credentials
- Ensure refresh token is valid
- Complete the implementation in `notifications.py`

## Next Steps

1. Set up email backend (Gmail or SendGrid)
2. Set up FastR API for SMS (optional but recommended)
   - Get your API key from FastR dashboard
   - Add `FASTR_API_KEY` to `.env`
3. Complete Google Calendar OAuth2 setup (optional)
4. Test the full flow: submit booking → approve → verify notifications

## Support

For issues or questions, check:
- Django email documentation: https://docs.djangoproject.com/en/stable/topics/email/
- FastR API documentation: https://pushr.pywe.org/api/client (or check your FastR dashboard)
- Google Calendar API: https://developers.google.com/calendar/api

