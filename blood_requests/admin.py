from django.contrib import admin
from .models import BloodRequest, DonorResponse, Notification

admin.site.register(BloodRequest)
admin.site.register(DonorResponse)
admin.site.register(Notification)