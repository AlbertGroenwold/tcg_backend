from store.views import get_items_by_category
from django.urls import path
from .views import (
    RegisterUserView,
    UserDetailView,
    get_user_orders,
    get_item_detail,
    CustomTokenObtainPairView,
    search_items,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('items/', get_items_by_category, name='get_items_by_category'),
    path('items/<str:name>/', get_item_detail, name='get_item_detail'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('user/<str:username>/', UserDetailView.as_view(), name='user_detail'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/', get_user_orders, name='user_orders'),
    path('search/', search_items, name='search_items'),
]