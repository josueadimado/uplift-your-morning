"""
API views for devotions.
These views provide JSON responses for API requests.
"""
from rest_framework import generics
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import Devotion, DevotionSeries
from .serializers import DevotionSerializer, DevotionSeriesSerializer


class TodayDevotionAPIView(generics.RetrieveAPIView):
    """
    API endpoint to get today's devotion.
    GET /api/devotions/today/
    """
    serializer_class = DevotionSerializer

    def get_object(self):
        """
        Get today's published devotion, or the most recent one if none exists for today.
        """
        today = timezone.now().date()
        devotion = Devotion.objects.filter(
            publish_date=today,
            is_published=True
        ).order_by('-created_at').first()
        
        if not devotion:
            # If no devotion for today, get the most recent one
            devotion = Devotion.objects.filter(
                is_published=True
            ).order_by('-publish_date').first()
        
        return devotion


class DevotionListAPIView(generics.ListAPIView):
    """
    API endpoint to list all published devotions.
    GET /api/devotions/
    Supports filtering by date, series, and search.
    """
    serializer_class = DevotionSerializer

    def get_queryset(self):
        """
        Get devotions with optional filtering.
        """
        queryset = Devotion.objects.filter(is_published=True)
        
        # Filter by date
        date = self.request.query_params.get('date', None)
        if date:
            try:
                date_obj = parse_date(date)
                queryset = queryset.filter(publish_date=date_obj)
            except (ValueError, TypeError):
                pass
        
        # Filter by series
        series_slug = self.request.query_params.get('series', None)
        if series_slug:
            queryset = queryset.filter(series__slug=series_slug)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                body__icontains=search
            ) | queryset.filter(
                scripture_reference__icontains=search
            )
        
        return queryset.order_by('-publish_date')


class DevotionDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint to get a single devotion by slug.
    GET /api/devotions/{slug}/
    """
    serializer_class = DevotionSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        """
        Only return published devotions.
        """
        return Devotion.objects.filter(is_published=True)


class DevotionSeriesListAPIView(generics.ListAPIView):
    """
    API endpoint to list all active devotion series.
    GET /api/devotions/series/
    """
    serializer_class = DevotionSeriesSerializer
    queryset = DevotionSeries.objects.filter(is_active=True)


class DevotionSeriesDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint to get a single devotion series by slug.
    GET /api/devotions/series/{slug}/
    """
    serializer_class = DevotionSeriesSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    queryset = DevotionSeries.objects.all()

