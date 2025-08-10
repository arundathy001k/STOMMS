from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from users.models import VendorProfile
from orders.models import Order  # corrected from Orders to Order
from subscriptions.models import Subscription


# Admin Login
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            return redirect('admin_dashboard')
        else:
            return render(request, 'adminpanel/login.html', {'error': 'Invalid credentials'})
    return render(request, 'adminpanel/login.html')


# Admin Dashboard
def admin_dashboard(request):
    return render(request, 'adminpanel/dashboard.html')


# Admin Logout
def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


# Manage Users
def manage_users(request):
    CustomUser = get_user_model()
    users = CustomUser.objects.all()
    return render(request, 'adminpanel/manage_users.html', {'users': users})


# Manage Vendors
def manage_vendors(request):
    vendors = VendorProfile.objects.select_related('user').all()
    return render(request, 'adminpanel/manage_vendors.html', {'vendors': vendors})


def vendor_detail_admin(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    return render(request, 'adminpanel/vendor_detail_admin.html', {'vendor': vendor})


# View Orders
def view_orders(request):
    orders = Order.objects.select_related('user', 'meal__vendor__user').all().order_by('-ordered_at')
    return render(request, 'adminpanel/view_orders.html', {'orders': orders})


# View Subscriptions
def view_subscriptions(request):
    subscriptions = Subscription.objects.select_related('user', 'vendor__user').order_by('-start_date')
    return render(request, 'adminpanel/view_subscriptions.html', {'subscriptions': subscriptions})
