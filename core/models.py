from django.db import models
from django.core.validators import validate_email, RegexValidator, MinValueValidator
from django.utils import timezone
import pytz


class PricingPlan(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    sessions = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    featured = models.BooleanField(default=False, help_text="Mark this plan as featured.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['price']  # Order plans by old price ascending

    @property
    def has_discount(self):
      return self.discounted_price is not None and self.discounted_price < self.price

class CoachingRequest(models.Model):
    REFERRAL_SOURCES = (
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('other', 'Other'),
    )


    scheduled_datetime = models.DateTimeField("Date and Time", default=timezone.now)
    details = models.TextField("Details", blank=True, null=True) 
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email", validators=[validate_email])

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField("Phone", validators=[phone_regex], max_length=17, blank=False)  # validators should be a list

    referral_source = models.CharField("Referral Source", max_length=10, choices=REFERRAL_SOURCES)
    plan = models.ForeignKey(PricingPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="coaching_requests")
    timezone = models.CharField("Time Zone", max_length=255, default='Africa/Cairo', choices=[(tz, tz) for tz in pytz.common_timezones])


    created_at = models.DateTimeField(auto_now_add=True) # Automatically record creation time
    updated_at = models.DateTimeField(auto_now=True)  #Automatically update on each save
    is_hidden = models.BooleanField(default=False)


    def __str__(self):
        return f"Coaching Request from {self.name} on {self.scheduled_datetime}"


    class Meta:
        verbose_name = "Coaching Request"
        verbose_name_plural = "Coaching Requests"
        ordering = ['-scheduled_datetime']


class HomePageContent(models.Model):
    hero_title = models.CharField("Hero Title", max_length=255, default="We invest in the world’s potential")
    hero_description = models.TextField("Hero Description", default="We focus on markets where technology, innovation, and capital can unlock long-term value and drive economic growth.")
    about_title = models.CharField("About Title", max_length=255, default="About")
    about_description = models.TextField("About Description", default="Ex cumque tempore....")
    about_image = models.ImageField("About Image", upload_to='home_images/', null=True, blank=True)

    def __str__(self):
        return "Home Page Content"

    class Meta:
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Content"
