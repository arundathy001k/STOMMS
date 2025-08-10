from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-vendors/', views.manage_vendors, name='manage_vendors'),
    path('view-orders/', views.view_orders, name='view_orders'),
    path('view-subscriptions/', views.view_subscriptions, name='view_subscriptions'),
    path('vendor/<int:vendor_id>/', views.vendor_detail_admin, name='vendor_detail_admin'),





]
