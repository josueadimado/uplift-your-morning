"""
Custom admin management views for staff users.
These views allow staff to manage content without needing full Django admin access.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.conf import settings
import requests
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Q

from apps.devotions.models import Devotion, DevotionSeries
from django.http import JsonResponse
import json
from apps.events.models import Event
from apps.resources.models import Resource, ResourceCategory
from apps.community.models import PrayerRequest, Testimony
from apps.pages.models import Donation, FortyDaysConfig, SiteSettings, CounselingBooking
from apps.subscriptions.models import Subscriber, ScheduledNotification


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only staff users can access these views."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        """
        Add a flag so the base template knows we're in the admin area.
        This lets us hide the public top navigation/footer.
        """
        context = super().get_context_data(**kwargs)
        context['hide_main_nav'] = True
        return context


# ==================== DEVOTIONS ====================

class DevotionListView(StaffRequiredMixin, ListView):
    """List all devotions with filters."""
    model = Devotion
    template_name = 'admin/devotions/list.html'
    context_object_name = 'devotions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Devotion.objects.all()
        # Filter by published status
        status = self.request.GET.get('status')
        if status == 'published':
            queryset = queryset.filter(is_published=True)
        elif status == 'draft':
            queryset = queryset.filter(is_published=False)
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search) |
                Q(topic__icontains=search)
            )
        return queryset.order_by('-publish_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Devotion.objects.count()
        context['published_count'] = Devotion.objects.filter(is_published=True).count()
        context['draft_count'] = Devotion.objects.filter(is_published=False).count()
        return context


class DevotionCreateView(StaffRequiredMixin, CreateView):
    """Create a new devotion."""
    model = Devotion
    template_name = 'admin/devotions/form.html'
    fields = [
        'title', 'series', 'theme', 'topic', 'scripture_reference', 'passage_text',
        'body', 'quote', 'reflection', 'prayer', 'action_point', 'publish_date',
        'is_published', 'image', 'audio_file', 'pdf_file', 'featured'
    ]
    success_url = reverse_lazy('manage:devotions_list')

    def get_initial(self):
        """
        Prefill publish date to today and default to published.
        """
        from django.utils import timezone
        initial = super().get_initial()
        initial.update({
            'publish_date': timezone.localdate(),
            'is_published': True,
        })
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Devotion created successfully!')
        return super().form_valid(form)


class DevotionUpdateView(StaffRequiredMixin, UpdateView):
    """Edit an existing devotion."""
    model = Devotion
    template_name = 'admin/devotions/form.html'
    fields = [
        'title', 'series', 'theme', 'topic', 'scripture_reference', 'passage_text',
        'body', 'quote', 'reflection', 'prayer', 'action_point', 'publish_date',
        'is_published', 'image', 'audio_file', 'pdf_file', 'featured'
    ]
    success_url = reverse_lazy('manage:devotions_list')

    def form_valid(self, form):
        messages.success(self.request, 'Devotion updated successfully!')
        return super().form_valid(form)


class DevotionDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a devotion."""
    model = Devotion
    template_name = 'admin/devotions/delete.html'
    success_url = reverse_lazy('manage:devotions_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Devotion deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== EVENTS ====================

class EventListView(StaffRequiredMixin, ListView):
    """List all events."""
    model = Event
    template_name = 'admin/events/list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        queryset = Event.objects.all()
        # Filter by upcoming/past
        filter_type = self.request.GET.get('filter')
        now = timezone.now()
        if filter_type == 'upcoming':
            queryset = queryset.filter(start_datetime__gte=now)
        elif filter_type == 'past':
            queryset = queryset.filter(start_datetime__lt=now)
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        return queryset.order_by('-start_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['total'] = Event.objects.count()
        context['upcoming_count'] = Event.objects.filter(start_datetime__gte=now).count()
        context['past_count'] = Event.objects.filter(start_datetime__lt=now).count()
        return context


class EventCreateView(StaffRequiredMixin, CreateView):
    """Create a new event."""
    model = Event
    template_name = 'admin/events/form.html'
    fields = [
        'title', 'description', 'start_datetime', 'end_datetime', 'location',
        'is_online', 'poster_image', 'livestream_url', 'youtube_url',
        'facebook_url', 'zoom_url', 'registration_open'
    ]
    success_url = reverse_lazy('manage:events_list')

    def form_valid(self, form):
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)


class EventUpdateView(StaffRequiredMixin, UpdateView):
    """Edit an existing event."""
    model = Event
    template_name = 'admin/events/form.html'
    fields = [
        'title', 'description', 'start_datetime', 'end_datetime', 'location',
        'is_online', 'poster_image', 'livestream_url', 'youtube_url',
        'facebook_url', 'zoom_url', 'registration_open'
    ]
    success_url = reverse_lazy('manage:events_list')

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)


