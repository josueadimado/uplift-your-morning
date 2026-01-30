"""
Models for static pages like Home, About, Contact, etc.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    """
    Model to store contact form submissions.
    (Kept for historical records, even though the page is now used for donations.)
    """
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class Donation(TimeStampedModel):
    """
    Records donations made via the website.
    We create a record when initializing the Paystack transaction
    and update it after verification on callback.
    """

    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Successful'),
        (STATUS_FAILED, 'Failed'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    amount_ghs = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=200, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    note = models.CharField(max_length=255, blank=True)
    raw_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - GHS {self.amount_ghs} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class SiteSettings(TimeStampedModel):
    """
    Site-wide settings that should only have one instance.
    Stores general configuration like Zoom links used across all programs.
    """
    zoom_link = models.URLField(
        blank=True,
        help_text="Zoom meeting link used for all programs (Uplift Your Morning, Access Hour, Edify, 40 Days)"
    )
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion - just clear the fields instead
        self.zoom_link = ''
        self.save()
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"


class CounselingBooking(TimeStampedModel):
    """
    Model for counseling session bookings.
    Requires admin approval before confirmation.
    """
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # User information
    full_name = models.CharField(max_length=200)
    # Email is optional – some users may only want to share a phone number
    email = models.EmailField(blank=True, null=True)
    # Store phone in international format (e.g. +233201234567)
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=100, blank=True)
    
    # Booking details
    preferred_date = models.DateField(help_text="Preferred date for counseling session")
    preferred_time = models.TimeField(help_text="Preferred time for counseling session")
    duration_minutes = models.IntegerField(default=30, help_text="Session duration in minutes (fixed at 30 minutes)")
    topic = models.CharField(
        max_length=200,
        blank=True,
        help_text="Brief topic or reason for counseling"
    )
    message = models.TextField(
        blank=True,
        help_text="Additional message or details"
    )
    
    # Status and admin fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    approved_date = models.DateField(null=True, blank=True, help_text="Admin-approved date")
    approved_time = models.TimeField(null=True, blank=True, help_text="Admin-approved time")
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    
    # Google Calendar integration
    google_calendar_event_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Google Calendar event ID after creation"
    )
    
    # Notification tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Counseling Booking"
        verbose_name_plural = "Counseling Bookings"
    
    def __str__(self):
        return f"{self.full_name} - {self.preferred_date} ({self.status})"


class Question(TimeStampedModel):
    """
    Questions submitted by visitors, categorized by topic.
    Staff can reply in the admin; replies can be sent to the submitter (e.g. by email).
    """
    CATEGORY_EDIFY = 'edify'
    CATEGORY_ACCESS_HOUR = 'access_hour'
    CATEGORY_UPLIFT_YOUR_MORNING = 'uplift_your_morning'
    CATEGORY_GENERAL = 'general'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_EDIFY, 'Edify'),
        (CATEGORY_ACCESS_HOUR, 'Access Hour'),
        (CATEGORY_UPLIFT_YOUR_MORNING, 'Uplift Your Morning'),
        (CATEGORY_GENERAL, 'General'),
        (CATEGORY_OTHER, 'Other'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_ANSWERED = 'answered'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ANSWERED, 'Answered'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    question = models.TextField(help_text="The question or message from the visitor")

    # Staff reply (filled in via admin)
    reply = models.TextField(blank=True, help_text="Your reply to the question")
    replied_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"{self.name} – {self.get_category_display()} ({self.status})"


class CoordinatorApplication(TimeStampedModel):
    """
    Applications for UPLIFT Student Movement or UPLIFT Professional Forum (Professional Movement).
    """
    TYPE_STUDENT = 'student'
    TYPE_PROFESSIONAL = 'professional'

    TYPE_CHOICES = [
        (TYPE_STUDENT, 'UPLIFT Student Movement'),
        (TYPE_PROFESSIONAL, 'UPLIFT Professional Forum'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_CONTACTED = 'contacted'
    STATUS_INTERVIEWED = 'interviewed'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONTACTED, 'Contacted'),
        (STATUS_INTERVIEWED, 'Interviewed'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
    ]

    application_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200, blank=True, help_text="Country of residence")
    email = models.EmailField()
    phone = models.CharField(max_length=50)

    # Student Movement fields
    campus_name = models.CharField(max_length=255, blank=True, help_text="Name of campus / institution")
    program_of_study = models.CharField(max_length=255, blank=True, help_text="Program or course of study")
    year_of_study = models.CharField(max_length=100, blank=True, help_text="e.g. Year 2, Final year")
    additional_student_info = models.TextField(
        blank=True,
        help_text="Leadership experience, interests, expected graduation, or anything else relevant as a student",
    )

    # Professional Forum fields
    role_or_profession = models.CharField(max_length=255, blank=True, help_text="Job title or profession")
    organisation_name = models.CharField(max_length=255, blank=True, help_text="Employer or organisation name")
    years_experience = models.CharField(max_length=100, blank=True, help_text="e.g. 5 years, 10+")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile (optional)")
    additional_professional_info = models.TextField(
        blank=True,
        help_text="Industry, key skills, career highlights, or anything else relevant to your professional profile",
    )

    # Legacy: kept for backward compatibility; new submissions use campus_name / organisation_name
    campus_or_profession = models.CharField(max_length=255, blank=True)

    profile_message = models.TextField(
        help_text="Why you want to be part of this group and what you hope to gain or contribute",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Movement Application'
        verbose_name_plural = 'Movement Applications'

    def __str__(self):
        return f"{self.name} – {self.get_application_type_display()} ({self.status})"


class FortyDaysConfig(TimeStampedModel):
    """
    Configuration for the annual "40 Days of Prayer, Planning & Planting" event.
    Stores the date range and live streaming URLs for morning and evening sessions.
    Only one active configuration should exist at a time.
    """
    start_date = models.DateField(
        help_text="Start date of the 40 Days event (e.g., November 10, 2025)"
    )
    end_date = models.DateField(
        help_text="End date of the 40 Days event (e.g., December 19, 2025)"
    )
    
    # Banner/Flyer image for the 40 Days section
    banner_image = models.ImageField(
        upload_to='fortydays/banners/',
        blank=True,
        null=True,
        help_text="Banner/flyer image for the 40 Days section on the homepage"
    )
    
    # Morning session (5:00-5:30am Ghana time)
    morning_youtube_url = models.URLField(
        blank=True,
        help_text="YouTube live URL for morning sessions (5:00-5:30am Ghana time)"
    )
    morning_facebook_url = models.URLField(
        blank=True,
        help_text="Facebook live URL for morning sessions (5:00-5:30am Ghana time)"
    )
    
    # Evening session (6:00-7:00pm Ghana time)
    evening_youtube_url = models.URLField(
        blank=True,
        help_text="YouTube live URL for evening sessions (6:00-7:00pm Ghana time)"
    )
    evening_facebook_url = models.URLField(
        blank=True,
        help_text="Facebook live URL for evening sessions (6:00-7:00pm Ghana time)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Set to False to disable this configuration (useful for past years)"
    )
    
    def __str__(self):
        return f"40 Days {self.start_date.year} ({self.start_date} to {self.end_date})"
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "40 Days Configuration"
        verbose_name_plural = "40 Days Configurations"


class PageView(TimeStampedModel):
    """
    Tracks page views for analytics purposes.
    Records each visit to a page on the website.
    """
    path = models.CharField(
        max_length=500,
        help_text="The URL path that was visited (e.g., /devotions/, /events/)"
    )
    page_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Human-readable page name (e.g., 'Home', 'Devotions List')"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the visitor"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent string"
    )
    referer = models.URLField(
        blank=True,
        help_text="The page the user came from (if available)"
    )
    
    def __str__(self):
        return f"{self.page_name or self.path} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['path']),
        ]


class Pledge(TimeStampedModel):
    """
    Model for collecting pledge commitments from supporters.
    Supports both monetary and non-monetary pledges (services, goods, time, etc.).
    """
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # Pledge type choices
    PLEDGE_TYPE_MONETARY = 'monetary'
    PLEDGE_TYPE_NON_MONETARY = 'non_monetary'
    
    PLEDGE_TYPE_CHOICES = [
        (PLEDGE_TYPE_MONETARY, 'Monetary (Money)'),
        (PLEDGE_TYPE_NON_MONETARY, 'Non-Monetary (Services, Goods, Time, etc.)'),
    ]
    
    # Common currency choices
    CURRENCY_GHS = 'GHS'
    CURRENCY_USD = 'USD'
    CURRENCY_GBP = 'GBP'
    CURRENCY_EUR = 'EUR'
    CURRENCY_NGN = 'NGN'
    CURRENCY_ZAR = 'ZAR'
    CURRENCY_OTHER = 'OTHER'
    
    CURRENCY_CHOICES = [
        (CURRENCY_GHS, 'GHS - Ghana Cedis'),
        (CURRENCY_USD, 'USD - US Dollars'),
        (CURRENCY_GBP, 'GBP - British Pounds'),
        (CURRENCY_EUR, 'EUR - Euros'),
        (CURRENCY_NGN, 'NGN - Nigerian Naira'),
        (CURRENCY_ZAR, 'ZAR - South African Rand'),
        (CURRENCY_OTHER, 'Other Currency'),
    ]
    
    # Donation frequency choices
    FREQUENCY_ONETIME = 'one_time'
    FREQUENCY_MONTHLY = 'monthly'
    FREQUENCY_QUARTERLY = 'quarterly'
    FREQUENCY_ANNUALLY = 'annually'
    FREQUENCY_CUSTOM = 'custom'
    
    FREQUENCY_CHOICES = [
        (FREQUENCY_ONETIME, 'One-time'),
        (FREQUENCY_MONTHLY, 'Monthly'),
        (FREQUENCY_QUARTERLY, 'Quarterly (Every 3 months)'),
        (FREQUENCY_ANNUALLY, 'Annually (Once per year)'),
        (FREQUENCY_CUSTOM, 'Custom (Specify below)'),
    ]
    
    # Contact information
    full_name = models.CharField(max_length=200, help_text="Full name of the person making the pledge")
    email = models.EmailField(help_text="Email address for contact")
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Phone number (optional, in international format e.g., +233 20 123 4567)"
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text="Country of residence (optional, ISO 3166-1 alpha-2 code)"
    )
    
    # Contact preferences
    CONTACT_EMAIL = 'email'
    CONTACT_PHONE = 'phone'
    CONTACT_WHATSAPP = 'whatsapp'
    
    CONTACT_METHOD_CHOICES = [
        (CONTACT_EMAIL, 'Email'),
        (CONTACT_PHONE, 'Phone Call'),
        (CONTACT_WHATSAPP, 'WhatsApp'),
    ]
    
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default=CONTACT_EMAIL,
        help_text="Preferred method of contact"
    )
    contact_info = models.CharField(
        max_length=200,
        blank=True,
        help_text="Additional contact information (e.g., WhatsApp number if different from phone, preferred time to call, etc.)"
    )
    
    # Pledge type
    pledge_type = models.CharField(
        max_length=20,
        choices=PLEDGE_TYPE_CHOICES,
        default=PLEDGE_TYPE_MONETARY,
        blank=True,
        help_text="Type of pledge: monetary or non-monetary"
    )
    
    # Monetary pledge details (only required if pledge_type is monetary)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount pledged (required for monetary pledges)"
    )
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_GHS,
        blank=True,
        help_text="Currency of the pledge amount (required for monetary pledges)"
    )
    other_currency = models.CharField(
        max_length=50,
        blank=True,
        help_text="Specify currency if 'Other' is selected"
    )
    usd_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount in USD (automatically calculated)"
    )
    conversion_rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Exchange rate used for conversion (from currency to USD)"
    )
    conversion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the conversion rate was fetched"
    )
    conversion_source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Source of the exchange rate (e.g., exchangerate-api.com, ECB)"
    )
    donation_frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default=FREQUENCY_ONETIME,
        blank=True,
        help_text="How often would you like to donate?"
    )
    custom_frequency = models.CharField(
        max_length=200,
        blank=True,
        help_text="Specify custom donation frequency (e.g., 'Every 6 months', 'Bi-weekly', etc.)"
    )
    
    # Non-monetary pledge details (only required if pledge_type is non_monetary)
    non_monetary_description = models.TextField(
        blank=True,
        help_text="Describe what you're pledging (services, goods, time, skills, etc.) - required for non-monetary pledges"
    )
    
    # Redemption/fulfillment date
    redemption_date = models.DateField(
        null=True,
        blank=True,
        help_text="When do you plan to redeem/fulfill this pledge? (optional)"
    )
    redemption_timeframe = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alternative: Specify a timeframe for redemption (e.g., 'Within 3 months', 'Q2 2025', etc.)"
    )
    
    # Additional information
    additional_notes = models.TextField(
        blank=True,
        help_text="Any additional information or notes from the pledger"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Current status of the pledge"
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal admin notes about this pledge"
    )
    
    # Completion tracking
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the pledge was fulfilled/completed"
    )
    
    def __str__(self):
        if self.pledge_type == self.PLEDGE_TYPE_MONETARY:
            currency_display = self.other_currency if self.currency == self.CURRENCY_OTHER else self.get_currency_display()
            amount_str = f"{currency_display} {self.amount}" if self.amount else "Amount TBD"
            return f"{self.full_name} - {amount_str} ({self.status})"
        else:
            desc = self.non_monetary_description[:50] + "..." if len(self.non_monetary_description) > 50 else self.non_monetary_description
            return f"{self.full_name} - {desc or 'Non-monetary pledge'} ({self.status})"
    
    def get_currency_display_value(self):
        """Return the currency code or name for display."""
        if self.currency == self.CURRENCY_OTHER:
            return self.other_currency or 'Other'
        return dict(self.CURRENCY_CHOICES).get(self.currency, self.currency)
    
    def get_pledge_summary(self):
        """Get a summary of the pledge for display."""
        if self.pledge_type == self.PLEDGE_TYPE_MONETARY:
            if self.amount:
                return f"{self.get_currency_display_value()} {self.amount:,.2f}"
            return "Amount to be determined"
        else:
            return self.non_monetary_description or "Non-monetary pledge"
    
    def get_country_name(self):
        """Get the country name from the country code."""
        if self.country:
            from django_countries import countries
            return dict(countries).get(self.country, self.country)
        return None
    
    def convert_to_usd(self):
        """Convert the pledge amount to USD using exchange rates."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if this is a monetary pledge with an amount
        if not self.amount:
            logger.debug(f"Pledge {self.id}: No amount, skipping conversion")
            self.usd_amount = None
            return None
        
        if self.pledge_type != self.PLEDGE_TYPE_MONETARY:
            logger.debug(f"Pledge {self.id}: Not monetary pledge, skipping conversion")
            self.usd_amount = None
            return None
        
        # Get currency code
        if self.currency == self.CURRENCY_OTHER:
            if not self.other_currency:
                logger.warning(f"Pledge {self.id}: OTHER currency selected but other_currency is empty")
                self.usd_amount = None
                return None
            currency_code = self.other_currency.strip().upper()
        else:
            if not self.currency:
                logger.warning(f"Pledge {self.id}: No currency specified")
                self.usd_amount = None
                return None
            currency_code = self.currency
        
        # If already in USD, no conversion needed
        if currency_code == 'USD':
            self.usd_amount = self.amount
            logger.info(f"Pledge {self.id}: Already in USD, no conversion needed")
            return self.usd_amount
        
        # Use exchangerate-api.com as primary method (more reliable, free, no API key)
        try:
            import requests
            url = f'https://api.exchangerate-api.com/v4/latest/{currency_code}'
            logger.debug(f"Pledge {self.id}: Attempting conversion from {currency_code} to USD via {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and 'USD' in data['rates']:
                    from decimal import Decimal
                    from datetime import datetime
                    rate = Decimal(str(data['rates']['USD']))  # Convert to Decimal to match amount type
                    self.usd_amount = self.amount * rate
                    self.conversion_rate = rate
                    self.conversion_source = 'exchangerate-api.com'
                    # Parse the date from the API response
                    if 'date' in data:
                        try:
                            self.conversion_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            from datetime import date
                            self.conversion_date = date.today()
                    else:
                        from datetime import date
                        self.conversion_date = date.today()
                    logger.info(f"Pledge {self.id}: Successfully converted {self.amount} {currency_code} = ${self.usd_amount} USD (rate: {rate} from exchangerate-api.com)")
                    return self.usd_amount
                else:
                    logger.warning(f"Pledge {self.id}: USD rate not found in API response for {currency_code}")
            else:
                logger.warning(f"Pledge {self.id}: API returned status {response.status_code} for {currency_code}")
        except Exception as e:
            logger.error(f"Pledge {self.id}: exchangerate-api.com failed for {currency_code}: {str(e)}")
        
        # Fallback to forex-python (may not always be available)
        try:
            from forex_python.converter import CurrencyRates
            from decimal import Decimal
            from datetime import date
            c = CurrencyRates()
            rate = c.get_rate(currency_code, 'USD')
            if rate:
                rate_decimal = Decimal(str(rate))  # Convert to Decimal
                self.usd_amount = self.amount * rate_decimal
                self.conversion_rate = rate_decimal
                self.conversion_source = 'ECB (via forex-python)'
                self.conversion_date = date.today()
                logger.info(f"Pledge {self.id}: Successfully converted via forex-python (ECB): {self.amount} {currency_code} = ${self.usd_amount} USD (rate: {rate_decimal})")
                return self.usd_amount
        except Exception as e:
            logger.warning(f"Pledge {self.id}: forex-python failed for {currency_code}: {str(e)}")
        
        # If all else fails, return None (conversion failed)
        logger.error(f"Pledge {self.id}: All conversion methods failed for {currency_code}")
        self.usd_amount = None
        return None
    
    def save(self, *args, **kwargs):
        """Override save to automatically convert to USD."""
        # Convert to USD before saving
        if self.pledge_type == self.PLEDGE_TYPE_MONETARY and self.amount:
            self.convert_to_usd()
        elif self.pledge_type != self.PLEDGE_TYPE_MONETARY:
            self.usd_amount = None
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Pledge"
        verbose_name_plural = "Pledges"


class AttendanceRecord(TimeStampedModel):
    """
    Model for recording daily attendance/viewership data for "Uplift Your Morning"
    on YouTube and Facebook platforms.
    """
    date = models.DateField(
        unique=True,
        help_text="Date for this attendance record (one record per day)"
    )
    
    # YouTube metrics
    youtube_views = models.IntegerField(
        default=0,
        help_text="Total views on YouTube for this day"
    )
    youtube_likes = models.IntegerField(
        default=0,
        blank=True,
        help_text="Number of likes on YouTube (optional)"
    )
    youtube_comments = models.IntegerField(
        default=0,
        blank=True,
        help_text="Number of comments on YouTube (optional)"
    )
    
    # Facebook metrics
    facebook_views = models.IntegerField(
        default=0,
        help_text="Total views on Facebook for this day"
    )
    facebook_reactions = models.IntegerField(
        default=0,
        blank=True,
        help_text="Number of reactions on Facebook (optional)"
    )
    facebook_comments = models.IntegerField(
        default=0,
        blank=True,
        help_text="Number of comments on Facebook (optional)"
    )
    facebook_shares = models.IntegerField(
        default=0,
        blank=True,
        help_text="Number of shares on Facebook (optional)"
    )
    
    # Additional notes
    notes = models.TextField(
        blank=True,
        help_text="Any additional notes about this day's attendance"
    )
    
    def __str__(self):
        return f"Attendance - {self.date.strftime('%Y-%m-%d')}"
    
    def get_total_views(self):
        """Calculate total views across all platforms."""
        return self.youtube_views + self.facebook_views
    
    def get_total_engagement(self):
        """Calculate total engagement (likes + reactions + comments + shares)."""
        return (
            self.youtube_likes + 
            self.youtube_comments + 
            self.facebook_reactions + 
            self.facebook_comments + 
            self.facebook_shares
        )
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        indexes = [
            models.Index(fields=['-date']),
        ]
