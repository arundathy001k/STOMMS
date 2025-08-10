from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home  # Import the home view

urlpatterns = [
    path('', home, name='home'),  # Show home.html when user opens the site
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # User-related URLs
    path('', include('adminpanel.urls')),  # Admin panel-related URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
