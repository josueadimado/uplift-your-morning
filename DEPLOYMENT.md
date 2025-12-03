# Deployment Guide - PythonAnywhere

This guide will help you deploy Uplift Your Morning to PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account (free or paid)
2. Your code pushed to GitHub
3. Your domain name (if using custom domain)

## Step 1: Prepare Your Code

### 1.0 Important: Python Version
**PythonAnywhere requires Python 3.10.** Make sure you don't commit your local `venv` folder (it's already in `.gitignore`). You'll create a new virtualenv on PythonAnywhere with Python 3.10.

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

**IMPORTANT:** PythonAnywhere requires Python 3.10. Do NOT use Python 3.13 or other versions.

```bash
# Remove the old venv if it exists (it has wrong Python version)
rm -rf venv

# Create new virtualenv with Python 3.10
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you cloned from GitHub and the venv folder was included, you MUST delete it and create a new one on PythonAnywhere with Python 3.10.

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
3. Click "Add a new web app" (if you don't have one yet)
4. Choose "Manual configuration"
5. Select Python version (3.10 recommended)

**IMPORTANT:** If you see a "Coming Soon!" page when visiting your domain, it means:
- The web app doesn't exist yet, OR
- The web app exists but your custom domain isn't added to it

### 4.2 Add Your Custom Domain

After creating the web app, you MUST add your custom domain:

1. In the Web app configuration page, find the "Domains" section
2. Add both domains:
   - `upliftyourmorning.com`
   - `www.upliftyourmorning.com`
3. Click "Save" or the domain will be added automatically
4. Make sure your DNS is configured correctly (see Custom Domain Setup section)

### 4.2 WSGI Configuration

1. Click on your web app
2. Click "WSGI configuration file" link (it should be `/var/www/upliftyourmorning_com_wsgi.py`)
3. Replace the content with:

```python
import os
import sys

# Add your project directory to the path
path = '/home/josueadimado/uplift-your-morning'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'uplift_afrika.settings'

# Activate virtual environment (Python 3.10 compatible method)
activate_venv = os.path.expanduser('/home/josueadimado/uplift-your-morning/venv/bin/activate_this.py')
if os.path.exists(activate_venv):
    exec(open(activate_venv).read(), {'__file__': activate_venv})
else:
    # Fallback: add venv site-packages to path
    venv_site_packages = '/home/josueadimado/uplift-your-morning/venv/lib/python3.10/site-packages'
    if venv_site_packages not in sys.path:
        sys.path.insert(0, venv_site_packages)

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Note:** This configuration is already set for your username. If you need to change it, replace `josueadimado` with your actual username.

### 4.3 Static Files Mapping

In the Web app configuration:

1. Go to "Static files" section
2. Add static files mapping:
   - URL: `/static/`
   - Directory: `/home/josueadimado/uplift-your-morning/staticfiles/`
   - Click "Add" or "Save"

3. **IMPORTANT:** Add media files mapping (for user uploads):
   - URL: `/media/`
   - Directory: `/home/josueadimado/uplift-your-morning/media/`
   - Click "Add" or "Save"

**Note:** Make sure you've run `python manage.py collectstatic` to create the `staticfiles` directory.

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

1. In Web app configuration, add your domain to `ALLOWED_HOSTS` in `.env`:
   ```
   ALLOWED_HOSTS=yourusername.pythonanywhere.com,upliftyourmorning.com,www.upliftyourmorning.com
   ```

2. Add your domain in PythonAnywhere's Web app settings:
   - Go to Web app configuration
   - Add `upliftyourmorning.com` and `www.upliftyourmorning.com` to the domain list

3. Configure DNS records in your domain registrar:
   
   **For the root domain (`upliftyourmorning.com`):**
   - **Option A (Recommended if supported):** Add a CNAME record:
     - Type: `CNAME`
     - Host/Name: `@` (or leave blank, depending on your DNS provider)
     - Value: `webapp-2858903.pythonanywhere.com.` (note the trailing dot)
     - TTL: Automatic
   
   - **Option B (If CNAME not allowed on root):** Some DNS providers don't allow CNAME on root domain. In this case:
     - Use an A record pointing to PythonAnywhere's IP (check PythonAnywhere docs for current IP)
     - OR set up a redirect from root to www in your DNS provider
   
   **For the www subdomain (`www.upliftyourmorning.com`):**
   - Type: `CNAME`
   - Host/Name: `www`
   - Value: `webapp-2858903.pythonanywhere.com.` (note the trailing dot)
   - TTL: Automatic

4. Wait for DNS propagation (can take up to 24-48 hours)

5. Reload your web app in PythonAnywhere dashboard

**Note:** If your DNS provider doesn't support CNAME on the root domain (@), you may need to:
- Use A records instead (check PythonAnywhere documentation for IP addresses)
- Or set up a redirect from root domain to www subdomain

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `.env` file not in git repository
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] Admin password is strong

