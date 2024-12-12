from django import forms
from .models import CoachingRequest, PricingPlan
from django.utils import timezone
from django.core.exceptions import ValidationError
import pytz

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
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        initial='Africa/Cairo',  # Default timezone is Egypt
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            'onchange': 'submit();' # Trigger submit when timezone change
        }),
        label='Your Time Zone'
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
            'available_times',
             'timezone'
        ]

        widgets = {
            'scheduled_datetime': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Select date',
                    'min': (timezone.now()).strftime('%Y-%m-%d'),
                    'onchange': 'submit();' # Trigger submit when date change
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
        # Populate initial time choices using the current date and selected timezone
        if 'scheduled_datetime' not in self.data:
          initial_date = timezone.now().date()
          self.data['scheduled_datetime'] = initial_date.strftime('%Y-%m-%d')
        self.fields['available_times'].choices = self.get_available_time_choices()


    def get_available_time_choices(self):
        selected_date = self.data.get('scheduled_datetime')
        selected_timezone = self.data.get('timezone')

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


        egypt_tz = pytz.timezone('Africa/Cairo')
        if selected_timezone:
            try:
              user_tz = pytz.timezone(selected_timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                user_tz = egypt_tz
        else:
              user_tz = egypt_tz

        start_time = timezone.datetime.combine(selected_date, timezone.datetime.min.time()).replace(hour=start_hour, minute=0)
        end_time = timezone.datetime.combine(selected_date, timezone.datetime.min.time()).replace(hour=18, minute=0)
        interval = timezone.timedelta(hours=1)

        time_slots = []
        current_time = start_time
        while current_time < end_time:
          egypt_time = egypt_tz.localize(current_time)
          user_time = egypt_time.astimezone(user_tz)
          time_str = user_time.strftime('%I:%M %p')
          time_slots.append((current_time.strftime('%H:%M'), time_str))
          current_time += interval



        # Filter out unavailable times (from existing requests).
        unavailable_times = CoachingRequest.objects.filter(
            scheduled_datetime__date=selected_date
        ).values_list('scheduled_datetime__time', flat=True)

        unavailable_times_str = [time.strftime('%H:%M') for time in unavailable_times]
        available_time_slots = [slot for slot in time_slots if slot[0] not in unavailable_times_str]

        return available_time_slots