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
from .models import (
    ContactMessage, Donation, FortyDaysConfig, SiteSettings,
    CounselingBooking, PageView, AttendanceRecord, Question, CoordinatorApplication,
)
from .forms import CounselingBookingForm, QuestionForm, CoordinatorApplicationForm
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
        ).only('id', 'name', 'country', 'testimony', 'created_at')[:5]
        
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

        # Questions (from Submit a Question)
        total_questions = Question.objects.count()
        pending_questions = Question.objects.filter(status=Question.STATUS_PENDING).count()
        answered_questions = Question.objects.filter(status=Question.STATUS_ANSWERED).count()

        # Coordinator Applications (Join the Movement)
        total_coordinator_apps = CoordinatorApplication.objects.count()
        pending_coordinator_apps = CoordinatorApplication.objects.filter(status=CoordinatorApplication.STATUS_PENDING).count()

        # Subscriptions
        from apps.subscriptions.models import Subscriber
        total_subscribers = Subscriber.objects.count()
        active_subscribers = Subscriber.objects.filter(is_active=True).count()
        email_subscribers = Subscriber.objects.filter(channel=Subscriber.CHANNEL_EMAIL, is_active=True).count()
        whatsapp_subscribers = Subscriber.objects.filter(channel=Subscriber.CHANNEL_WHATSAPP, is_active=True).count()
        daily_devotion_subscribers = Subscriber.objects.filter(is_active=True, receive_daily_devotion=True).count()
        special_programs_subscribers = Subscriber.objects.filter(is_active=True, receive_special_programs=True).count()
        recent_subscribers = Subscriber.objects.order_by('-created_at')[:5]
        # Get recent subscribers for the dashboard list (limit to 10 most recent)
        all_subscribers = Subscriber.objects.order_by('-created_at')[:10]

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
        context['recent_questions'] = Question.objects.order_by('-created_at')[:5]
        context['recent_coordinator_apps'] = CoordinatorApplication.objects.order_by('-created_at')[:5]
        context['recent_subscribers'] = recent_subscribers
        context['all_subscribers'] = all_subscribers

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
            'questions': {
                'total': total_questions,
                'pending': pending_questions,
                'answered': answered_questions,
            },
            'coordinator_apps': {
                'total': total_coordinator_apps,
                'pending': pending_coordinator_apps,
            },
            'subscriptions': {
                'total': total_subscribers,
                'active': active_subscribers,
                'email': email_subscribers,
                'whatsapp': whatsapp_subscribers,
                'daily_devotion': daily_devotion_subscribers,
                'special_programs': special_programs_subscribers,
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
            from decimal import Decimal, InvalidOperation
            amount_ghs_decimal = Decimal(amount_ghs)
            amount_pesewas = int(amount_ghs_decimal * 100)
        except (ValueError, InvalidOperation):
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
                amount_ghs=amount_ghs_decimal,
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
            # Send email notification to admin
            from .notifications import send_booking_submission_notification
            try:
                send_booking_submission_notification(booking)
            except Exception:
                # Don't break the submission if notification fails
                pass
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


class PledgeFormView(TemplateView):
    """
    View for users to submit pledge commitments.
    """
    template_name = 'pages/pledge_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .forms import PledgeForm
        context['form'] = PledgeForm()
        return context
    
    def post(self, request, *args, **kwargs):
        from .forms import PledgeForm
        from .models import Pledge
        
        form = PledgeForm(request.POST)
        if form.is_valid():
            pledge = form.save(commit=False)
            # Set default pledge type based on what fields are filled
            if not pledge.pledge_type:
                if pledge.amount:
                    pledge.pledge_type = Pledge.PLEDGE_TYPE_MONETARY
                elif pledge.non_monetary_description:
                    pledge.pledge_type = Pledge.PLEDGE_TYPE_NON_MONETARY
                else:
                    pledge.pledge_type = Pledge.PLEDGE_TYPE_MONETARY  # Default
            pledge.status = Pledge.STATUS_PENDING
            pledge.save()
            # Send email notification to admin
            from .notifications import send_pledge_submission_notification
            try:
                send_pledge_submission_notification(pledge)
            except Exception:
                # Don't break the submission if notification fails
                pass
            messages.success(
                request,
                'Thank you for your pledge commitment! Your information has been received and we will be in touch soon.'
            )
            return redirect('pages:pledge_form')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)


