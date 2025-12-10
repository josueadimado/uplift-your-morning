# Notification Scheduling System Guide

## Overview

The notification scheduling system allows you to schedule notifications to be sent to subscribers at specific dates and times. This guide explains how it works and how to set it up.

## How It Works

### When You Schedule a Notification

1. **You create a notification** in the dashboard (`/manage/notifications/create/`)
2. **Set the date and time** (e.g., December 25, 2024 at 2:00 PM)
3. **Preview the messages** that will be sent (email and WhatsApp)
4. **Save the notification** - it's now stored with status "Scheduled"

### When the Scheduled Time Arrives

The system uses a background command (`send_daily_devotions`) that runs periodically to check for due notifications:

1. **Command runs** (every hour or every 15 minutes, depending on your setup)
2. **Checks database** for scheduled notifications where:
   - Status = "Scheduled"
   - Is Paused = False
   - Current time >= Scheduled time
3. **If found**, sends the notification to all selected recipients:
   - Email subscribers (if enabled)
   - WhatsApp subscribers (if enabled)
4. **Updates status** to "Sent" and records statistics

### Timing Precision

- **If command runs every hour**: Notifications will be sent within 1 hour of scheduled time
- **If command runs every 15 minutes**: Notifications will be sent within 15 minutes of scheduled time
- **If command runs once daily**: Only daily devotions work; scheduled notifications won't be checked at other times

## Setting Up the Command

### Recommended: Run Every Hour

This ensures scheduled notifications are sent within 1 hour of their scheduled time.

**PythonAnywhere:**
- Create a scheduled task that runs **Hourly** at minute :00

**Linux/VPS (Cron):**
```bash
0 * * * * cd /path/to/project && source venv/bin/activate && python manage.py send_daily_devotions
```

### Best Precision: Run Every 15 Minutes

This ensures scheduled notifications are sent within 15 minutes of their scheduled time.

**PythonAnywhere:**
- Create 4 scheduled tasks:
  - Every hour at :00
  - Every hour at :15
  - Every hour at :30
  - Every hour at :45

**Linux/VPS (Cron):**
```bash
0,15,30,45 * * * * cd /path/to/project && source venv/bin/activate && python manage.py send_daily_devotions
```

## Example Scenarios

### Scenario 1: Daily Devotion at 5:00 AM

1. Schedule notification for **Tomorrow at 5:00 AM**
2. Command runs at **5:00 AM** (or within 15 min if checking every 15 min)
3. Notification is sent to all subscribers
4. Status changes to "Sent"

### Scenario 2: Special Announcement at 2:00 PM

1. Schedule notification for **December 25, 2024 at 2:00 PM**
2. Command runs at **2:00 PM** (or within 15 min)
3. Notification is sent
4. Status changes to "Sent"

### Scenario 3: Paused Notification

1. Schedule notification for **Tomorrow at 10:00 AM**
2. Before 10:00 AM, you click **"Pause"**
3. Command runs at **10:00 AM** but skips this notification (it's paused)
4. Status remains "Paused"
5. You can click **"Resume"** later to reactivate it

## Features

### Preview Messages
- See exactly what will be sent to email subscribers
- See exactly what will be sent to WhatsApp subscribers
- Preview shows recipient counts

### Pause/Resume
- Pause notifications before they're sent
- Resume paused notifications
- Useful for last-minute changes

### Statistics
- Track how many emails were sent
- Track how many emails failed
- Track how many SMS/WhatsApp were sent
- Track how many SMS/WhatsApp failed

## Troubleshooting

### Notification Not Sent at Scheduled Time

1. **Check if command is running**: Look at server logs or PythonAnywhere task logs
2. **Check notification status**: Go to `/manage/notifications/` and verify status
3. **Check if paused**: Paused notifications won't be sent
4. **Check command frequency**: If command only runs once daily, it won't catch notifications at other times

### Notification Sent Multiple Times

- This shouldn't happen - the system marks notifications as "Sent" after sending
- If it does, check if multiple command instances are running

### Command Not Running

1. **PythonAnywhere**: Check "Tasks" tab - ensure task is enabled
2. **Linux/VPS**: Check cron logs: `grep CRON /var/log/syslog`
3. **Test manually**: Run `python manage.py send_daily_devotions --dry-run`

## Best Practices

1. **Run command frequently** (every hour or every 15 minutes) for best precision
2. **Preview messages** before scheduling to ensure content is correct
3. **Test with dry-run** before scheduling important notifications
4. **Monitor statistics** after sending to ensure delivery success
5. **Use pause feature** if you need to make last-minute changes

