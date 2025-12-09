"""
Views for static pages like Home, About, Contact, etc.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.urls import reverse_lazy
import requests
from .models import ContactMessage, Donation, FortyDaysConfig, SiteSettings, CounselingBooking, PageView
from .forms import CounselingBookingForm
from apps.devotions.models import Devotion
from apps.events.models import Event
from apps.resources.models import Resource
from apps.community.models import Testimony, PrayerRequest
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta


class HomeView(TemplateView):
    """
    Home page view that displays:
    - Today's devotion
    - Upcoming events
    - Featured resources
    - Featured testimonies
    """
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get today's devotion (optimized query)
        from django.utils import timezone
        import zoneinfo
        today = timezone.now().date()
        context['todays_devotion'] = Devotion.objects.filter(
            publish_date=today,
            is_published=True
        ).select_related('series').first()
        
        # Get upcoming events (next 3) - optimized query
        context['upcoming_events'] = Event.objects.filter(
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:3]
        
        # Get featured resources - optimized query
        context['featured_resources'] = Resource.objects.filter(
            is_featured=True
        ).select_related('category')[:3]
        
        # Get featured testimonies - optimized query
        context['featured_testimonies'] = Testimony.objects.filter(
            is_approved=True,
            featured=True
        ).only('id', 'title', 'content', 'author_name', 'author_location', 'created_at')[:5]
        
        # Check if we're in the active 40 Days period
        forty_days_config = FortyDaysConfig.objects.filter(is_active=True).first()
        context['is_40_days_active'] = False
        context['forty_days_config'] = None
        
        if forty_days_config:
            # Check if today is within the date range
            if forty_days_config.start_date <= today <= forty_days_config.end_date:
                context['is_40_days_active'] = True
                context['forty_days_config'] = forty_days_config
                
                # Calculate current day number (Day 1 = start_date)
                days_elapsed = (today - forty_days_config.start_date).days + 1
                context['forty_days_current_day'] = days_elapsed
                context['forty_days_total_days'] = (forty_days_config.end_date - forty_days_config.start_date).days + 1
                
                # Check if we're in the live time windows (Ghana time)
                # Live buttons appear 15 minutes before session starts
                accra_tz = zoneinfo.ZoneInfo("Africa/Accra")
                now_accra = timezone.now().astimezone(accra_tz)
                from datetime import timedelta
                
                # Morning session: 5:00-5:30am (live buttons from 4:45am)
                morning_start = now_accra.replace(hour=5, minute=0, second=0, microsecond=0)
                morning_live_start = morning_start - timedelta(minutes=15)  # 15 min before
                morning_end = now_accra.replace(hour=5, minute=30, second=0, microsecond=0)
                context['is_morning_live'] = morning_live_start <= now_accra <= morning_end
                
                # Evening session: 6:00-7:00pm (live buttons from 5:45pm)
                evening_start = now_accra.replace(hour=18, minute=0, second=0, microsecond=0)
                evening_live_start = evening_start - timedelta(minutes=15)  # 15 min before
                evening_end = now_accra.replace(hour=19, minute=0, second=0, microsecond=0)
                context['is_evening_live'] = evening_live_start <= now_accra <= evening_end
                
                # Calculate next session time for countdown
                current_hour = now_accra.hour
                current_minute = now_accra.minute
                
                # Determine next session (considering 15 min early start)
                if now_accra < morning_live_start:
                    # Before morning session (before 4:45am) - next is morning
                    next_session = morning_live_start
                    context['next_session_type'] = 'morning'
                    context['next_session_time'] = '4:45 AM'
                elif now_accra < evening_live_start:
                    # After morning, before evening (before 5:45pm) - next is evening
                    next_session = evening_live_start
                    context['next_session_type'] = 'evening'
                    context['next_session_time'] = '5:45 PM'
                else:
                    # After evening - next is tomorrow's morning
                    next_morning_live = (now_accra + timedelta(days=1)).replace(hour=4, minute=45, second=0, microsecond=0)
                    next_session = next_morning_live
                    context['next_session_type'] = 'morning'
                    context['next_session_time'] = '4:45 AM (Tomorrow)'
                
                # Calculate time until next session (in seconds for JavaScript countdown)
                time_until = (next_session - now_accra).total_seconds()
                context['next_session_timestamp'] = int(time_until)
        
        # Add timezone information for all sections (always available)
        # GMT = same as Ghana time (Africa/Accra)
        # CAT (Central Africa Time) = GMT + 2
        # EAT (East Africa Time) = GMT + 3
        context['morning_time_gmt'] = '5:00 AM'
        context['morning_time_cat'] = '7:00 AM'
        context['morning_time_eat'] = '8:00 AM'
        context['evening_time_gmt'] = '6:00 PM'
        context['evening_time_cat'] = '8:00 PM'
        context['evening_time_eat'] = '9:00 PM'
        
        # Get site settings (Zoom link for all programs)
        site_settings, _ = SiteSettings.objects.get_or_create(pk=1)
        zoom_link = site_settings.zoom_link
        context['global_zoom_link'] = zoom_link
        
        # Time-based logic for showing Zoom buttons
        accra_tz = zoneinfo.ZoneInfo("Africa/Accra")
        now_accra = timezone.now().astimezone(accra_tz)
        current_weekday = now_accra.weekday()  # 0=Monday, 6=Sunday
        
        # Uplift Your Morning: 5:00-5:30am GMT (Monday-Sunday, all days)
        morning_start = now_accra.replace(hour=5, minute=0, second=0, microsecond=0)
        morning_end = now_accra.replace(hour=5, minute=30, second=0, microsecond=0)
        context['show_uplift_zoom'] = (morning_start <= now_accra <= morning_end) and bool(zoom_link)
        
        # Access Hour: 6:00-7:00pm GMT (Wednesday only, weekday=2)
        evening_start = now_accra.replace(hour=18, minute=0, second=0, microsecond=0)
        evening_end = now_accra.replace(hour=19, minute=0, second=0, microsecond=0)
        context['show_access_hour_zoom'] = (current_weekday == 2) and (evening_start <= now_accra <= evening_end) and bool(zoom_link)
        
        # Edify: 6:00-7:00pm GMT (Friday only, weekday=4)
        context['show_edify_zoom'] = (current_weekday == 4) and (evening_start <= now_accra <= evening_end) and bool(zoom_link)
        
        # For 40 Days, Zoom should only show during live sessions (already handled above)
        # We'll use the existing is_morning_live and is_evening_live flags
        
        return context


class AboutView(TemplateView):
    """
    About page view.
    """
    template_name = 'pages/about.html'


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Simple internal dashboard for admins/staff to see key stats and quick links.
    This is separate from Django's built-in /admin/ interface.
    """
    template_name = 'pages/admin_dashboard.html'

    def test_func(self):
        # Only allow staff/superusers to see this dashboard
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tell the base template that we're in the admin area
        context['hide_main_nav'] = True

        # Devotions
        total_devotions = Devotion.objects.count()
        published_devotions = Devotion.objects.filter(is_published=True).count()

        # Events
        now = timezone.now()
        upcoming_events = Event.objects.filter(start_datetime__gte=now).count()
        past_events = Event.objects.filter(start_datetime__lt=now).count()

        # Resources
        total_resources = Resource.objects.count()

        # Community (prayers and testimonies)
        total_prayer_requests = PrayerRequest.objects.count()
        open_prayer_requests = PrayerRequest.objects.filter(is_prayed_for=False).count()
        total_testimonies = Testimony.objects.count()
        pending_testimonies = Testimony.objects.filter(is_approved=False).count()

        # Donations
        total_donations = Donation.objects.count()
        successful_donations = Donation.objects.filter(status=Donation.STATUS_SUCCESS)
        successful_donations_count = successful_donations.count()
        successful_donations_total = successful_donations.aggregate(
            total=Sum('amount_ghs')
        )['total'] or 0
        # Also get pending and failed counts for completeness
        pending_donations_count = Donation.objects.filter(status=Donation.STATUS_PENDING).count()
        failed_donations_count = Donation.objects.filter(status=Donation.STATUS_FAILED).count()

        # Counseling Bookings
        total_counseling_bookings = CounselingBooking.objects.count()
        pending_counseling = CounselingBooking.objects.filter(status=CounselingBooking.STATUS_PENDING).count()
        approved_counseling = CounselingBooking.objects.filter(status=CounselingBooking.STATUS_APPROVED).count()
        completed_counseling = CounselingBooking.objects.filter(status=CounselingBooking.STATUS_COMPLETED).count()

        # Analytics - Page Views (optimized queries)
        # Handle case where PageView table doesn't exist yet (migrations not run)
        try:
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            # For "this week" - use 6 days ago to today (7 days total) to match the chart
            week_start = today_start - timedelta(days=6)
            month_start = today_start - timedelta(days=30)
            
            # Use single query with aggregation for better performance
            total_page_views = PageView.objects.count()
            
            # Optimize: Use single query with date filtering for all counts
            page_views_today = PageView.objects.filter(created_at__gte=today_start).count()
            page_views_week = PageView.objects.filter(created_at__gte=week_start).count()
            page_views_month = PageView.objects.filter(created_at__gte=month_start).count()
            
            # Most viewed pages (last 30 days) - optimized with limit
            most_viewed_pages = list(PageView.objects.filter(
                created_at__gte=month_start
            ).values('path', 'page_name').annotate(
                view_count=Count('id')
            ).order_by('-view_count')[:10])
            
            # Page views by day (last 7 days) for chart
            # Optimized: Use database aggregation for better performance
            from django.db.models import Count as CountFunc
            
            daily_views_data = PageView.objects.filter(
                created_at__gte=week_start
            ).annotate(
                day=TruncDate('created_at')
            ).values('day').annotate(
                count=CountFunc('id')
            ).order_by('day')
            
            # Convert to dictionary for easy lookup
            daily_counts = {item['day']: item['count'] for item in daily_views_data}
            
            # Build daily_views list with all 7 days (from 6 days ago to today)
            # This matches the week_start date range exactly
            daily_views = []
            for i in range(7):
                day_start = today_start - timedelta(days=6-i)  # Start from 6 days ago (i=0) to today (i=6)
                day_date = day_start.date()
                count = daily_counts.get(day_date, 0)
                daily_views.append({
                    'date': day_start.strftime('%b %d'),
                    'count': count
                })
            
            # Calculate the total for the chart (should match page_views_week)
            # This ensures the bar heights are calculated correctly
            chart_total = sum(day['count'] for day in daily_views)
        except Exception:
            # If PageView table doesn't exist or any error occurs, use empty defaults
            total_page_views = 0
            page_views_today = 0
            page_views_week = 0
            page_views_month = 0
            most_viewed_pages = []
            daily_views = []
            chart_total = 0

        # Recent activity
        context['recent_devotions'] = Devotion.objects.order_by('-created_at')[:5]
        context['recent_events'] = Event.objects.order_by('-created_at')[:5]
        context['recent_prayers'] = PrayerRequest.objects.order_by('-created_at')[:5]
        # Show all donations to ensure nothing is missed
        context['recent_donations'] = Donation.objects.all().order_by('-created_at')
        context['recent_counseling'] = CounselingBooking.objects.order_by('-created_at')[:5]

        context['stats'] = {
            'devotions': {
                'total': total_devotions,
                'published': published_devotions,
            },
            'events': {
                'upcoming': upcoming_events,
                'past': past_events,
            },
            'resources': {
                'total': total_resources,
            },
            'community': {
                'prayer_total': total_prayer_requests,
                'prayer_open': open_prayer_requests,
                'testimony_total': total_testimonies,
                'testimony_pending': pending_testimonies,
            },
            'donations': {
                'total': total_donations,
                'successful_count': successful_donations_count,
                'successful_total': successful_donations_total,
                'pending_count': pending_donations_count,
                'failed_count': failed_donations_count,
            },
            'counseling': {
                'total': total_counseling_bookings,
                'pending': pending_counseling,
                'approved': approved_counseling,
                'completed': completed_counseling,
            },
            'analytics': {
                'total_views': total_page_views,
                'views_today': page_views_today,
                'views_week': page_views_week,
                'views_month': page_views_month,
                'most_viewed': most_viewed_pages,
                'daily_views': daily_views,
                'chart_total': chart_total,  # Total for chart calculation (matches the 7 days shown)
            },
        }

        return context


