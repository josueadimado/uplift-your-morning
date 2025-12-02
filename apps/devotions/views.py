"""
Views for devotions and devotion series.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Devotion, DevotionSeries


class DevotionListView(ListView):
    """
    Display a list of all published devotions.
    """
    model = Devotion
    template_name = 'devotions/list.html'
    context_object_name = 'devotions'
    paginate_by = 10

    def get_queryset(self):
        """
        Get only published devotions, ordered by publish date (newest first).
        """
        queryset = Devotion.objects.filter(is_published=True)
        
        # Filter by series if provided
        series_slug = self.request.GET.get('series')
        if series_slug:
            queryset = queryset.filter(series__slug=series_slug)

            # When viewing a specific series (e.g., 40 Days of Prayer),
            # only show devotions for the current calendar year so that
            # each year's campaign has its own clean list.
            today = timezone.now().date()
            queryset = queryset.filter(publish_date__year=today.year)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                body__icontains=search
            ) | queryset.filter(
                scripture_reference__icontains=search
            )
        
        return queryset.order_by('-publish_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series_slug = self.request.GET.get('series')
        # When viewing a 40 days series, limit the dropdown to ONLY 40 days series.
        if series_slug and "40-days-of-prayer" in series_slug:
            context['series_list'] = DevotionSeries.objects.filter(
                is_active=True, slug__icontains="40-days-of-prayer"
            )
        else:
            context['series_list'] = DevotionSeries.objects.filter(is_active=True)

        context['current_series'] = series_slug
        context['search_query'] = self.request.GET.get('search', '')

        # Provide the full series object (if any) so templates can show
        # series-specific banners and information such as date range.
        if series_slug:
            current_series = DevotionSeries.objects.filter(slug=series_slug).first()
            context['current_series_obj'] = current_series

            # Helper flag: treat any slug that contains "40-days-of-prayer"
            # as a 40 Days of Prayer campaign (e.g. "40-days-of-prayer-2025").
            context['is_40_days_series'] = (
                current_series is not None
                and "40-days-of-prayer" in current_series.slug
            )
        else:
            context['current_series_obj'] = None
            context['is_40_days_series'] = False
        return context


class TodayDevotionView(DetailView):
    """
    Display today's devotion.
    """
    model = Devotion
    template_name = 'devotions/today.html'
    context_object_name = 'devotion'

    def get(self, request, *args, **kwargs):
        """
        Only show a devotion if it is published for TODAY.
        If there is no devotion with today's date, the page will show the
        "no devotion available" message instead of falling back.
        """
        today = timezone.now().date()
        devotion = Devotion.objects.filter(
            publish_date=today,
            is_published=True
        ).order_by('-created_at').first()

        # This can be None if nothing is scheduled for today; the template
        # already handles the `{% if devotion %} ... {% else %}` case.
        self.object = devotion
        # Ensure the template always has a "devotion" variable (can be None)
        context = self.get_context_data(object=self.object, devotion=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Monthly theme/banner: use a published devotion from the current month
        today = timezone.now().date()
        month_theme_devotion = Devotion.objects.filter(
            publish_date__year=today.year,
            publish_date__month=today.month,
            is_published=True,
        ).order_by("publish_date").first()
        context["month_theme_devotion"] = month_theme_devotion

        # Increment view count when devotion is viewed
        if self.object:
            self.object.view_count += 1
            self.object.save(update_fields=['view_count'])

        # Determine if we are currently in the live devotion window
        # Devotion happens 5:00am – 5:30am Ghana time (Africa/Accra)
        import zoneinfo

        accra_tz = zoneinfo.ZoneInfo("Africa/Accra")
        now_accra = timezone.now().astimezone(accra_tz)

        # Build today's live window in Accra time
        live_start = now_accra.replace(hour=5, minute=0, second=0, microsecond=0)
        live_end = now_accra.replace(hour=5, minute=30, second=0, microsecond=0)

        is_live_time = live_start <= now_accra <= live_end

        context["is_live_time"] = is_live_time
        # Zoom link is only shown during live time; YouTube and Facebook are always available
        context["show_zoom_link"] = is_live_time

        return context


class DevotionDetailView(DetailView):
    """
    Display a single devotion in detail.
    """
    model = Devotion
    template_name = 'devotions/detail.html'
    context_object_name = 'devotion'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """
        Only show published devotions.
        """
        return Devotion.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Increment view count when devotion is viewed
        if self.object:
            self.object.view_count += 1
            self.object.save(update_fields=['view_count'])
        
        # Get related devotions (same series or recent ones)
        if self.object.series:
            context['related_devotions'] = Devotion.objects.filter(
                series=self.object.series,
                is_published=True
            ).exclude(id=self.object.id)[:3]
        else:
            context['related_devotions'] = Devotion.objects.filter(
                is_published=True
            ).exclude(id=self.object.id)[:3]
        
        return context


class DevotionSeriesDetailView(DetailView):
    """
    Display a devotion series with all its devotions.
    """
    model = DevotionSeries
    template_name = 'devotions/series_detail.html'
    context_object_name = 'series'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all published devotions in this series
        context['devotions'] = self.object.devotions.filter(
            is_published=True
        ).order_by('publish_date')
        return context
