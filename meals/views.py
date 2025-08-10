from django.shortcuts import render, redirect, get_object_or_404
from .forms import MealForm
from .models import Meal
from users.models import VendorProfile
from django.contrib.auth.decorators import login_required

@login_required
def meal_list(request):
    vendor_profile = VendorProfile.objects.get(user=request.user)
    meals = Meal.objects.filter(vendor=vendor_profile)
    return render(request, 'meals/meal_list.html', {'meals': meals})

@login_required
def add_meal(request):
    vendor_profile = VendorProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.vendor = vendor_profile
            meal.save()
            return redirect('meal_list')
    else:
        form = MealForm()
    return render(request, 'meals/add_meal.html', {'form': form})

@login_required
def edit_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    form = MealForm(request.POST or None, request.FILES or None, instance=meal)
    if form.is_valid():
        form.save()
        return redirect('meal_list')
    return render(request, 'meals/edit_meal.html', {'form': form})

@login_required
def delete_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    meal.delete()
    return redirect('meal_list')
