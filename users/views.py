from django.conf import settings
import stripe
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomRegisterForm, VendorProfileForm, DeliveryTimeForm, UserProfileForm, MealForm, MealPlanForm, DailyMenuForm
from .models import CustomUser, VendorProfile, UserProfile, Subscription, MealPlan, Payment, Notification # Added MealPlan here
from meals.models import Meal
from django.utils import timezone
from .models import Notification
from django.http import HttpResponse 
from django.http import Http404
from .forms import MealForm
from meals.forms import MealForm
from .forms import DailyMenuForm
from users.models import Notification
stripe.api_key = settings.STRIPE_SECRET_KEY
from meals.forms import DailyMenuForm
from orders.models import Order


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'vendorprofile'):
                return redirect('vendor_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'users/login.html')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'vendorprofile'):
        return redirect('vendor_dashboard')
    else:
        return redirect('user_dashboard')



@login_required
def admin_dashboard(request):
    return render(request, 'adminpanel/dashboard.html')

def vendor_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'vendor':
        return redirect('login')

    vendor = get_object_or_404(VendorProfile, user=request.user)

    
    vendor_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    context = {
        'vendor': vendor,
        'notifications': vendor_notifications,
    }

    return render(request, 'vendor/dashboard.html', context) 

@login_required
def user_dashboard(request):
    user_profile = None
    if hasattr(request.user, 'userprofile'):
        user_profile = request.user.userprofile

    subscriptions = Subscription.objects.filter(user=request.user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    vendors = VendorProfile.objects.all()

    return render(request, 'users/dashboard.html', {
        'user_profile': user_profile,
        'subscriptions': subscriptions,
        'notifications': notifications,
        'vendor': vendors
    })


@login_required
def edit_vendor_profile(request):
    profile, created = VendorProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = VendorProfileForm(instance=profile)
    return render(request, 'vendor/edit_profile.html', {'form': form})

@login_required
def set_delivery_time(request):
    vendor_profile = VendorProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = DeliveryTimeForm(request.POST, instance=vendor_profile)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = DeliveryTimeForm(instance=vendor_profile)
    return render(request, 'vendor/set_delivery_time.html', {'form': form})

@login_required
def manage_subscriptions(request):
    vendor_profile = VendorProfile.objects.get(user=request.user)
    subscriptions = Subscription.objects.filter(vendor=vendor_profile)
    return render(request, 'vendor/manage_subscriptions.html', {'subscriptions': subscriptions})

@login_required
def update_subscription_status(request, subscription_id, action):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if subscription.vendor == request.user and subscription.status == 'Pending':
        if action == 'accept':
            subscription.status = 'Accepted'
        elif action == 'reject':
            subscription.status = 'Rejected'
        subscription.save()

        Notification.objects.create(user=subscription.user, message=f"Your subscription to {subscription.vendor.username}'s meal plan has been {action}!")
    return redirect('manage_subscriptions')


# User: View All Meals
@login_required
def view_meals(request):
    if request.user.role == 'vendor':
        vendor = get_object_or_404(VendorProfile, user=request.user)
        meals = MealPlan.objects.filter(vendor=vendor)
        return render(request, 'vendor/view_meals.html', {'meals': meals})
    else:
        return render(request, 'users/dashboard.html')

@login_required
def browse_meals(request):
    meals = MealPlan.objects.all()
    return render(request, 'users/browse_meals.html', {'meals': meals})

@login_required
def place_order(request):
    meals = MealPlan.objects.all() 

    if request.method == "POST":
        meal_id = request.POST.get("meal")
        meal = MealPlan.objects.get(id=meal_id)
        
        return redirect('dashboard')  

    return render(request, 'users/place_order.html', {'meals': meals})

@login_required
def subscribe_plan(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    meal_plans = MealPlan.objects.filter(vendor=vendor)

    if request.method == 'POST':
        meal_plan_id = request.POST.get('meal_plan')
        
        if meal_plan_id:
            meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, vendor=vendor)

            # Create a new subscription for the logged-in user, linking it to the vendor and the selected meal plan
            subscription = Subscription(user=request.user, vendor=vendor, meal_plan=meal_plan)
            subscription.save()

            # Create a notification for the user (recipient is the user who subscribed)
            Notification.objects.create(
                user=request.user,  # The user who is sending the notification (probably the admin or vendor)
                recipient=request.user,  # The recipient is the user who subscribed
                message=f"Subscribed to {vendor.business_name}'s plan {meal_plan.name}."
            )

            # Redirect the user to their subscription page or dashboard
            return redirect('my_subscriptions')

    # If GET request, pass meal plans to the template
    return render(request, "users/subscribe_plan.html", {'vendor': vendor, 'meal_plans': meal_plans})



# User's subscriptions
def my_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'users/my_subscriptions.html', {'subscriptions': subscriptions})



# User: Place Order (Placeholder)
@login_required
def place_order(request):
    if request.method == 'POST':
        selected_meal_id = request.POST.get('meal')
        request.session['selected_meal_id'] = selected_meal_id  # Save meal temporarily in session
        return redirect('enter_delivery_address')  # Redirect to delivery address page
    meals = Meal.objects.all()
    return render(request, 'users/place_order.html', {'meals': meals})

def enter_delivery_address(request):
    selected_meal_id = request.session.get('selected_meal_id')
    if not selected_meal_id:
        return redirect('place_order')  # fallback

    meal = Meal.objects.get(id=selected_meal_id)

    if request.method == 'POST':
        address = request.POST.get('address')
        Order.objects.create(user=request.user, meal=meal, address=address)
        return redirect('order_success')  # create this template too

    return render(request, 'users/enter_delivery_address.html', {'meal': meal})



def order_success(request):
    return render(request, 'users/order_success.html')



# User: Edit Profile
@login_required
def edit_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'users/edit_profile.html', {'form': form})


