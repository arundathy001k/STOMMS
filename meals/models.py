from django.db import models
from django.conf import settings
from users.models import VendorProfile  # Adjust if needed

class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='meal_meals')
    title = models.CharField(max_length=100)
    description = models.TextField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='meal_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.meal_type})"


class Subscription(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions_from_meals_app')
    vendor = models.ForeignKey(VendorProfile, related_name='meals_subscriptions', on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=50, choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner')])
    start_date = models.DateField()
    end_date = models.DateField()
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} -> {self.vendor.business_name} ({self.meal_type})"
