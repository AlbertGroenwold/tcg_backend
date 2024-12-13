from django.contrib import admin
from django.urls import path, include
from store.views import home  # Import the home view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),  # Add this line for the root path
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),
]

# Serve media files during development
if settings.DEBUG:  # Only serve media files through Django in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
