from django.contrib import admin
from .models import Certification, CoachingRequest, PricingPlan

admin.site.register(CoachingRequest)
admin.site.register(Certification)
admin.site.register(PricingPlan)