# Vendor: Add Meal
@login_required
def add_meal(request):
    vendor = VendorProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.vendor = vendor
            meal.save()
            print("Meal saved:", meal)
            return redirect('view_meals')  # Make sure this name matches your URL pattern
        else:
            print("Form errors:", form.errors)
    else:
        form = MealForm()

    return render(request, 'vendor/add_meal.html', {'form': form})

 # Render a form for adding a meal
@login_required
def add_meal_plan(request):
    vendor = VendorProfile.objects.get(user=request.user)  # Get the logged-in vendor's profile
    
    if request.method == 'POST':
        form = MealPlanForm(request.POST, request.FILES)  # Pass request.FILES to handle image uploads
        if form.is_valid():
            meal_plan = form.save(commit=False)
            meal_plan.vendor = vendor  # Associate the plan with the logged-in vendor
            meal_plan.save()
            return redirect('view_meal_plans')  # Redirect to the view where meal plans are listed
    
    else:
        form = MealPlanForm()

    return render(request, 'vendor/add_meal_plan.html', {'form': form})


# User: View Vendor Detail Page
def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    meals = Meal.objects.filter(vendor=vendor)
    return render(request, 'vendor/vendor_detail.html', {'vendor': vendor, 'meals': meals})


# Contact Page
def contact(request):
    return render(request, 'contact.html')


# Add Meal Plan and Daily Menu for VendorProfile@login_required
@login_required
def add_meal(request):
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the vendor associated with the user
            vendor = get_object_or_404(VendorProfile, user=request.user)

            # Create the meal
            meal = form.save(commit=False)
            meal.vendor = vendor  # Link the meal to the vendor
            meal.save()

            messages.success(request, 'Meal added successfully.')
            return redirect('view_meals')  # Redirect to the page where meals are listed
    else:
        form = MealForm()

    return render(request, 'vendor/add_meal.html', {'form': form})



@login_required
def add_daily_menu(request, plan_id):
    if request.user.role != 'vendor':
        raise Http404("You do not have permission to view this page.")
    meal_plan = MealPlan.objects.get(id=plan_id)
    if meal_plan.vendor != request.user.vendorprofile:
        raise Http404("This meal plan doesn't belong to you.")
    if request.method == 'POST':
        daily_menu_form = DailyMenuForm(request.POST)
        if daily_menu_form.is_valid():
            daily_menu = daily_menu_form.save(commit=False)
            daily_menu.meal_plan = meal_plan
            daily_menu.save()
            messages.success(request, "Daily Menu added successfully!")
            return redirect('vendor_dashboard')
    else:
        daily_menu_form = DailyMenuForm()
    return render(request, 'vendor/add_daily_menu.html', {'daily_menu_form': daily_menu_form})

def view_meal_plans(request):
    meal_plans = MealPlan.objects.all()  # Fetch all meal plans or filter based on some criteria
    return render(request, 'vendor/view_meal_plans.html', {'meal_plans': meal_plans})

@login_required
def accept_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.status = 'Accepted'
        subscription.save()
        return redirect('manage_subscriptions')
    except Subscription.DoesNotExist:
        return redirect('manage_subscriptions')



@login_required
def reject_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.status = 'Rejected'
        subscription.save()
        return redirect('manage_subscriptions')
    except Subscription.DoesNotExist:
        
        return redirect('manage_subscriptions')



