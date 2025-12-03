"""
Custom admin management views for staff users.
These views allow staff to manage content without needing full Django admin access.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.conf import settings
import requests
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Q

from apps.devotions.models import Devotion, DevotionSeries
from apps.events.models import Event
from apps.resources.models import Resource, ResourceCategory
from apps.community.models import PrayerRequest, Testimony
from apps.pages.models import Donation, FortyDaysConfig


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

