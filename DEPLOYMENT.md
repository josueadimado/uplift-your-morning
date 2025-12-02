# Deployment Guide - PythonAnywhere

This guide will help you deploy Uplift Your Morning to PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account (free or paid)
2. Your code pushed to GitHub
3. Your domain name (if using custom domain)

## Step 1: Prepare Your Code

### 1.1 Update settings.py for Production

Make sure your `settings.py` has production-ready settings:

```python
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
```

### 1.2 Update requirements.txt

Ensure all dependencies are listed:

```bash
pip freeze > requirements.txt
```

## Step 2: Push to GitHub

1. Create a new repository on GitHub
2. Initialize git and push:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

## Step 3: PythonAnywhere Setup

### 3.1 Clone Your Repository

1. Log into PythonAnywhere
2. Open a Bash console
3. Navigate to your home directory
4. Clone your repository:

```bash
cd ~
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 3.2 Create Virtual Environment

```bash
python3.10 -m venv venv  # Use Python 3.10 or your preferred version
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Set Up Environment Variables

Create a `.env` file in your project root:

```bash
nano .env
```

Add your environment variables:

```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
PAYSTACK_SECRET_KEY=your-paystack-secret-key
```

### 3.4 Database Setup

For SQLite (simple, good for small sites):
```bash
python manage.py migrate
python manage.py createsuperuser
```

For PostgreSQL (recommended for production):
1. Create a database in PythonAnywhere's database tab
2. Update your `.env` with database credentials
3. Install psycopg2: `pip install psycopg2-binary`
4. Run migrations

### 3.5 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 4: Configure Web App

### 4.1 Create Web App

1. Go to PythonAnywhere Dashboard
2. Click "Web" tab
3. Click "Add a new web app"
4. Choose "Manual configuration"
5. Select Python version (3.10 recommended)

### 4.2 WSGI Configuration

1. Click on your web app
2. Click "WSGI configuration file" link
3. Replace the content with:

```python
import os
import sys

# Add your project directory to the path
path = '/home/yourusername/your-repo-name'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'uplift_afrika.settings'

# Activate virtual environment
activate_this = '/home/yourusername/your-repo-name/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important**: Replace `yourusername` and `your-repo-name` with your actual values!

### 4.3 Static Files Mapping

In the Web app configuration:

1. Go to "Static files" section
2. Add mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/your-repo-name/staticfiles/`

3. Add media files mapping:
   - URL: `/media/`
   - Directory: `/home/yourusername/your-repo-name/media/`

### 4.4 Update Source Code Path

In Web app configuration, set:
- Source code: `/home/yourusername/your-repo-name`

## Step 5: Reload Web App

Click the green "Reload" button in the Web app tab.

## Step 6: Create Superuser

In a Bash console:

```bash
cd ~/your-repo-name
source venv/bin/activate
python manage.py createsuperuser
```

## Step 7: Test Your Site

Visit: `https://yourusername.pythonanywhere.com`

## Troubleshooting

### Static files not loading
- Check static files mapping in Web app configuration
- Run `python manage.py collectstatic` again
- Check file permissions

### 500 Error
- Check error log in Web app tab
- Verify `.env` file exists and has correct values
- Check `ALLOWED_HOSTS` includes your domain

### Database errors
- Verify database credentials in `.env`
- Run migrations: `python manage.py migrate`
- Check database file permissions (for SQLite)

### Module not found errors
- Activate virtual environment: `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Check WSGI file has correct paths

## Updating Your Site

When you push updates to GitHub:

```bash
cd ~/your-repo-name
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # If requirements changed
python manage.py migrate  # If database changes
python manage.py collectstatic --noinput  # If static files changed
```

Then reload your web app in the PythonAnywhere dashboard.

## Custom Domain Setup

1. In Web app configuration, add your domain to `ALLOWED_HOSTS` in `.env`
2. Configure DNS to point to PythonAnywhere's IP
3. Add domain in PythonAnywhere's Web app settings

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `.env` file not in git repository
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] Admin password is strong

