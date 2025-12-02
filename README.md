# Uplift Your Morning

A Django-based web platform for daily devotions, spiritual resources, events, and community engagement across Africa.

## Features

- 📖 Daily Devotions - Access today's devotion and browse all devotions
- 📅 Events - View and manage upcoming events and prayer gatherings
- 📚 Resources - Download PDFs, audio files, and videos
- 🙏 Community - Share testimonies and submit prayer requests
- 💰 Donations - Secure payment integration with Paystack
- 📧 Subscriptions - Email and WhatsApp subscription management
- 🎨 Admin Dashboard - Custom admin interface for content management

## Tech Stack

- **Backend**: Django 5.2.8
- **Frontend**: Tailwind CSS (via CDN)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Payment**: Paystack API
- **API**: Django REST Framework

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/uplift-your-morning.git
cd uplift-your-morning
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- `SECRET_KEY` - Generate a new Django secret key
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Add your domain(s)
- `PAYSTACK_PUBLIC_KEY` and `PAYSTACK_SECRET_KEY` - Your Paystack credentials

### 5. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Deployment to PythonAnywhere

See `DEPLOYMENT.md` for detailed PythonAnywhere deployment instructions.

## Project Structure

```
uplift-your-morning/
├── apps/
│   ├── core/          # Core utilities
│   ├── pages/         # Static pages and admin dashboard
│   ├── devotions/     # Daily devotions app
│   ├── events/        # Events management
│   ├── resources/     # Resources (PDFs, audio, video)
│   ├── community/     # Testimonies and prayer requests
│   ├── subscriptions/ # Email/WhatsApp subscriptions
│   └── api/           # REST API endpoints
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User-uploaded files
├── uplift_afrika/     # Project settings
└── manage.py          # Django management script
```

## Environment Variables

All sensitive configuration is stored in `.env` file. See `.env.example` for required variables.

## License

Copyright © 2024 Uplift Your Morning. All rights reserved.
