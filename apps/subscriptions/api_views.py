"""
API views for subscriptions.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Subscriber
from .serializers import SubscribeSerializer, UnsubscribeSerializer


class SubscribeAPIView(generics.CreateAPIView):
    """
    API endpoint to subscribe for daily devotions.
    POST /api/subscriptions/subscribe/
    """
    serializer_class = SubscribeSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle subscription creation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        channel = data['channel']
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        receive_daily = data.get('receive_daily_devotion', True)
        receive_special = data.get('receive_special_programs', True)

        if channel == Subscriber.CHANNEL_EMAIL:
            # Normalize email (lowercase)
            email = email.lower()
            
            # Check if already subscribed (active)
            existing_subscriber = Subscriber.objects.filter(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL,
                is_active=True
            ).first()
            
            if existing_subscriber:
                return Response(
                    {'error': 'This email address is already subscribed. If you want to update your preferences, please contact us or unsubscribe first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if exists but inactive (reactivate)
            inactive_subscriber = Subscriber.objects.filter(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL,
                is_active=False
            ).first()
            
            if inactive_subscriber:
                # Reactivate and update preferences
                inactive_subscriber.is_active = True
                inactive_subscriber.receive_daily_devotion = receive_daily
                inactive_subscriber.receive_special_programs = receive_special
                inactive_subscriber.save()
                message = 'Your subscription has been reactivated! You will receive daily devotions via email.'
            else:
                # Create new subscriber
                Subscriber.objects.create(
                    email=email,
                    channel=Subscriber.CHANNEL_EMAIL,
                    receive_daily_devotion=receive_daily,
                    receive_special_programs=receive_special,
                    is_active=True
                )
                message = 'Successfully subscribed via email!'
        
        elif channel == Subscriber.CHANNEL_WHATSAPP:
            # Normalize phone number (remove spaces and common separators)
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Check if already subscribed (active)
            existing_subscriber = Subscriber.objects.filter(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=True
            ).first()
            
            if existing_subscriber:
                return Response(
                    {'error': 'This phone number is already subscribed. If you want to update your preferences, please contact us or unsubscribe first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if exists but inactive (reactivate)
            inactive_subscriber = Subscriber.objects.filter(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP,
                is_active=False
            ).first()
            
            if inactive_subscriber:
                # Reactivate and update preferences
                inactive_subscriber.is_active = True
                inactive_subscriber.receive_daily_devotion = receive_daily
                inactive_subscriber.receive_special_programs = receive_special
                inactive_subscriber.save()
                message = 'Your subscription has been reactivated! You will receive daily devotions via WhatsApp.'
            else:
                # Create new subscriber
                Subscriber.objects.create(
                    phone=phone,
                    channel=Subscriber.CHANNEL_WHATSAPP,
                    receive_daily_devotion=receive_daily,
                    receive_special_programs=receive_special,
                    is_active=True
                )
                message = 'Successfully subscribed via WhatsApp!'

        return Response({'message': message}, status=status.HTTP_201_CREATED)


class UnsubscribeAPIView(generics.CreateAPIView):
    """
    API endpoint to unsubscribe.
    POST /api/subscriptions/unsubscribe/
    """
    serializer_class = UnsubscribeSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle unsubscribe requests.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()

        if email:
            subscriber = Subscriber.objects.filter(
                email=email,
                channel=Subscriber.CHANNEL_EMAIL
            ).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.save()
                return Response({'message': 'Successfully unsubscribed from email notifications.'}, 
                             status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Email address not found.'}, 
                             status=status.HTTP_404_NOT_FOUND)
        
        elif phone:
            subscriber = Subscriber.objects.filter(
                phone=phone,
                channel=Subscriber.CHANNEL_WHATSAPP
            ).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.save()
                return Response({'message': 'Successfully unsubscribed from WhatsApp notifications.'}, 
                             status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Phone number not found.'}, 
                             status=status.HTTP_404_NOT_FOUND)

