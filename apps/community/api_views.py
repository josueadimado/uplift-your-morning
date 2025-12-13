"""
API views for community features.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from .models import PrayerRequest, Testimony
from .serializers import PrayerRequestSerializer, TestimonySerializer, TestimonyListSerializer
from .notifications import send_prayer_request_notification, send_testimony_notification


class PrayerRequestCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to submit prayer requests.
    POST /api/community/prayer-requests/
    """
    serializer_class = PrayerRequestSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a prayer request and send notification.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prayer_request = serializer.save()
        # Send email notification to admin
        try:
            send_prayer_request_notification(prayer_request)
        except Exception:
            # Don't break the submission if notification fails
            pass
        return Response(
            {'message': 'Thank you for sharing your prayer request. We will be praying for you!'},
            status=status.HTTP_201_CREATED
        )


class TestimonyCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to submit testimonies.
    POST /api/community/testimonies/
    """
    serializer_class = TestimonySerializer

    def create(self, request, *args, **kwargs):
        """
        Create a testimony (needs admin approval) and send notification.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Testimonies need approval, so is_approved defaults to False
        testimony = serializer.save(is_approved=False)
        # Send email notification to admin
        try:
            send_testimony_notification(testimony)
        except Exception:
            # Don't break the submission if notification fails
            pass
        return Response(
            {'message': 'Thank you for sharing your testimony! It will be reviewed and published soon.'},
            status=status.HTTP_201_CREATED
        )


class TestimonyListAPIView(generics.ListAPIView):
    """
    API endpoint to list approved testimonies.
    GET /api/community/testimonies/
    """
    serializer_class = TestimonyListSerializer
    queryset = Testimony.objects.filter(
        is_approved=True,
        is_public=True
    ).order_by('-created_at')

