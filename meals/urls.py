from django.urls import path
from .views import (
    meal_list, add_meal, edit_meal, delete_meal,
    browse_meals, view_meal, subscription_page
)

urlpatterns = [
    # Vendor-side URLs
    path('vendor/meals/', meal_list, name='meal_list'),
    path('vendor/meals/add/', add_meal, name='add_meal'),
    path('vendor/meals/edit/<int:pk>/', edit_meal, name='edit_meal'),
    path('vendor/meals/delete/<int:pk>/', delete_meal, name='delete_meal'),

    # 👇 User-side URLs
    path('browse-meals/', browse_meals, name='browse_meals'),
    path('view_meal/<int:meal_id>/', view_meal, name='view_meal'),
    path('subscription/<int:meal_id>/', subscription_page, name='subscription_page'),
    path('view-meals/', browse_meals, name='view_meals'),

]
