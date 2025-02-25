from django.db import models
from django.core.validators import validate_email, RegexValidator, MinValueValidator
from django.utils import timezone
import pytz


class PricingPlan(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    # Change price and discounted_price to CharField
    price = models.CharField(max_length=50)  # e.g., "$100", "€90", "Free"
    discounted_price = models.CharField(
        max_length=50, blank=True, null=True
    )  # e.g., "$80", "€70"
    sessions = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    featured = models.BooleanField(
        default=False, help_text="Mark this plan as featured."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["pk"]  # consistent ordering, pk ensures consistent behavior

    @property
    def has_discount(self):
        return self.discounted_price is not None and self.discounted_price != ""

    @property
    def savings_text(self):
        """Calculates and returns savings text, handling different currencies and free plans.

        Returns:
            str:  A user-friendly string showing the savings, or an empty
                  string if there's no discount or if the calculation is
                  not possible.
        """
        if not self.has_discount:
            return ""

        try:
            # Extract numeric parts, handling different currencies robustly
            price_str = "".join(filter(str.isdigit, self.price))
            discounted_price_str = "".join(filter(str.isdigit, self.discounted_price))

            if not price_str or not discounted_price_str:
                return ""  # Not enough numeric data

            price_num = int(price_str)
            discounted_price_num = int(discounted_price_str)

            # get currency from orginal text.
            price_currency = self.price.replace(price_str, "")
            savings = price_num - discounted_price_num

            if savings > 0:
                return f"{savings} {price_currency}"  # Or any format you prefer
            else:
                return ""  # Handle cases where discounted_price might be higher
        except ValueError:
            return ""  # Handle cases if there isn't integers to extract or calculate
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""


class CoachingRequest(models.Model):
    REFERRAL_SOURCES = (
        ("instagram", "Instagram"),
        ("linkedin", "LinkedIn"),
        ("twitter", "Twitter"),
        ("facebook", "Facebook"),
        ("youtube", "Youtube"),
        ("other", "Other"),
    )

    scheduled_datetime = models.DateTimeField("Date and Time", default=timezone.now)
    details = models.TextField("Details", blank=True, null=True)
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email", validators=[validate_email])

    phone_regex = RegexValidator(
        regex=r"^\+\d{9,15}$",
        message="أدخل رقم الهاتف بالتنسيق الدولي: '+رمز الدولةرقم الهاتف'.",  # More user-friendly message
    )
    phone = models.CharField(
        "Phone", validators=[phone_regex], max_length=17, blank=False
    )  # validators should be a list

    referral_source = models.CharField(
        "Referral Source", max_length=10, choices=REFERRAL_SOURCES
    )
    plan = models.ForeignKey(
        PricingPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coaching_requests",
    )
    timezone = models.CharField(
        "Time Zone",
        max_length=255,
        default="Africa/Cairo",
        choices=[(tz, tz) for tz in pytz.common_timezones],
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Automatically record creation time
    updated_at = models.DateTimeField(
        auto_now=True
    )  # Automatically update on each save
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"Coaching Request from {self.name} on {self.scheduled_datetime}"

    class Meta:
        verbose_name = "Coaching Request"
        verbose_name_plural = "Coaching Requests"
        ordering = ["-scheduled_datetime"]


class HomePageContent(models.Model):
    hero_title = models.CharField(
        "Hero Title", max_length=255, default="We invest in the world’s potential"
    )
    hero_description = models.TextField(
        "Hero Description",
        default="We focus on markets where technology, innovation, and capital can unlock long-term value and drive economic growth.",
    )
    about_title = models.CharField("About Title", max_length=255, default="About")
    about_description = models.TextField(
        "About Description", default="Ex cumque tempore...."
    )
    about_image = models.ImageField(
        "About Image", upload_to="home_images/", null=True, blank=True
    )

    def __str__(self):
        return "Home Page Content"

    class Meta:
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Content"


class Certification(models.Model):
    title = models.TextField(default="", blank=True, null=True)
    subtitle = models.TextField(
        help_text="Source of the certification", default="", blank=True, null=True
    )
    details = models.TextField(default="", blank=True, null=True)
    image = models.ImageField(upload_to="certifications/", blank=True, null=True)

    def __str__(self):
        return self.title
