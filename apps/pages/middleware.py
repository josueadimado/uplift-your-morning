"""
Middleware to track page views for analytics.
Optimized with rate limiting and caching to prevent performance issues.
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
import hashlib

# Lazy import to avoid issues during Django startup
try:
    from .models import PageView
except (ImportError, RuntimeError):
    PageView = None


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Tracks page views for analytics purposes.
    Only tracks public pages (not admin pages).
    Uses rate limiting to prevent database overload.
    """
    # Paths to exclude from tracking
    EXCLUDED_PATHS = [
        '/admin/',
        '/manage/',
        '/static/',
        '/media/',
        '/api/',
    ]
    
    # Page name mapping for common paths
    PAGE_NAMES = {
        '/': 'Home',
        '/devotions/': 'Devotions List',
        '/events/': 'Events List',
        '/resources/': 'Resources List',
        '/community/prayer-request/': 'Prayer Request Form',
        '/community/testimony/': 'Testimony Form',
        '/subscriptions/subscribe/': 'Subscribe',
        '/counseling/': 'Counseling Booking',
        '/about/': 'About',
    }
    
    # Rate limiting: only track once per IP+path per 5 minutes
    RATE_LIMIT_SECONDS = 300  # 5 minutes
    
    def process_response(self, request, response):
        """
        Track page view after response is generated.
        Only track successful GET requests to public pages.
        Uses rate limiting to prevent performance issues.
        """
        # Early exit if PageView model is not available (e.g., during migrations)
        if PageView is None:
            return response
        
        # Check if analytics is enabled
        if not getattr(settings, 'ENABLE_ANALYTICS', True):
            return response
        
        # Only track GET requests with successful responses
        if request.method != 'GET' or response.status_code != 200:
            return response
        
        # Skip excluded paths
        path = request.path
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            return response
        
        # Skip if user is staff/admin (internal traffic)
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return response
        
        # Rate limiting: Check if we've tracked this IP+path recently
        ip_address = self.get_client_ip(request)
        cache_key = self._get_cache_key(ip_address, path)
        
        # Check cache - if exists, skip tracking (already tracked recently)
        if cache.get(cache_key):
            return response
        
        # Get page name from mapping or use path
        page_name = self.PAGE_NAMES.get(path, '')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get referer
        referer = request.META.get('HTTP_REFERER', '')
        
        # Create page view record asynchronously (non-blocking)
        # Use a try-except to ensure it never blocks the response
        try:
            # Set cache to prevent duplicate tracking for RATE_LIMIT_SECONDS
            cache.set(cache_key, True, self.RATE_LIMIT_SECONDS)
            
            # Create the record (this is still synchronous but rate-limited)
            PageView.objects.create(
                path=path,
                page_name=page_name,
                ip_address=ip_address,
                user_agent=user_agent[:500],  # Limit length
                referer=referer[:500] if referer else '',  # Limit length
            )
        except Exception:
            # Silently fail if there's any error (don't break the site)
            # Remove cache key if creation failed so it can retry
            cache.delete(cache_key)
            pass
        
        return response
    
    def _get_cache_key(self, ip_address, path):
        """Generate a unique cache key for rate limiting."""
        # Create a hash of IP + path for the cache key
        key_string = f"analytics:{ip_address}:{path}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