class EventDeleteView(StaffRequiredMixin, DeleteView):
    """Delete an event."""
    model = Event
    template_name = 'admin/events/delete.html'
    success_url = reverse_lazy('manage:events_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== RESOURCES ====================

class ResourceListView(StaffRequiredMixin, ListView):
    """List all resources."""
    model = Resource
    template_name = 'admin/resources/list.html'
    context_object_name = 'resources'
    paginate_by = 20

    def get_queryset(self):
        queryset = Resource.objects.all()
        # Filter by type
        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(type=resource_type)
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Resource.objects.count()
        return context


class ResourceCreateView(StaffRequiredMixin, CreateView):
    """Create a new resource."""
    model = Resource
    template_name = 'admin/resources/form.html'
    fields = ['title', 'category', 'type', 'description', 'file', 'external_url', 'is_featured']
    success_url = reverse_lazy('manage:resources_list')

    def form_valid(self, form):
        messages.success(self.request, 'Resource created successfully!')
        return super().form_valid(form)


class ResourceUpdateView(StaffRequiredMixin, UpdateView):
    """Edit an existing resource."""
    model = Resource
    template_name = 'admin/resources/form.html'
    fields = ['title', 'category', 'type', 'description', 'file', 'external_url', 'is_featured']
    success_url = reverse_lazy('manage:resources_list')

    def form_valid(self, form):
        messages.success(self.request, 'Resource updated successfully!')
        return super().form_valid(form)


class ResourceDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a resource."""
    model = Resource
    template_name = 'admin/resources/delete.html'
    success_url = reverse_lazy('manage:resources_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Resource deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== RESOURCE CATEGORIES ====================

class ResourceCategoryListView(StaffRequiredMixin, ListView):
    """List all resource categories."""
    model = ResourceCategory
    template_name = 'admin/resources/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        queryset = ResourceCategory.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = ResourceCategory.objects.count()
        return context


class ResourceCategoryCreateView(StaffRequiredMixin, CreateView):
    """Create a new resource category."""
    model = ResourceCategory
    template_name = 'admin/resources/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('manage:resource_categories_list')

    def form_valid(self, form):
        messages.success(self.request, 'Resource category created successfully!')
        return super().form_valid(form)


class ResourceCategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Update a resource category."""
    model = ResourceCategory
    template_name = 'admin/resources/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('manage:resource_categories_list')

    def form_valid(self, form):
        messages.success(self.request, 'Resource category updated successfully!')
        return super().form_valid(form)


class ResourceCategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a resource category."""
    model = ResourceCategory
    template_name = 'admin/resources/category_delete.html'
    success_url = reverse_lazy('manage:resource_categories_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Resource category deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== PRAYER REQUESTS ====================

class PrayerRequestListView(StaffRequiredMixin, ListView):
    """List all prayer requests."""
    model = PrayerRequest
    template_name = 'admin/prayers/list.html'
    context_object_name = 'prayers'
    paginate_by = 20

    def get_queryset(self):
        queryset = PrayerRequest.objects.all()
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'open':
            queryset = queryset.filter(is_prayed_for=False)
        elif status == 'prayed':
            queryset = queryset.filter(is_prayed_for=True)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = PrayerRequest.objects.count()
        context['open_count'] = PrayerRequest.objects.filter(is_prayed_for=False).count()
        context['prayed_count'] = PrayerRequest.objects.filter(is_prayed_for=True).count()
        return context


class PrayerRequestMarkPrayedView(StaffRequiredMixin, View):
    """Mark a prayer request as prayed for."""
    def post(self, request, *args, **kwargs):
        try:
            prayer = PrayerRequest.objects.get(pk=kwargs['pk'])
            prayer.is_prayed_for = True
            prayer.save()
            messages.success(request, 'Prayer request marked as prayed for!')
        except PrayerRequest.DoesNotExist:
            messages.error(request, 'Prayer request not found.')
        return redirect('manage:prayers_list')


class PrayerRequestDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a prayer request."""
    model = PrayerRequest
    template_name = 'admin/prayers/delete.html'
    success_url = reverse_lazy('manage:prayers_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Prayer request deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== DONATIONS ====================

class DonationListView(StaffRequiredMixin, ListView):
    """List all donations."""
    model = Donation
    template_name = 'admin/donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20

    def get_queryset(self):
        queryset = Donation.objects.all()
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(paystack_reference__icontains=search)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Donation.objects.count()
        context['successful'] = Donation.objects.filter(status=Donation.STATUS_SUCCESS)
        context['successful_count'] = context['successful'].count()
        context['successful_total'] = context['successful'].aggregate(
            total=Sum('amount_ghs')
        )['total'] or 0
        context['pending_count'] = Donation.objects.filter(status=Donation.STATUS_PENDING).count()
        context['failed_count'] = Donation.objects.filter(status=Donation.STATUS_FAILED).count()
        return context


class DonationVerifyView(StaffRequiredMixin, View):
    """Manually verify a donation with Paystack."""
    def post(self, request, *args, **kwargs):
        try:
            donation = Donation.objects.get(pk=kwargs['pk'])
        except Donation.DoesNotExist:
            messages.error(request, 'Donation not found.')
            return redirect('manage:donations_list')

        paystack_secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        if not paystack_secret_key:
            messages.error(request, 'Payment configuration is missing.')
            return redirect('manage:donations_list')

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
        }

        try:
            verify_resp = requests.get(
                f'https://api.paystack.co/transaction/verify/{donation.paystack_reference}',
                headers=headers,
                timeout=30
            )
            verify_data = verify_resp.json()
        except Exception as e:
            messages.error(request, f'Could not verify payment: {str(e)}')
            return redirect('manage:donations_list')

        # Check if the API call was successful
        if verify_resp.status_code != 200:
            messages.error(request, f'Paystack API error: {verify_data.get("message", "Unknown error")}')
            return redirect('manage:donations_list')

        # Check transaction status
        transaction_data = verify_data.get('data', {})
        transaction_status = transaction_data.get('status')
        
        donation.raw_response = transaction_data
        
        if transaction_status == 'success':
            donation.status = Donation.STATUS_SUCCESS
            messages.success(request, f'Donation verified successfully! Status updated to Successful. Amount: GHS {donation.amount_ghs}')
        elif transaction_status in ['failed', 'reversed', 'insufficient_funds']:
            donation.status = Donation.STATUS_FAILED
            messages.warning(request, f'Payment verification shows status: {transaction_status}. Status updated to Failed.')
        else:
            # Still pending or other status
            messages.info(request, f'Payment status is still: {transaction_status}. Donation remains as Pending.')
        
        donation.save(update_fields=['status', 'raw_response', 'updated_at'])

        return redirect('manage:donations_list')


class DonationDetailView(StaffRequiredMixin, DetailView):
    """View donation details."""
    model = Donation
    template_name = 'admin/donations/detail.html'
    context_object_name = 'donation'


# ==================== TESTIMONIES ====================

class TestimonyListView(StaffRequiredMixin, ListView):
    """List all testimonies."""
    model = Testimony
    template_name = 'admin/testimonies/list.html'
    context_object_name = 'testimonies'
    paginate_by = 20

    def get_queryset(self):
        queryset = Testimony.objects.all()
        # Filter by approval status
        status = self.request.GET.get('status')
        if status == 'approved':
            queryset = queryset.filter(is_approved=True)
        elif status == 'pending':
            queryset = queryset.filter(is_approved=False)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Testimony.objects.count()
        context['approved_count'] = Testimony.objects.filter(is_approved=True).count()
        context['pending_count'] = Testimony.objects.filter(is_approved=False).count()
        return context


class TestimonyApproveView(StaffRequiredMixin, View):
    """Approve a testimony."""
    def post(self, request, *args, **kwargs):
        try:
            testimony = Testimony.objects.get(pk=kwargs['pk'])
            testimony.is_approved = True
            testimony.save()
            messages.success(request, 'Testimony approved!')
        except Testimony.DoesNotExist:
            messages.error(request, 'Testimony not found.')
        return redirect('manage:testimonies_list')


class TestimonyDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a testimony."""
    model = Testimony
    template_name = 'admin/testimonies/delete.html'
    success_url = reverse_lazy('manage:testimonies_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Testimony deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== 40 DAYS CONFIGURATION ====================

class FortyDaysConfigListView(StaffRequiredMixin, ListView):
    """List all 40 Days configurations."""
    model = FortyDaysConfig
    template_name = 'admin/fortydays/list.html'
    context_object_name = 'configs'
    paginate_by = 20

    def get_queryset(self):
        queryset = FortyDaysConfig.objects.all()
        # Filter by active status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        return queryset.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = FortyDaysConfig.objects.count()
        context['active_count'] = FortyDaysConfig.objects.filter(is_active=True).count()
        context['inactive_count'] = FortyDaysConfig.objects.filter(is_active=False).count()
        return context


class FortyDaysConfigCreateView(StaffRequiredMixin, CreateView):
    """Create a new 40 Days configuration."""
    model = FortyDaysConfig
    template_name = 'admin/fortydays/form.html'
    fields = [
        'start_date', 'end_date', 'is_active', 'banner_image',
        'morning_youtube_url', 'morning_facebook_url',
        'evening_youtube_url', 'evening_facebook_url'
    ]
    success_url = reverse_lazy('manage:fortydays_list')

    def form_valid(self, form):
        messages.success(self.request, '40 Days configuration created successfully!')
        return super().form_valid(form)


class FortyDaysConfigUpdateView(StaffRequiredMixin, UpdateView):
    """Update a 40 Days configuration."""
    model = FortyDaysConfig
    template_name = 'admin/fortydays/form.html'
    fields = [
        'start_date', 'end_date', 'is_active', 'banner_image',
        'morning_youtube_url', 'morning_facebook_url',
        'evening_youtube_url', 'evening_facebook_url'
    ]
    success_url = reverse_lazy('manage:fortydays_list')

    def form_valid(self, form):
        # Save the form (this handles image upload if present)
        response = super().form_valid(form)
        messages.success(self.request, '40 Days configuration updated successfully!')
        return response


class FortyDaysConfigDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a 40 Days configuration."""
    model = FortyDaysConfig
    template_name = 'admin/fortydays/delete.html'
    success_url = reverse_lazy('manage:fortydays_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '40 Days configuration deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== SITE SETTINGS ====================

class SiteSettingsUpdateView(StaffRequiredMixin, UpdateView):
    """Update site settings (singleton model)."""
    model = SiteSettings
    template_name = 'admin/sitesettings/form.html'
    fields = ['zoom_link']
    success_url = reverse_lazy('manage:sitesettings_edit')

    def get_object(self, queryset=None):
        # Get or create the singleton instance
        obj, created = SiteSettings.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Site settings updated successfully!')
        return super().form_valid(form)


# ==================== COUNSELING BOOKINGS ====================

from .notifications import send_booking_approval_notifications, create_google_calendar_event

class CounselingBookingListView(StaffRequiredMixin, ListView):
    """List all counseling bookings."""
    model = CounselingBooking
    template_name = 'admin/counseling/list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = CounselingBooking.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                full_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                phone__icontains=search
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = CounselingBooking.objects.count()
        context['pending'] = CounselingBooking.objects.filter(status=CounselingBooking.STATUS_PENDING).count()
        context['approved'] = CounselingBooking.objects.filter(status=CounselingBooking.STATUS_APPROVED).count()
        return context


class CounselingBookingDetailView(StaffRequiredMixin, DetailView):
    """View details of a counseling booking."""
    model = CounselingBooking
    template_name = 'admin/counseling/detail.html'
    context_object_name = 'booking'


# ==================== SUBSCRIBERS ====================

class SubscriberListView(StaffRequiredMixin, ListView):
    """List all subscribers with filters and search."""
    model = Subscriber
    template_name = 'admin/subscribers/list.html'
    context_object_name = 'subscribers'
    paginate_by = 30

    def get_queryset(self):
        queryset = Subscriber.objects.all()
        
        # Filter by channel
        channel = self.request.GET.get('channel')
        if channel:
            queryset = queryset.filter(channel=channel)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filter by preferences
        preference = self.request.GET.get('preference')
        if preference == 'daily':
            queryset = queryset.filter(receive_daily_devotion=True, is_active=True)
        elif preference == 'special':
            queryset = queryset.filter(receive_special_programs=True, is_active=True)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Subscriber.objects.count()
        context['active_count'] = Subscriber.objects.filter(is_active=True).count()
        context['inactive_count'] = Subscriber.objects.filter(is_active=False).count()
        context['email_count'] = Subscriber.objects.filter(channel=Subscriber.CHANNEL_EMAIL, is_active=True).count()
        context['whatsapp_count'] = Subscriber.objects.filter(channel=Subscriber.CHANNEL_WHATSAPP, is_active=True).count()
        context['daily_devotion_count'] = Subscriber.objects.filter(is_active=True, receive_daily_devotion=True).count()
        context['special_programs_count'] = Subscriber.objects.filter(is_active=True, receive_special_programs=True).count()
        return context


class SubscriberActivateView(StaffRequiredMixin, View):
    """Activate a subscriber."""
    def post(self, request, pk):
        subscriber = get_object_or_404(Subscriber, pk=pk)
        subscriber.is_active = True
        subscriber.save()
        messages.success(request, f'Subscriber activated: {subscriber.email or subscriber.phone}')
        return redirect('manage:subscribers_list')


class SubscriberDeactivateView(StaffRequiredMixin, View):
    """Deactivate a subscriber."""
    def post(self, request, pk):
        subscriber = get_object_or_404(Subscriber, pk=pk)
        subscriber.is_active = False
        subscriber.save()
        messages.success(request, f'Subscriber deactivated: {subscriber.email or subscriber.phone}')
        return redirect('manage:subscribers_list')


class SubscriberDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a subscriber."""
    model = Subscriber
    template_name = 'admin/subscribers/delete.html'
    success_url = reverse_lazy('manage:subscribers_list')
    
    def delete(self, request, *args, **kwargs):
        subscriber = self.get_object()
        messages.success(request, f'Subscriber deleted: {subscriber.email or subscriber.phone}')
        return super().delete(request, *args, **kwargs)


# ==================== NOTIFICATIONS ====================

class NotificationScheduleListView(StaffRequiredMixin, ListView):
    """List all scheduled notifications."""
    model = ScheduledNotification
    template_name = 'admin/notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        queryset = ScheduledNotification.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-scheduled_date', '-scheduled_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = ScheduledNotification.objects.count()
        context['scheduled'] = ScheduledNotification.objects.filter(status=ScheduledNotification.STATUS_SCHEDULED, is_paused=False).count()
        context['paused'] = ScheduledNotification.objects.filter(is_paused=True).count()
        context['sent'] = ScheduledNotification.objects.filter(status=ScheduledNotification.STATUS_SENT).count()
        return context


class NotificationScheduleCreateView(StaffRequiredMixin, CreateView):
    """Create a new scheduled notification."""
    model = ScheduledNotification
    template_name = 'admin/notifications/form.html'
    fields = [
        'title', 'devotion', 'custom_message', 'scheduled_date', 'scheduled_time',
        'send_to_email', 'send_to_whatsapp', 'only_daily_devotion_subscribers', 'notes'
    ]
    success_url = reverse_lazy('manage:notifications_list')

    def get_initial(self):
        """Set default values for the form."""
        from datetime import date, time
        from django.utils import timezone
        
        # Get today's date
        today = date.today()
        
        # Default time: 5:00 AM
        default_time = time(5, 0)
        
        return {
            'title': 'Daily Devotion - Uplift Your Morning',
            'scheduled_date': today,
            'scheduled_time': default_time,
            'send_to_email': True,
            'send_to_whatsapp': True,
            'only_daily_devotion_subscribers': True,
        }

    def form_valid(self, form):
        messages.success(self.request, 'Notification scheduled successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get today's devotion for preview
        from datetime import date
        from apps.devotions.models import Devotion
        try:
            today_devotion = Devotion.objects.filter(
                is_published=True,
                publish_date=date.today()
            ).first()
            context['today_devotion'] = today_devotion
        except:
            context['today_devotion'] = None
        return context


class NotificationScheduleDetailView(StaffRequiredMixin, DetailView):
    """View details and preview of a scheduled notification."""
    model = ScheduledNotification
    template_name = 'admin/notifications/detail.html'
    context_object_name = 'notification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notification = self.get_object()
        
        # Build preview messages
        from apps.subscriptions.management.commands.send_daily_devotions import Command as DevotionCommand
        command = DevotionCommand()
        
        # Get the devotion to use
        devotion = notification.devotion
        if not devotion:
            from datetime import date
            from apps.devotions.models import Devotion
            devotion = Devotion.objects.filter(
                is_published=True,
                publish_date=notification.scheduled_date
            ).first()
        
        # Build email preview with subject
        if devotion:
            email_subject = f'{notification.title} - {devotion.title}'
            email_preview = command._build_devotion_email(devotion)
            if notification.custom_message:
                email_preview += f"\n\n{notification.custom_message}"
            sms_preview = command._build_devotion_sms(devotion)
            if notification.custom_message:
                sms_preview += f"\n\n{notification.custom_message[:100]}..."  # Truncate for SMS
            has_devotion = True
        else:
            email_subject = notification.title
            email_preview = command._build_no_devotion_email()
            if notification.custom_message:
                email_preview += f"\n\n{notification.custom_message}"
            sms_preview = command._build_no_devotion_sms()
            if notification.custom_message:
                sms_preview += f"\n\n{notification.custom_message[:100]}..."
            has_devotion = False
        
        context['email_subject'] = email_subject
        context['email_preview'] = email_preview
        context['sms_preview'] = sms_preview
        context['devotion'] = devotion
        context['has_devotion'] = has_devotion
        
        # Get recipient counts
        from apps.subscriptions.models import Subscriber
        email_count = 0
        whatsapp_count = 0
        
        if notification.send_to_email:
            email_qs = Subscriber.objects.filter(
                channel=Subscriber.CHANNEL_EMAIL,
                is_active=True,
                email__isnull=False
            ).exclude(email='')
            if notification.only_daily_devotion_subscribers:
                email_qs = email_qs.filter(receive_daily_devotion=True)
            email_count = email_qs.count()
        
        if notification.send_to_whatsapp:
            whatsapp_qs = Subscriber.objects.filter(
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=True,
                phone__isnull=False
            ).exclude(phone='')
            if notification.only_daily_devotion_subscribers:
                whatsapp_qs = whatsapp_qs.filter(receive_daily_devotion=True)
            whatsapp_count = whatsapp_qs.count()
        
        context['email_recipient_count'] = email_count
        context['whatsapp_recipient_count'] = whatsapp_count
        
        return context


class NotificationPauseView(StaffRequiredMixin, View):
    """Pause a scheduled notification."""
    def post(self, request, pk):
        notification = get_object_or_404(ScheduledNotification, pk=pk)
        notification.pause()
        messages.success(request, f'Notification "{notification.title}" has been paused.')
        return redirect('manage:notifications_detail', pk=pk)


class NotificationResumeView(StaffRequiredMixin, View):
    """Resume a paused notification."""
    def post(self, request, pk):
        notification = get_object_or_404(ScheduledNotification, pk=pk)
        notification.resume()
        messages.success(request, f'Notification "{notification.title}" has been resumed.')
        return redirect('manage:notifications_detail', pk=pk)


class NotificationDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a scheduled notification."""
    model = ScheduledNotification
    template_name = 'admin/notifications/delete.html'
    success_url = reverse_lazy('manage:notifications_list')
    
    def delete(self, request, *args, **kwargs):
        notification = self.get_object()
        messages.success(request, f'Notification "{notification.title}" has been deleted.')
        return super().delete(request, *args, **kwargs)


class CounselingBookingApproveView(StaffRequiredMixin, View):
    """Approve a counseling booking and send notifications."""
    def post(self, request, pk):
        booking = get_object_or_404(CounselingBooking, pk=pk)
        
        if booking.status != CounselingBooking.STATUS_PENDING:
            messages.error(request, 'Only pending bookings can be approved.')
            return redirect('manage:counseling_detail', pk=pk)
        
        # Update booking status
        booking.status = CounselingBooking.STATUS_APPROVED
        if not booking.approved_date:
            booking.approved_date = booking.preferred_date
        if not booking.approved_time:
            booking.approved_time = booking.preferred_time
        booking.save()
        
        # Send notifications (email and SMS)
        try:
            send_booking_approval_notifications(booking)
            messages.success(request, f'Booking approved and notifications sent to {booking.email}')
        except Exception as e:
            messages.warning(request, f'Booking approved but notifications failed: {str(e)}')
        
        # Create Google Calendar event
        try:
            create_google_calendar_event(booking)
            messages.success(request, 'Google Calendar event created successfully.')
        except Exception as e:
            messages.warning(request, f'Google Calendar event creation failed: {str(e)}')
        
        return redirect('manage:counseling_detail', pk=pk)


class CounselingBookingRejectView(StaffRequiredMixin, View):
    """Reject a counseling booking."""
    def post(self, request, pk):
        booking = get_object_or_404(CounselingBooking, pk=pk)
        
        if booking.status != CounselingBooking.STATUS_PENDING:
            messages.error(request, 'Only pending bookings can be rejected.')
            return redirect('manage:counseling_detail', pk=pk)
        
        booking.status = CounselingBooking.STATUS_REJECTED
        booking.save()
        
        messages.success(request, 'Booking rejected successfully.')
        return redirect('manage:counseling_detail', pk=pk)


# ==================== DEVOTION SERIES AJAX ====================

class DevotionSeriesCreateAjaxView(StaffRequiredMixin, View):
    """Create a new devotion series via AJAX."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            start_date = data.get('start_date') or None
            end_date = data.get('end_date') or None
            
            if not title:
                return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)
            
            # Check if series with this title already exists
            if DevotionSeries.objects.filter(title=title).exists():
                return JsonResponse({'success': False, 'error': 'A series with this title already exists'}, status=400)
            
            # Create the series
            series = DevotionSeries.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'series': {
                    'id': series.id,
                    'title': series.title,
                    'slug': series.slug
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

