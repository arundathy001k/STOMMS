from django.contrib import admin
from .models import VendorProfile, MealPlan, Subscription, Notification

admin.site.register(VendorProfile)
admin.site.register(MealPlan)
admin.site.register(Subscription)
admin.site.register(Notification)
