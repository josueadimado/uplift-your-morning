"""
Forms for pages app.
"""
from django import forms
from .models import CounselingBooking
from django.utils import timezone
from datetime import date, time


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