class QuestionSubmitView(TemplateView):
    """
    View for visitors to submit questions by topic (Edify, Access Hour, Uplift Your Morning, General, Other).
    Staff can reply in the admin.
    """
    template_name = 'pages/question_submit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QuestionForm()
        return context

    def post(self, request, *args, **kwargs):
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.status = Question.STATUS_PENDING
            question.save()
            from .notifications import send_question_submission_notification
            try:
                send_question_submission_notification(question)
            except Exception:
                pass
            messages.success(
                request,
                'Thank you! Your question has been submitted. We will reply based on the topic you selected.'
            )
            return redirect('pages:question_submit')
        messages.error(request, 'Please correct the errors below.')
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class CoordinatorApplicationView(TemplateView):
    """
    Apply as UPLIFT Campus Coordinator (Student Movement) or UPLIFT Professional Coordinator (Professional Forum).
    """
    template_name = 'pages/coordinator_application.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CoordinatorApplicationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CoordinatorApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.status = CoordinatorApplication.STATUS_PENDING
            application.save()
            from .notifications import send_coordinator_application_notification
            try:
                send_coordinator_application_notification(application)
            except Exception:
                pass
            messages.success(
                request,
                'Thank you! Your application has been submitted. We will review it and be in touch. You can also reach us on WhatsApp: +233 57 912 4333.'
            )
            return redirect('pages:coordinator_application')
        messages.error(request, 'Please correct the errors below.')
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class AttendanceAnalyticsPublicView(TemplateView):
    """
    Public view for attendance analytics - accessible to team without login.
    Mobile-friendly with responsive charts.
    Requires access code for security.
    """
    template_name = 'pages/attendance_analytics.html'
    access_code_template = 'pages/attendance_analytics_access.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check access code before allowing access."""
        from django.conf import settings
        from django.contrib import messages
        
        # Check if access code is provided in session or query parameter
        access_code = request.GET.get('code', '')
        session_code = request.session.get('attendance_analytics_authenticated', False)
        
        # Get the required access code from settings
        required_code = getattr(settings, 'ATTENDANCE_ANALYTICS_CODE', 'uplift2024')
        
        # If code is provided in URL, validate it
        if access_code:
            if access_code == required_code:
                # Store in session for future visits
                request.session['attendance_analytics_authenticated'] = True
                request.session.set_expiry(86400 * 7)  # 7 days
                messages.success(request, 'Access granted! You can now view the analytics.')
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.error(request, 'Invalid access code. Please try again.')
                return render(request, self.access_code_template, {
                    'error': 'Invalid access code. Please try again.'
                })
        
        # Check if already authenticated via session
        if session_code:
            return super().dispatch(request, *args, **kwargs)
        
        # Show access code form
        return render(request, self.access_code_template)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import json
        from datetime import datetime, timedelta
        
        # Get date range from query params (default to last 30 days)
        date_to = self.request.GET.get('date_to')
        date_from = self.request.GET.get('date_from')
        
        if not date_to:
            date_to = datetime.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        # Get records in date range
        records = AttendanceRecord.objects.filter(
            date__gte=date_from,
            date__lte=date_to
        ).order_by('date')
        
        # Prepare data for charts
        dates = [r.date.strftime('%Y-%m-%d') for r in records]
        youtube_views = [r.youtube_views for r in records]
        facebook_views = [r.facebook_views for r in records]
        total_views = [r.get_total_views() for r in records]
        
        # Convert to JSON for JavaScript
        dates_json = json.dumps(dates)
        youtube_views_json = json.dumps(youtube_views)
        facebook_views_json = json.dumps(facebook_views)
        total_views_json = json.dumps(total_views)
        
        # Calculate statistics
        total_youtube = sum(youtube_views)
        total_facebook = sum(facebook_views)
        total_all = sum(total_views)
        
        avg_youtube = total_youtube / len(records) if records else 0
        avg_facebook = total_facebook / len(records) if records else 0
        avg_total = total_all / len(records) if records else 0
        
        # Find peak days
        peak_day = None
        peak_views = 0
        for r in records:
            total = r.get_total_views()
            if total > peak_views:
                peak_views = total
                peak_day = r
        
        # Weekly aggregates
        weekly_data = {}
        for r in records:
            week_start = r.date - timedelta(days=r.date.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'youtube': 0,
                    'facebook': 0,
                    'total': 0,
                    'count': 0
                }
            weekly_data[week_key]['youtube'] += r.youtube_views
            weekly_data[week_key]['facebook'] += r.facebook_views
            weekly_data[week_key]['total'] += r.get_total_views()
            weekly_data[week_key]['count'] += 1
        
        weekly_dates = sorted(weekly_data.keys())
        weekly_youtube = [weekly_data[w]['youtube'] for w in weekly_dates]
        weekly_facebook = [weekly_data[w]['facebook'] for w in weekly_dates]
        weekly_total = [weekly_data[w]['total'] for w in weekly_dates]
        
        # Convert weekly data to JSON
        weekly_dates_json = json.dumps(weekly_dates)
        weekly_youtube_json = json.dumps(weekly_youtube)
        weekly_facebook_json = json.dumps(weekly_facebook)
        weekly_total_json = json.dumps(weekly_total)
        
        context.update({
            'records': records,
            'dates': dates_json,
            'youtube_views': youtube_views_json,
            'facebook_views': facebook_views_json,
            'total_views': total_views_json,
            'weekly_dates': weekly_dates_json,
            'weekly_youtube': weekly_youtube_json,
            'weekly_facebook': weekly_facebook_json,
            'weekly_total': weekly_total_json,
            'total_youtube': total_youtube,
            'total_facebook': total_facebook,
            'total_all': total_all,
            'avg_youtube': round(avg_youtube, 2),
            'avg_facebook': round(avg_facebook, 2),
            'avg_total': round(avg_total, 2),
            'peak_day': peak_day,
            'peak_views': peak_views,
            'date_from': date_from.strftime('%Y-%m-%d'),
            'date_to': date_to.strftime('%Y-%m-%d'),
            'num_days': (date_to - date_from).days + 1,
        })
        return context