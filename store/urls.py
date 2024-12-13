from django.urls import path

from store.views import get_items_by_category
from .views import get_item_detail

urlpatterns = [
    path('items/', get_items_by_category, name='get_items_by_category'),
    path('items/<int:id>/', get_item_detail, name='get_item_detail'),
]