@login_required
def confirm_payment(request, subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)
    
    # Check if the payment has already been processed
    if Payment.objects.filter(subscription=subscription, payment_status='Paid').exists():
        return JsonResponse({'message': 'Payment already processed.'}, status=400)
    
    # Assuming payment was successful
    payment = Payment.objects.create(
        subscription=subscription,
        payment_method='Stripe',  # or 'Razorpay' based on your choice
        amount=subscription.meal_plan.price,  # Assuming price is stored in the MealPlan model
        payment_status='Paid',
        transaction_id='Some-Transaction-ID',  # Get transaction ID from payment gateway
    )
    
    # Update subscription status to Paid
    subscription.status = 'Paid'
    subscription.save()

    # Redirect to the user's subscription page or a success page
    return redirect('my_subscriptions')

@login_required
def create_payment_intent(request, subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)

    # Create a Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=int(subscription.meal_plan.price * 100),  # Stripe accepts cents
        currency='usd',
        metadata={'subscription_id': subscription.id},
    )

    # Render the payment page with the client secret and subscription details
    return render(request, 'payment_page.html', {
        'client_secret': intent.client_secret,
        'subscription': subscription,
    })

def handle_payment_success(request):
    if not request.user.is_authenticated:
        return redirect('login')

    subscription_id = request.session.get('subscription_id')
    if not subscription_id:
        return redirect('my_subscriptions')

    try:
        subscription = Subscription.objects.get(id=subscription_id, user=request.user)
        subscription.status = 'paid'
        subscription.save()

        vendor_user = subscription.vendor.user
        Notification.objects.create(
            user=request.user,
            recipient=vendor_user,
            message=f"{request.user.username} completed payment for {subscription.meal_plan.name}."
        )

        del request.session['subscription_id']

    except Subscription.DoesNotExist:
        pass

    return redirect('my_subscriptions')


@login_required
def start_payment(request, subscription_id):
    try:
        print("Starting payment process...")
        subscription = Subscription.objects.get(id=subscription_id)
        print(f"Subscription found: {subscription.id}")

        if subscription.status != 'Accepted':
            return HttpResponse("Subscription is not accepted yet.", status=400)

        
        request.session['subscription_id'] = subscription.id

        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(subscription.meal_plan.price * 100),  # Amount in cents
            currency='usd',
            metadata={'subscription_id': subscription.id},
        )

        print(f"PaymentIntent created: {intent.id}")

        return render(request, 'payment_page.html', {
            'client_secret': intent.client_secret,
            'subscription': subscription,
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)



def handle_payment_success(request):
    subscription_id = request.session.get('subscription_id')

    if subscription_id:
        try:
            subscription = Subscription.objects.get(id=subscription_id)
            vendor = subscription.vendor
            user = subscription.user

            # Debugging logs
            print(f"User: {user.username}, Vendor: {vendor.user.username}")

            # Log before saving
            print(f"Before save: {subscription.is_active}")  
            
            # Activate subscription
            subscription.is_active = True
            subscription.save()

            # Log after saving
            print(f"After save: {subscription.is_active}")  

            # Send notification to vendor
            notification = Notification.objects.create(
                user=user,  # The customer who made the payment
                recipient=vendor.user,  # The vendor to receive the notification
                message=f"{user.username} completed payment for {subscription.meal_plan.name}."
            )

            # Debugging log for notification
            print(f"Notification created: {notification.message}")

            # Clear session
            del request.session['subscription_id']

        except Subscription.DoesNotExist:
            pass

    messages.success(request, "Payment successful. Subscription activated.")
    return redirect('my_subscriptions')

def add_daily_menu(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, vendor__user=request.user)

    if request.method == 'POST':
        form = DailyMenuForm(request.POST)
        if form.is_valid():
            daily_menu = form.save(commit=False)
            daily_menu.meal_plan = plan
            daily_menu.save()
            return redirect('view_meal_plan', plan_id=plan.id)  # or any page showing the plan
    else:
        form = DailyMenuForm()

    return render(request, 'vendor/add_daily_menu.html', {'form': form, 'plan': plan})

def update_daily_menu(request, meal_plan_id, day_number):
    # Retrieve the meal plan and specific day menu
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    daily_menu = get_object_or_404(DailyMenu, meal_plan=meal_plan, day_number=day_number)
    
    # Check if the user is a vendor and has the correct permissions
    if request.user.role != 'vendor' or daily_menu.meal_plan.vendor.user != request.user:
        return redirect('some_error_page')  # Redirect if not a vendor or wrong vendor

    if request.method == 'POST':
        form = DailyMenuForm(request.POST, instance=daily_menu)
        if form.is_valid():
            form.save()
            return redirect('meal_plan_detail', meal_plan_id=meal_plan.id)  # Redirect to meal plan details page
    else:
        form = DailyMenuForm(instance=daily_menu)

    return render(request, 'update_daily_menu.html', {'form': form, 'meal_plan': meal_plan, 'day_number': day_number})

def vendor_detail_admin(request, vendor_id):
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    return render(request, 'adminpanel/vendor_detail_admin.html', {'vendor': vendor})

