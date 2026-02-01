"""
Forms for pages app.
"""
from django import forms
from .models import CounselingBooking, Pledge, AttendanceRecord, Question, CoordinatorApplication
from django.utils import timezone
from datetime import date, time


def _get_country_choices():
    """Lazy-load country choices so django_countries isn't loaded at server startup."""
    from django_countries import countries
    return [('', 'Select your country...')] + list(countries)


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


class QuestionForm(forms.ModelForm):
    """Form for visitors to submit questions by topic (Edify, Access Hour, Uplift Your Morning, General, Other)."""
    class Meta:
        model = Question
        fields = ['category', 'name', 'email', 'question']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Your name',
                'required': True,
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'your.email@example.com',
                'required': True,
                'autocomplete': 'email',
            }),
            'question': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 5,
                'placeholder': 'Type your question here. We will reply based on the topic you selected.',
                'required': True,
            }),
        }


def _get_country_choices_for_coordinator():
    """Lazy-load country choices for coordinator form."""
    from django_countries import countries
    return [('', 'Select your country...')] + list(countries)


class CoordinatorApplicationForm(forms.ModelForm):
    """Form for joining the UPLIFT Student Movement or UPLIFT Professional Forum as a member."""
    country = forms.ChoiceField(
        choices=_get_country_choices_for_coordinator,
        required=True,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 border rounded-lg', 'required': True}),
    )

    class Meta:
        model = CoordinatorApplication
        fields = [
            'application_type', 'name', 'email', 'phone',
            'campus_name', 'program_of_study', 'year_of_study', 'additional_student_info',
            'role_or_profession', 'organisation_name', 'years_experience', 'linkedin_url', 'additional_professional_info',
            'profile_message',
        ]
        widgets = {
            'application_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Your full name',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'your.email@example.com',
                'autocomplete': 'email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': '+233 59 148 5783',
                'autocomplete': 'tel',
            }),
            'campus_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g. University of Ghana, KNUST',
            }),
            'program_of_study': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g. Computer Science, Medicine, Business Administration',
            }),
            'year_of_study': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g. Year 2, Final year',
            }),
            'additional_student_info': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 4,
                'placeholder': 'Leadership experience, clubs, expected graduation, interests, or anything else relevant as a student.',
            }),
            'role_or_profession': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g. Software Engineer, Medical Doctor, Teacher',
            }),
            'organisation_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'Employer or organisation name',
            }),
            'years_experience': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'e.g. 5 years, 10+',
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'placeholder': 'https://linkedin.com/in/yourprofile (optional)',
            }),
            'additional_professional_info': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 4,
                'placeholder': 'Industry, key skills, career highlights, or anything else relevant to your professional profile.',
            }),
            'profile_message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 4,
                'placeholder': 'Why do you want to be part of this group and what do you hope to gain or contribute?',
            }),
        }

    def clean(self):
        data = super().clean()
        app_type = data.get('application_type')
        if app_type == CoordinatorApplication.TYPE_STUDENT:
            if not data.get('campus_name'):
                self.add_error('campus_name', 'Please enter your campus or institution name.')
            if not data.get('program_of_study'):
                self.add_error('program_of_study', 'Please enter your program of study.')
        elif app_type == CoordinatorApplication.TYPE_PROFESSIONAL:
            if not data.get('role_or_profession'):
                self.add_error('role_or_profession', 'Please enter your role or profession.')
            if not data.get('organisation_name'):
                self.add_error('organisation_name', 'Please enter your organisation name.')
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.country = self.cleaned_data.get('country', '')
        if commit:
            instance.save()
        return instance


class PledgeForm(forms.ModelForm):
    """Form for submitting pledge commitments (monetary or non-monetary)."""
    
    country = forms.ChoiceField(
        choices=_get_country_choices,
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


class AttendanceRecordForm(forms.ModelForm):
    """Form for recording daily attendance data."""
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'date', 'youtube_views', 'youtube_likes', 'youtube_comments',
            'facebook_views', 'facebook_reactions', 'facebook_comments', 'facebook_shares',
            'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'required': True
            }),
            'youtube_views': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0',
                'required': True
            }),
            'youtube_likes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0'
            }),
            'youtube_comments': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0'
            }),
            'facebook_views': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0',
                'required': True
            }),
            'facebook_reactions': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0'
            }),
            'facebook_comments': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0'
            }),
            'facebook_shares': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border rounded-lg',
                'rows': 3,
                'placeholder': 'Any additional notes about this day\'s attendance (optional)'
            }),
        }
    
    def clean_date(self):
        """Ensure date is not in the future."""
        date_value = self.cleaned_data.get('date')
        if date_value and date_value > date.today():
            raise forms.ValidationError("Date cannot be in the future.")
        return date_value

