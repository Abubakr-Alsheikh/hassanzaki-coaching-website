from django.contrib import admin
from .models import Certification, CoachingRequest

admin.site.register(CoachingRequest)
admin.site.register(Certification)