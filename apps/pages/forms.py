"""
Forms for pages app.
"""
from django import forms
from .models import CounselingBooking, Pledge
from django.utils import timezone
from datetime import date, time
from django_countries import countries


class CounselingBookingForm(forms.ModelForm):
    """Form for submitting counseling booking requests."""
    
    class Meta:
        model = CounselingBooking
        fields = [
            'full_name', 'email', 'phone', 'country',
            'preferred_date', 'preferred_time', 'duration_minutes',
            'topic', 'message'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Your full name',
                'required': True,
                'autocomplete': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'your.email@example.com (optional)',
                # Email is optional on this form
                'required': False,
                'autocomplete': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                # Ask users to enter phone numbers in full international format
                # e.g. +233 20 123 4567 or +234 803 123 4567
                'placeholder': '+233 20 123 4567',
                'required': True,
                'autocomplete': 'tel'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Your country (optional)',
                'autocomplete': 'country-name'
            }),
            'preferred_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 border rounded-lg date-picker',
                'required': True,
                'autocomplete': 'off',
                'readonly': True,
                'data-lpignore': 'true',
                'data-form-type': 'other'
            }),
            'preferred_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'required': True
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg bg-gray-100',
                'value': 30,
                'readonly': True,
                'style': 'cursor: not-allowed;'
            }),
            'topic': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Brief topic or reason for counseling (optional)',
                'maxlength': 200
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 4,
                'placeholder': 'Additional details or message (optional)'
            }),
        }
    
    def clean_preferred_date(self):
        """Ensure preferred date is not in the past."""
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < date.today():
            raise forms.ValidationError("Preferred date cannot be in the past.")
        return preferred_date
    
    def clean_duration_minutes(self):
        """Always set duration to 30 minutes (fixed for all sessions)."""
        return 30


class PledgeForm(forms.ModelForm):
    """Form for submitting pledge commitments (monetary or non-monetary)."""
    
    country = forms.ChoiceField(
        choices=[('', 'Select your country...')] + list(countries),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 border rounded-lg',
            'autocomplete': 'country'
        })
    )
    
    class Meta:
        model = Pledge
        fields = [
            'full_name', 'email', 'phone', 'country',
            'preferred_contact_method', 'contact_info',
            'amount', 'currency', 'other_currency',
            'donation_frequency', 'custom_frequency',
            'redemption_date', 'redemption_timeframe',
            'non_monetary_description', 'additional_notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Your full name',
                'required': True,
                'autocomplete': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'your.email@example.com',
                'required': True,
                'autocomplete': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Phone number (optional)',
                'required': False,
                'autocomplete': 'tel',
                'type': 'tel'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'required': True
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 3,
                'placeholder': 'Additional contact information (e.g., WhatsApp number if different, preferred time to call, etc.)'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg'
            }),
            'other_currency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Specify currency (e.g., CAD, AUD, JPY)'
            }),
            'donation_frequency': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg'
            }),
            'custom_frequency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g., Every 6 months, Bi-weekly, etc.',
                'style': 'display: none;'
            }),
            'non_monetary_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 4,
                'placeholder': 'Describe what you\'re pledging (e.g., "I will provide 10 hours of graphic design services" or "I will donate 50 books")',
                'style': 'display: none;'
            }),
            'redemption_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg flatpickr',
                'placeholder': 'Select a date',
                'type': 'text'  # Use text type for Flatpickr
            }),
            'redemption_timeframe': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g., Within 3 months, Q2 2025, By end of year'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 4,
                'placeholder': 'Any additional information or notes (optional)'
            }),
        }
    
    def clean_amount(self):
        """Ensure amount is positive if provided."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Pledge amount must be greater than zero.")
        return amount
    
    def clean(self):
        """Validate fields."""
        cleaned_data = super().clean()
        currency = cleaned_data.get('currency')
        other_currency = cleaned_data.get('other_currency')
        amount = cleaned_data.get('amount')
        
        # If amount is provided, currency should be provided too
        if amount and not currency:
            raise forms.ValidationError({
                'currency': 'Please select a currency when entering an amount.'
            })
        
        # If "Other" currency is selected, require the other_currency field
        if currency == Pledge.CURRENCY_OTHER and not other_currency:
            raise forms.ValidationError({
                'other_currency': 'Please specify the currency name when selecting "Other Currency".'
            })
        
        # If "Custom" frequency is selected, require the custom_frequency field
        donation_frequency = cleaned_data.get('donation_frequency')
        custom_frequency = cleaned_data.get('custom_frequency')
        if donation_frequency == Pledge.FREQUENCY_CUSTOM and not custom_frequency:
            raise forms.ValidationError({
                'custom_frequency': 'Please specify your custom donation frequency.'
            })
        
        # Normalize phone number if provided
        phone = cleaned_data.get('phone')
        if phone:
            # Remove any extra whitespace
            phone = phone.strip()
            # Ensure it starts with + if it's a valid international number
            if phone and not phone.startswith('+') and phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
                # If it's just digits without +, we'll let intl-tel-input handle it
                # But we should keep it as is since the JS will format it
                pass
            cleaned_data['phone'] = phone
        
        return cleaned_data

