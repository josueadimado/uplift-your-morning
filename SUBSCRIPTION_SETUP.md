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

### Automated Notification Sending
- **Automated daily sending** - Set up once, runs automatically forever
- Sends to both **email** and **WhatsApp** subscribers based on their preference
- Only sends to subscribers who opted in for daily devotions
- Email subscribers receive full devotion content
- WhatsApp subscribers receive concise SMS with link
- Includes link to read full devotion online

## Setting Up Automated Daily Notifications

**IMPORTANT**: You only need to set this up **ONCE**. After setup, the system runs **automatically every day** - you don't need to do anything manually!

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

### Step 2: Configure SMS/WhatsApp Settings (Optional)

If you have WhatsApp subscribers, add FastR API settings to your `.env` file:

```bash
FASTR_API_KEY=your-secret-key-here
FASTR_API_BASE_URL=https://prompt.pywe.org/api/client
FASTR_SENDER_ID=COME CENTRE
```

**Note**: This is the same API used for counseling booking SMS notifications.

### Step 3: Set Up SITE_URL (Optional)

Add to your `.env` file for proper links in emails:

```bash
SITE_URL=https://upliftyourmorning.com
```

If not set, it defaults to `https://upliftyourmorning.com`.

### Step 4: Set Up Automated Scheduled Task (ONE-TIME SETUP)

**This is the key step!** You'll set up a scheduled task that runs automatically. The command checks for:
1. **Scheduled notifications** that are due to be sent (at their specific scheduled time)
2. **Daily devotions** to send to all subscribers

**IMPORTANT**: For scheduled notifications to work at any time, the command needs to run **frequently** (every hour or every 15 minutes), not just once per day. This way, when you schedule a notification for 2:00 PM, it will be sent at 2:00 PM.

#### On PythonAnywhere (Production Server):

**Option 1: Run Every Hour (Recommended for Scheduled Notifications)**

1. Log into your PythonAnywhere account
2. Go to the **"Tasks"** tab in the dashboard
3. Click **"Create a new scheduled task"**
4. Fill in the details:
   - **Command**: 
     ```bash
     cd ~/your-project-folder && source venv/bin/activate && python manage.py send_daily_devotions
     ```
     (Replace `your-project-folder` with your actual project folder name)
   - **Schedule**: 
     - **Frequency**: Hourly
     - **Time**: Every hour (e.g., :00 minutes past each hour)
   - **Enabled**: ✅ Yes
5. Click **"Create"**

**Option 2: Run Every 15 Minutes (Best for Precise Timing)**

If you want notifications to be sent more precisely (within 15 minutes of scheduled time):

1. Create **4 scheduled tasks** (one for each 15-minute interval):
   - Task 1: Every hour at :00 (e.g., 5:00, 6:00, 7:00...)
   - Task 2: Every hour at :15 (e.g., 5:15, 6:15, 7:15...)
   - Task 3: Every hour at :30 (e.g., 5:30, 6:30, 7:30...)
   - Task 4: Every hour at :45 (e.g., 5:45, 6:45, 7:45...)

**Option 3: Run Once Daily (For Basic Daily Devotions Only)**

If you only want to send daily devotions at a fixed time (not using scheduled notifications):

1. Create a scheduled task:
   - **Frequency**: Daily
   - **Time**: 5:00 AM (or your preferred time)
   - This will send daily devotions but won't check for scheduled notifications at other times

#### On Other Servers (Linux/VPS):

**For Hourly Checks (Recommended):**

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add this line (runs every hour at minute 0):
   ```bash
   0 * * * * cd /path/to/your/project && source venv/bin/activate && python manage.py send_daily_devotions
   ```

**For Every 15 Minutes (Best Precision):**

Add these 4 lines:
```bash
0,15,30,45 * * * * cd /path/to/your/project && source venv/bin/activate && python manage.py send_daily_devotions
```

**For Once Daily (Basic Setup):**

Add this line (runs daily at 5:00 AM):
```bash
0 5 * * * cd /path/to/your/project && source venv/bin/activate && python manage.py send_daily_devotions
```

## How Scheduled Notifications Work

When you schedule a notification for a specific date and time (e.g., "December 25, 2024 at 2:00 PM"):

1. **The notification is stored** in the database with status "Scheduled"
2. **The command runs** (every hour or every 15 minutes, depending on your setup)
3. **The command checks** if any scheduled notifications are due (current time >= scheduled time)
4. **If due and not paused**, the notification is sent to all selected recipients
5. **Status updates** to "Sent" and statistics are recorded

**Example Timeline:**
- You schedule a notification for **Dec 25, 2024 at 2:00 PM**
- Command runs at **2:00 PM** (or within 15 minutes if checking every 15 min)
- System checks: "Is current time (2:00 PM) >= scheduled time (2:00 PM)? Yes!"
- Notification is sent immediately
- Status changes to "Sent"

### Step 5: Test the Command (Before Setting Up Automation)

Before setting up the scheduled task, test the command manually to make sure everything works:

```bash
# Test run (dry-run, doesn't actually send emails/SMS)
python manage.py send_daily_devotions --dry-run

# Actual test (sends to real subscribers - use carefully!)
python manage.py send_daily_devotions
```

**After testing, set up the scheduled task (Step 4) so it runs automatically.**

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

1. **Automatic Execution**: The scheduled task runs automatically every day at the time you set (e.g., 5:00 AM)
2. **Devotion Lookup**: Finds today's published devotion (by `publish_date`)
3. **Subscriber Filtering**: Gets all active subscribers who opted in for daily devotions:
   - **Email subscribers** (`channel='email'`) → Receive email
   - **WhatsApp subscribers** (`channel='whatsapp'`) → Receive SMS/WhatsApp
4. **Notification Sending**: 
   - **Email subscribers**: Receive full devotion content via email
   - **WhatsApp subscribers**: Receive concise SMS/WhatsApp message with link
5. **Content Includes**:
   - Today's devotion title and content
   - Scripture reference and passage
   - Reflection, prayer, and action points
   - Link to read full devotion online
   - Unsubscribe link

**You don't need to do anything - it runs automatically every day!**

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

