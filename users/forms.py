from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, VendorProfile, UserProfile
from .models import Meal
from django import forms
from .models import Meal, MealPlan, DailyMenu
from meals.models import Meal 



class CustomRegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('vendor', 'Vendor'),
    ]
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'address', 'contact_number','business_description', 'profile_image']

class DeliveryTimeForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['delivery_time']
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'profile_picture']


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['name', 'description', 'price', ]  # You can add other fields if needed
        widgets = {
            'name': forms.Select(choices=MealPlan.PLAN_CHOICES),  # This makes the dropdown for plan choices
        }

# Form for Meal Plan creation
class DailyMenuForm(forms.ModelForm):
    class Meta:
        model = DailyMenu
        fields = ['day_number', 'breakfast', 'breakfast_time', 'lunch', 'lunch_time', 'dinner', 'dinner_time']
        widgets = {
            'breakfast_time': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_time': forms.TimeInput(attrs={'type': 'time'}),
            'dinner_time': forms.TimeInput(attrs={'type': 'time'}),
        }


# Form for Daily Menu creation


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['title', 'description', 'meal_type', 'price', 'image']

