from django.urls import path

from store.views import get_items_by_category

urlpatterns = [
    path('items/', get_items_by_category, name='get_items_by_category'),
]