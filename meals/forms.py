from django import forms
from meals.models import Meal
from users.models import DailyMenu

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['title', 'description', 'meal_type', 'price', 'image']

class DailyMenuForm(forms.ModelForm):
    class Meta:
        model = DailyMenu
        fields = ['meal_plan', 'day_number', 'breakfast', 'lunch', 'dinner', 'breakfast_time', 'lunch_time', 'dinner_time']
        widgets = {
            'breakfast': forms.Textarea(attrs={'rows': 2}),
            'lunch': forms.Textarea(attrs={'rows': 2}),
            'dinner': forms.Textarea(attrs={'rows': 2}),
            'breakfast_time': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_time': forms.TimeInput(attrs={'type': 'time'}),
            'dinner_time': forms.TimeInput(attrs={'type': 'time'}),
        }