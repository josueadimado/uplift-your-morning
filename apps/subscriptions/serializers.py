"""
Serializers for subscriptions API.
"""
from rest_framework import serializers
from .models import Subscriber


class SubscribeSerializer(serializers.Serializer):
    """
    Serializer for subscription requests.
    Validates subscription form data.
    """
    channel = serializers.ChoiceField(choices=Subscriber.CHANNEL_CHOICES)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    receive_daily_devotion = serializers.BooleanField(default=True)
    receive_special_programs = serializers.BooleanField(default=True)

    def validate(self, data):
        """
        Ensure either email or phone is provided based on channel.
        """
        channel = data.get('channel')
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()

        if channel == Subscriber.CHANNEL_EMAIL and not email:
            raise serializers.ValidationError("Email is required for email subscriptions.")
        
        if channel == Subscriber.CHANNEL_SMS and not phone:
            raise serializers.ValidationError("Phone number is required for SMS subscriptions.")
        
        if channel == Subscriber.CHANNEL_WHATSAPP and not phone:
            raise serializers.ValidationError("Phone number is required for WhatsApp subscriptions.")
        
        return data


class UnsubscribeSerializer(serializers.Serializer):
    """
    Serializer for unsubscribe requests.
    """
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=50)

    def validate(self, data):
        """
        Ensure either email or phone is provided.
        """
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()

        if not email and not phone:
            raise serializers.ValidationError("Either email or phone number is required.")
        
        return data

