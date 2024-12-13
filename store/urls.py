from store.views import get_items_by_category
from .views import get_item_detail
from django.urls import path
from .views import RegisterUserView, UserDetailView

urlpatterns = [
    path('items/', get_items_by_category, name='get_items_by_category'),
    path('items/<int:id>/', get_item_detail, name='get_item_detail'),
    path('api/register/', RegisterUserView.as_view(), name='register'),
    path('api/user/<str:username>/', UserDetailView.as_view(), name='user_detail'),
]