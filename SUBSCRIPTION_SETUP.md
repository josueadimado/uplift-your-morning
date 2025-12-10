# Subscription System Setup Guide

This guide explains how to set up and use the automated daily devotion email system.

## Overview

The subscription system allows users to subscribe to receive daily devotions via email or WhatsApp. The system includes:

1. **Subscription Management**: Users can subscribe/unsubscribe via web forms or API
2. **Admin Dashboard**: View subscriber statistics and manage subscriptions
3. **Automated Email Sending**: Daily command to send devotions to subscribers

## Features

### Subscriber Management
- Email and WhatsApp subscriptions
- Preference management (daily devotions, special programs)
- Active/inactive status tracking
- Admin interface for managing subscribers

### Automated Email Sending
- Daily command to send today's devotion to all active email subscribers
- Only sends to subscribers who opted in for daily devotions
- Includes full devotion content in email
- Link to read devotion online

## Setting Up Automated Daily Emails

### Step 1: Configure Email Settings

Make sure your `.env` file has proper email configuration:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Use Gmail App Password, not regular password
DEFAULT_FROM_EMAIL=noreply@upliftyourmorning.com
```

**Important**: For Gmail, you must use an App Password, not your regular password. See the main deployment guide for instructions.

### Step 2: Set Up SITE_URL (Optional)

Add to your `.env` file for proper links in emails:

```bash
SITE_URL=https://upliftyourmorning.com
```

If not set, it defaults to `https://upliftyourmorning.com`.

### Step 3: Set Up Cron Job (Production)

On your production server (PythonAnywhere), set up a scheduled task to run daily:

1. Go to PythonAnywhere Dashboard
2. Click "Tasks" tab
3. Create a new scheduled task:
   - **Command**: `cd ~/uplift-your-morning && source venv/bin/activate && python manage.py send_daily_devotions`
   - **Schedule**: Daily at 5:00 AM (or your preferred time, before devotion time)
   - **Enabled**: Yes

**Note**: Make sure the time is set before your devotion time so subscribers receive it in the morning.

### Step 4: Test the Command

Before setting up the cron job, test the command manually:

```bash
# Test run (dry-run, doesn't actually send emails)
python manage.py send_daily_devotions --dry-run

# Actual test (sends to real subscribers)
python manage.py send_daily_devotions
```

## Command Options

### Basic Usage
```bash
python manage.py send_daily_devotions
```

### Options

- `--dry-run`: Test mode - shows what would be sent without actually sending emails
- `--force`: Send email even if no devotion is published for today (sends a "no devotion" message)

### Examples

```bash
# Test run
python manage.py send_daily_devotions --dry-run

# Force send (even if no devotion today)
python manage.py send_daily_devotions --force

# Normal run
python manage.py send_daily_devotions
```

## How It Works

1. **Command Execution**: Runs daily via cron job
2. **Devotion Lookup**: Finds today's published devotion (by `publish_date`)
3. **Subscriber Filtering**: Gets all active email subscribers who opted in for daily devotions
4. **Email Sending**: Sends personalized email to each subscriber with:
   - Today's devotion title and content
   - Scripture reference and passage
   - Reflection, prayer, and action points
   - Link to read full devotion online
   - Unsubscribe link

## Email Content

The email includes:
- Greeting
- Full devotion content (scripture, body, reflection, prayer, action point)
- Link to read online
- Unsubscribe information

## Troubleshooting

### Emails Not Sending

1. **Check Email Configuration**: Verify `.env` settings are correct
2. **Test Email Backend**: Run `python manage.py send_daily_devotions --dry-run` to see errors
3. **Check Gmail App Password**: Make sure you're using an App Password, not regular password
4. **Check Server Logs**: Look for error messages in PythonAnywhere error logs

### No Devotion Found

- The command will skip sending if no devotion is published for today
- Use `--force` flag to send a "no devotion" message to subscribers
- Make sure devotions are published with today's date in `publish_date` field

### Subscribers Not Receiving

1. **Check Subscriber Status**: Verify subscribers are `is_active=True`
2. **Check Preferences**: Verify `receive_daily_devotion=True`
3. **Check Email Addresses**: Make sure email addresses are valid
4. **Check Spam Folder**: Emails might be going to spam

## Admin Dashboard

The admin dashboard (`/manage/`) now includes:

- **Subscriptions Section**: Shows total, active, email, WhatsApp subscribers
- **Recent Subscribers**: Lists the 5 most recent subscribers
- **Quick Links**: Direct link to manage all subscribers in Django admin

## Future Enhancements

Potential improvements:
- WhatsApp integration for sending devotions via WhatsApp
- HTML email templates (currently plain text)
- Email scheduling options
- Unsubscribe tracking
- Bounce handling
- Email analytics

