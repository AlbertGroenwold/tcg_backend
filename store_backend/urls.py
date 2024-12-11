from django.contrib import admin
from django.urls import path, include
from store.views import home  # Import the home view

urlpatterns = [
    path('', home, name='home'),  # Add this line for the root path
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),
]
