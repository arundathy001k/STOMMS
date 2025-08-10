from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django import forms


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    delivery_time = models.CharField(max_length=50, blank=True, null=True)
    business_description = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='vendor_profiles/', blank=True, null=True)

    def __str__(self):
        return self.business_name

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'vendor':
        VendorProfile.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Meal(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='user_meals')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='meal_images/', null=True, blank=True)

    def __str__(self):
        return self.name


from django.db import models

class MealPlan(models.Model):
    PLAN_CHOICES = [
        ('2day', '2 Days Free Trial'),
        ('2week_veg', '2 Week Vegetarian'),
        ('2week_nonveg', '2 Week Non-Vegetarian'),
        ('1month_veg', '1 Month Vegetarian'),
        ('1month_nonveg', '1 Month Non-Vegetarian'),
        ('3month_veg', '3 Month Vegetarian'),
        ('3month_nonveg', '3 Month Non-Vegetarian'),
    ]

    vendor = models.ForeignKey('VendorProfile', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=PLAN_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='meal_plan_images/', blank=True, null=True)

    def __str__(self):
        return self.get_name_display()

    def get_duration_days(self):
        """Returns the duration in days based on plan name."""
        durations = {
            '2day': 2,
            '2week_veg': 14,
            '2week_nonveg': 14,
            '1month_veg': 30,
            '1month_nonveg': 30,
            '3month_veg': 90,
            '3month_nonveg': 90,
        }
        return durations.get(self.name, 0)



class DailyMenu(models.Model):
    meal_plan = models.ForeignKey('MealPlan', on_delete=models.CASCADE, related_name='daily_menus')
    day_number = models.PositiveIntegerField()  # Day 1, Day 2, etc.
    
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()

    breakfast_time = models.TimeField()
    lunch_time = models.TimeField()
    dinner_time = models.TimeField()

    def __str__(self):
        return f"{self.meal_plan.name} - Day {self.day_number}"



# Notification model - user notifications
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications') 
    message = models.TextField()
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.user} to {self.recipient} at {self.created_at}"


# Subscription Model
class Subscription(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Paid', 'Paid'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    vendor = models.ForeignKey('VendorProfile', on_delete=models.CASCADE, related_name='vendor_subscriptions')
    meal_plan = models.ForeignKey('MealPlan', on_delete=models.CASCADE, related_name='meal_plan_subscriptions')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    is_active = models.BooleanField(default=False) 

    def __str__(self):
        return f"Subscription for {self.user.username} with {self.vendor.business_name}"


class Payment(models.Model):
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.subscription.user.username} - {self.payment_status}"

class DailyMenuForm(forms.ModelForm):
    class Meta:
        model = DailyMenu
        fields = ['day_number', 'breakfast', 'breakfast_time', 'lunch', 'lunch_time', 'dinner', 'dinner_time']
        widgets = {
            'breakfast_time': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_time': forms.TimeInput(attrs={'type': 'time'}),
            'dinner_time': forms.TimeInput(attrs={'type': 'time'}),
        }


def create_daily_menu():
    from meals.models import DailyMenu  # Lazy import inside the function
    menu = DailyMenu.objects.create(day_number=1, breakfast="Pancakes", lunch="Salad", dinner="Pasta", breakfast_time="08:00", lunch_time="12:00", dinner_time="19:00")
    return menu