# Email Setup Guide - Gmail Configuration

## Step 1: Generate Gmail App Password

Since you're using Gmail (`comecenters@gmail.com`), you need to create an **App Password** (not your regular password).

### How to Generate Gmail App Password:

1. **Go to your Google Account**: https://myaccount.google.com/
2. **Enable 2-Step Verification** (if not already enabled):
   - Go to Security → 2-Step Verification
   - Follow the prompts to enable it
3. **Generate App Password**:
   - Go to Security → 2-Step Verification
   - Scroll down to "App passwords"
   - Click "App passwords"
   - Select "Mail" as the app
   - Select "Other (Custom name)" as the device
   - Enter "Uplift Your Morning" as the name
   - Click "Generate"
   - **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)

## Step 2: Update .env File

Add or update these lines in your `.env` file:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=comecenters@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password-here
DEFAULT_FROM_EMAIL=comecenters@gmail.com
```

**Important Notes:**
- Replace `your-16-character-app-password-here` with the actual 16-character App Password you generated
- Remove any spaces from the App Password (it might be shown as `abcd efgh ijkl mnop`, but use it as `abcdefghijklmnop`)
- Make sure there are NO comments on the same line as the password (this was causing issues before)

## Step 3: Test the Email Configuration

After updating your `.env` file, test the email sending:

### Option 1: Use the Test Notifications Command

```bash
python manage.py test_notifications --email your-test-email@gmail.com
```

This will send a test email to verify the configuration works.

### Option 2: Test via Django Shell

```bash
python manage.py shell
```

Then run:
```python
from django.core.mail import send_mail
from django.conf import settings

# Check configuration
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Email Password Set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")

# Send test email
try:
    send_mail(
        subject='Test Email from Uplift Your Morning',
        message='This is a test email to verify the email configuration is working correctly.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['your-test-email@gmail.com'],  # Replace with your test email
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Email failed: {str(e)}")
```

### Option 3: Test via Counseling Booking

1. Go to `/counseling/` and submit a test booking
2. Go to `/manage/counseling/` and approve the booking
3. Check if the email notification is sent

## Troubleshooting

### Error: "Username and Password not accepted"
- Make sure you're using the **App Password**, not your regular Gmail password
- Verify 2-Step Verification is enabled
- Check that there are no spaces or extra characters in the password
- Make sure there are no comments on the same line in `.env`

### Error: "Less secure app access"
- Gmail no longer supports "less secure apps"
- You MUST use App Passwords (not regular passwords)
- Make sure 2-Step Verification is enabled

### Error: "Connection refused" or "Timeout"
- Check your internet connection
- Verify `EMAIL_HOST=smtp.gmail.com` and `EMAIL_PORT=587`
- Check if your firewall is blocking port 587

### Email Backend is Console
- Make sure `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` (not `console`)
- Restart your Django server after changing `.env`

## Security Notes

- **Never commit your `.env` file to git** (it should be in `.gitignore`)
- **Never share your App Password** publicly
- If you suspect your App Password is compromised, revoke it and generate a new one
- App Passwords are specific to each app - you can have multiple for different services

