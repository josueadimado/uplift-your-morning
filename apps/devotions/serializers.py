"""
Serializers for devotions API.
Serializers convert Django models to JSON format for API responses.
"""
from rest_framework import serializers
from .models import Devotion, DevotionSeries


class DevotionSeriesSerializer(serializers.ModelSerializer):
    """
    Serializer for DevotionSeries model.
    Converts DevotionSeries objects to JSON.
    """
    class Meta:
        model = DevotionSeries
        fields = ['id', 'title', 'slug', 'description', 'start_date', 'end_date', 'is_active']


class DevotionSerializer(serializers.ModelSerializer):
    """
    Serializer for Devotion model.
    Includes series information in the response.
    """
    series = DevotionSeriesSerializer(read_only=True)
    
    class Meta:
        model = Devotion
        fields = [
            'id', 'title', 'slug', 'series', 'theme', 'topic',
            'scripture_reference', 'passage_text', 'body', 'quote',
            'reflection', 'prayer', 'action_point', 'publish_date',
            'audio_file', 'pdf_file', 'featured', 'view_count'
        ]

