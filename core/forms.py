from django import forms
from .models import CoachingRequest, PricingPlan
from django.utils import timezone
from django.core.exceptions import ValidationError


class CoachingRequestForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=PricingPlan.objects.all(), widget=forms.HiddenInput(), required=False
    )
    available_times = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            'placeholder': 'Select available time'
        }),
        label='Available Time'
    )

    class Meta:
        model = CoachingRequest
        fields = [
            'scheduled_datetime',
            'details',
            'name',
            'email',
            'phone',
            'referral_source',
            'plan',
            'available_times' # Add the new field

        ]

        widgets = {
            'scheduled_datetime': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Select date',
                    'min': (timezone.now()).strftime('%Y-%m-%d'),
                    'onchange': 'submit();'

                }
            ),
            'details': forms.Textarea(
                attrs={
                    'rows': '8',
                    'class': 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Your details here'
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Type your name'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Type your email'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Type your phone'
                }
            ),
            'referral_source': forms.Select(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['available_times'].choices = self.get_available_time_choices()  # Populate initial choices.

    def clean(self):
        cleaned_data = super().clean()
        selected_date = cleaned_data.get('scheduled_datetime')
        selected_time = cleaned_data.get('available_times')

        if selected_date and selected_time:
              try:
                  combined_datetime_str = f"{selected_date.strftime('%Y-%m-%d')} {selected_time}"
                  combined_datetime = timezone.datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M')
                  cleaned_data['scheduled_datetime'] = combined_datetime
                  if combined_datetime < timezone.now():
                      raise ValidationError("Please select a date and time in the future.")
              except (ValueError, TypeError):
                  raise ValidationError("Invalid date and time format.")


        return cleaned_data


    def get_available_time_choices(self):
        selected_date = self.data.get('scheduled_datetime')
        if not selected_date:
            return []

        try:
            selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return []

        if selected_date.weekday() == 4:
            return [('', 'Friday is not available')]

        if selected_date.weekday() == 5:
            start_hour = 10
        else:
            start_hour = 12

        start_time = timezone.datetime.combine(selected_date, timezone.datetime.min.time()).replace(hour=start_hour, minute=0)
        end_time = timezone.datetime.combine(selected_date, timezone.datetime.min.time()).replace(hour=18, minute=0)
        interval = timezone.timedelta(hours=1)

        time_slots = []
        current_time = start_time
        while current_time < end_time:
            time_str = current_time.strftime('%I:%M %p')  # Format as AM/PM
            time_slots.append((current_time.strftime('%H:%M'), time_str)) # Save the hour in 24 format for backend, but show in AM/PM
            current_time += interval


        # Filter out unavailable times (from existing requests).
        unavailable_times = CoachingRequest.objects.filter(
            scheduled_datetime__date=selected_date
        ).values_list('scheduled_datetime__time', flat=True)
        
        unavailable_times_str = [time.strftime('%H:%M') for time in unavailable_times]
        available_time_slots = [slot for slot in time_slots if slot[0] not in unavailable_times_str]

        return available_time_slots