class AdminLoginView(LoginView):
    """Custom admin login view with nice UI."""
    template_name = 'admin/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect to dashboard after login
        next_url = self.request.GET.get('next', '')
        if next_url:
            return next_url
        return reverse_lazy('pages:admin_dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


class AdminLogoutView(LogoutView):
    """Custom admin logout view."""
    next_page = reverse_lazy('pages:home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class DonationView(TemplateView):
    """
    Donation page (formerly Contact) which explains giving options.
    """
    template_name = 'pages/contact.html'


class DonationCheckoutView(View):
    """
    Initialize a Paystack payment and redirect the user to Paystack checkout.
    Uses PAYSTACK_PUBLIC_KEY and PAYSTACK_SECRET_KEY from settings.
    """

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        reference = request.POST.get('reference', '').strip()
        amount_ghs = request.POST.get('amount', '').strip()

        if not (name and email and amount_ghs):
            messages.error(request, 'Please provide your name, email and an amount.')
            return redirect('pages:donate')

        try:
            amount_pesewas = int(float(amount_ghs) * 100)
        except ValueError:
            messages.error(request, 'Please enter a valid amount.')
            return redirect('pages:donate')

        paystack_secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        paystack_public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')

        if not paystack_secret_key or not paystack_public_key:
            messages.error(request, 'Payment configuration is missing. Please contact the site administrator.')
            return redirect('pages:donate')

        # Build callback URL (where Paystack redirects after payment)
        callback_url = request.build_absolute_uri('/donate/thanks/')

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': email,
            'amount': amount_pesewas,
            'currency': 'GHS',
            'callback_url': callback_url,
            'metadata': {
                'custom_fields': [
                    {
                        'display_name': 'Donor Name',
                        'variable_name': 'donor_name',
                        'value': name,
                    }
                ]
            },
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize',
                                     json=data, headers=headers, timeout=30)
            response_data = response.json()
        except Exception:
            messages.error(request, 'Unable to connect to payment service. Please try again later.')
            return redirect('pages:donate')

        if response.status_code == 200 and response_data.get('status'):
            init_data = response_data.get('data', {})
            auth_url = init_data.get('authorization_url')
            paystack_ref = init_data.get('reference')

            if not (auth_url and paystack_ref):
                messages.error(request, 'Payment initialisation failed. Please try again.')
                return redirect('pages:donate')

            # Record pending donation in our database
            Donation.objects.create(
                name=name,
                email=email,
                amount_ghs=amount_ghs,
                paystack_reference=paystack_ref,
                status=Donation.STATUS_PENDING,
                note=reference or '',
                raw_response=init_data,
            )

            return redirect(auth_url)

        messages.error(request, 'Could not start payment. Please try again later.')
        return redirect('pages:donate')


class DonationThanksView(TemplateView):
    """
    Thank-you page after Paystack redirects back.
    Verifies the transaction and updates the Donation record.
    """
    template_name = 'pages/donation_thanks.html'

    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference')
        if not reference:
            messages.error(request, 'No payment reference supplied.')
            return super().get(request, *args, **kwargs)

        paystack_secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        if not paystack_secret_key:
            messages.error(request, 'Payment configuration is missing.')
            return super().get(request, *args, **kwargs)

        # Look up existing donation
        try:
            donation = Donation.objects.get(paystack_reference=reference)
        except Donation.DoesNotExist:
            donation = None

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
        }

        try:
            verify_resp = requests.get(
                f'https://api.paystack.co/transaction/verify/{reference}',
                headers=headers,
                timeout=30
            )
            verify_data = verify_resp.json()
        except Exception:
            messages.error(request, 'Could not verify payment at this time.')
            return super().get(request, *args, **kwargs)

        status_ok = verify_data.get('status') and verify_data.get('data', {}).get('status') == 'success'

        if donation:
            donation.raw_response = verify_data.get('data')
            if status_ok:
                donation.status = Donation.STATUS_SUCCESS
            else:
                donation.status = Donation.STATUS_FAILED
            donation.save(update_fields=['status', 'raw_response', 'updated_at'])

        if not status_ok:
            messages.error(request, 'Your payment could not be confirmed. If money was deducted, please contact support.')
        else:
            messages.success(request, 'Your donation has been received successfully. Thank you!')

        return super().get(request, *args, **kwargs)


class CounselingBookingView(TemplateView):
    """
    View for users to submit counseling booking requests.
    """
    template_name = 'pages/counseling_booking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CounselingBookingForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CounselingBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = CounselingBooking.STATUS_PENDING
            booking.save()
            messages.success(
                request,
                'Your counseling booking request has been submitted successfully! '
                'You will receive an email and SMS once it is approved.'
            )
            return redirect('pages:counseling_booking')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)