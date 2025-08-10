from django.db import models
from django.conf import settings
from users.models import VendorProfile

class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='subscriptions_from_subscriptions_app'
    )
    vendor = models.ForeignKey(
        VendorProfile, 
        related_name='subscriptions_subscriptions', 
        on_delete=models.CASCADE
    )
    plan_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], 
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.plan_name}"
