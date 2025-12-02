"""
Serializers for community API.
"""
from rest_framework import serializers
from .models import PrayerRequest, Testimony


class PrayerRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for prayer requests.
    """
    class Meta:
        model = PrayerRequest
        fields = ['id', 'name', 'email', 'request', 'is_public', 'created_at']
        read_only_fields = ['created_at']


class TestimonySerializer(serializers.ModelSerializer):
    """
    Serializer for testimonies.
    """
    class Meta:
        model = Testimony
        fields = ['id', 'name', 'country', 'testimony', 'is_approved', 'featured', 'created_at']
        read_only_fields = ['is_approved', 'featured', 'created_at']


class TestimonyListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing approved testimonies (public view).
    """
    class Meta:
        model = Testimony
        fields = ['id', 'name', 'country', 'testimony', 'featured', 'created_at']
        read_only_fields = ['featured', 'created_at']

