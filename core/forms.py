from django import forms
from django.core.validators import validate_email, RegexValidator
from .models import Certification, CoachingRequest, PricingPlan
from django.utils import timezone as django_timezone
from django.utils import timezone
import pytz


class CoachingRequestForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=PricingPlan.objects.all(), widget=forms.HiddenInput(), required=False
    )
    available_times = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
            }
        ),
        label="الوقت المتاح",
        help_text="اختر الوقت المناسب لك بناءً على المنطقة الزمنية المحددة.",
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid_choice': 'نعتذر من الخطاء. الرجاء اختيار وقت متاح من القائمة مرة اخرى.'}
    )
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        initial="Africa/Cairo",
        widget=forms.Select(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
            }
        ),
        label="المنطقة الزمنية",
        help_text="يرجى تحديد منطقتك الزمنية لتظهر لك الأوقات المتاحة بشكل صحيح.",
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid_choice': 'الرجاء اختيار منطقة زمنية صحيحة.'}
    )
    scheduled_datetime = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "placeholder": "اختر التاريخ",
                "min": (django_timezone.now().date()).strftime("%Y-%m-%d"),
            }
        ),
        label="التاريخ المقترح للجلسة",
        help_text="اختر التاريخ المفضل لجلسة التدريب. سيتم عرض الأوقات المتاحة بعد اختيار التاريخ والمنطقة الزمنية.",
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid': 'أدخل تاريخاً صحيحاً.'}
    )
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "placeholder": "أدخل اسمك كاملاً",
            }
        ),
        label="اسمك بالكامل",
        error_messages={'required': 'هذا الحقل مطلوب.'}
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "placeholder": "أدخل عنوان بريدك الإلكتروني (example@domain.com)",
                "dir": "ltr",
            }
        ),
        label="بريدك الإلكتروني",
        validators=[validate_email],
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid': 'أدخل عنوان بريد إلكتروني صحيح.'}
    )
    phone = forms.CharField(
        max_length=17,
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "placeholder": "أدخل رقم هاتفك (مثال: 201234567890+)",
                "dir": "ltr",
            }
        ),
        label="رقم هاتفك للتواصل",
        help_text="مثال: 2010XXXXXXXX+",
        validators=[RegexValidator(
            regex=r'^\+\d{9,15}$',
            message="أدخل رقم الهاتف بالتنسيق الدولي: '+رمز الدولةرقم الهاتف'."
        )],
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid': 'أدخل رقم هاتف صحيح. رقم الهاتف بالتنسيق الدولي: +رمز الدولةرقم الهاتف'}
    )
    referral_source = forms.ChoiceField(
        choices=CoachingRequest.REFERRAL_SOURCES,
        widget=forms.Select(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
            }
        ),
        label="كيف سمعت عني؟",
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid_choice': 'الرجاء اختيار مصدر صحيح.'}
    )
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": "4",
                "class": "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "placeholder": "شاركني بتفاصيل حول ما تأمل تحقيقه من الجلسة (اختياري)",
            }
        ),
        label="رسالتك أو تفاصيل إضافية (اختياري)",
    )

    class Meta:
        model = CoachingRequest
        fields = [
            "timezone",
            "scheduled_datetime",
            "available_times",
            "name",
            "phone",
            "email",
            "referral_source",
            "details",
        ]
        labels = {
            "scheduled_datetime": "التاريخ المقترح للجلسة",
            "details": "رسالتك أو تفاصيل إضافية (اختياري)",
            "name": "اسمك بالكامل",
            "email": "بريدك الإلكتروني",
            "phone": "رقم هاتفك للتواصل",
            "referral_source": "كيف سمعت عني؟",
        }
        help_texts = {
            "phone": "مثال: 2010XXXXXXXX+",
            "scheduled_datetime": "اختر التاريخ المفضل لجلسة التدريب. سيتم عرض الأوقات المتاحة بعد اختيار التاريخ والمنطقة الزمنية.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "scheduled_datetime" not in self.data:
            initial_date = timezone.now().date()
            if 'scheduled_datetime' not in self.initial:  # Prevent overwriting initial data
                self.initial["scheduled_datetime"] = initial_date.strftime("%Y-%m-%d")
        self.fields["available_times"].choices = self.get_available_time_choices()

    def get_available_time_choices(self):
        selected_date_str = self.data.get("scheduled_datetime") or self.initial.get("scheduled_datetime")
        selected_timezone_str = self.data.get("timezone") or self.initial.get("timezone")

        if not selected_date_str:
            return []

        try:
            selected_date = timezone.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return []

        # Handle Fridays and Saturdays
        if selected_date.weekday() == 4:  # Friday
            return [("", "الجمعة غير متاح, الرجاء اختيار يوم اخر")]

        # Set start time based on the day
        start_hour = 10 if selected_date.weekday() == 5 else 17
        end_hour = 18 if selected_date.weekday() == 5 else 23

        # Timezone Handling
        egypt_tz = pytz.timezone("Africa/Cairo")
        try:
            user_tz = pytz.timezone(selected_timezone_str) if selected_timezone_str else egypt_tz
        except pytz.exceptions.UnknownTimeZoneError:
            user_tz = egypt_tz

        # Define start and end times (timezone-aware)
        start_time = egypt_tz.localize(
            timezone.datetime(selected_date.year, selected_date.month, selected_date.day, start_hour, 0)
        )
        end_time = egypt_tz.localize(
            timezone.datetime(selected_date.year, selected_date.month, selected_date.day, end_hour, 0)
        )

        # Filter out past times (always use Egypt time for comparison)
        now_egypt_tz = timezone.now().astimezone(egypt_tz)
        if start_time < now_egypt_tz:
            # Adjust start_time to the next full hour in Egypt time
            start_time = now_egypt_tz.replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)

        # Create time slots
        time_slots = []
        current_time = start_time
        while current_time <= end_time:
            user_time = current_time.astimezone(user_tz)
            time_str = user_time.strftime("%I:%M %p")
            time_slots.append((current_time.strftime("%H:%M"), time_str))
            current_time += timezone.timedelta(hours=1)

        # Filter out unavailable times
        unavailable_times = CoachingRequest.objects.filter(
            scheduled_datetime__date=selected_date
        ).values_list("scheduled_datetime", flat=True)

        unavailable_times_str = [time.astimezone(egypt_tz).strftime("%H:%M") for time in unavailable_times]
        available_time_slots = [
            slot for slot in time_slots if slot[0] not in unavailable_times_str
        ]

        if not available_time_slots:
            return [("", "لا يوجد أوقات متاحة في هذا اليوم")]

        return available_time_slots


class PricingPlanForm(forms.ModelForm):
    class Meta:
        model = PricingPlan
        fields = [
            "name",
            "description",
            "price",
            "discounted_price",
            "sessions",
            "featured",
        ]

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            raise forms.ValidationError("هذا الحقل مطلوب.")
        return price
        
    def clean_sessions(self):
        sessions = self.cleaned_data.get("sessions")
        if sessions is None:
            raise forms.ValidationError("هذا الحقل مطلوب.")
        if sessions <= 0:
            raise forms.ValidationError(
                "يجب أن يكون عدد الجلسات أكبر من صفر."
            )
        return sessions
    
    def clean(self):
        cleaned_data = super().clean()
        discounted_price = cleaned_data.get('discounted_price')
        price = cleaned_data.get('price')
        
        if discounted_price is not None and price is not None:
          if discounted_price >= price:
            self.add_error('discounted_price', "يجب أن يكون السعر الجديد أقل من السعر الأصلي.")
        return cleaned_data


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['title', 'subtitle', 'details', 'image']