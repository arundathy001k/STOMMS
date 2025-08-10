from django.urls import path
from . import views
from django.contrib import admin
from .views import vendor_detail_admin

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('view-meals/', views.view_meals, name='view_meals'),
    path('subscribe/<int:vendor_id>/', views.subscribe_plan, name='subscribe_plan'),
    path('my_subscriptions/', views.my_subscriptions, name='my_subscriptions'), 
    path('place_order/', views.place_order, name='place_order'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add-meal/', views.add_meal, name='add_meal'),
    #path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('vendor/<int:vendor_id>/', views.vendor_detail_admin, name='vendor_detail_admin'),

    

    # Vendor features
    path('vendor/profile/', views.edit_vendor_profile, name='edit_vendor_profile'),
    path('set-delivery-time/', views.set_delivery_time, name='set_delivery_time'),
    path('manage-subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('update-subscription/<int:subscription_id>/<str:action>/', views.update_subscription_status, name='update_subscription_status'),
    path('accept/<int:subscription_id>/', views.accept_subscription, name='accept_subscription'),
    path('reject/<int:subscription_id>/', views.reject_subscription, name='reject_subscription'),
    path('add-meal-plan/', views.add_meal_plan, name='add_meal_plan'),
    path('view-meal-plans/', views.view_meal_plans, name='view_meal_plans'),
    path('start-payment/<int:subscription_id>/', views.start_payment, name='start_payment'),
    path('create_payment_intent/<int:subscription_id>/', views.create_payment_intent, name='create_payment_intent'),
    path('payment-success/', views.handle_payment_success, name='handle_payment_success'),
    path('vendor/mealplan/<int:plan_id>/add-day/', views.add_daily_menu, name='add_daily_menu'),
    
    path('enter_delivery_address/', views.enter_delivery_address, name='enter_delivery_address'),

    path('contact/', views.contact, name='contact'),
    path('order-success/', views.order_success, name='order_success'),
]


