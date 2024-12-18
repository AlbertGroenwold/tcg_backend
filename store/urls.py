from store.views import get_items_by_category
from django.urls import path
from .views import (
    RegisterUserView,
    UserDetailView,
    get_user_orders,
    get_item_detail,
    CustomTokenObtainPairView,
    search_items,
    get_category_hierarchy,
    get_sidebar_data,
    AddressDetailView,
    AddressListCreateView,
    create_order,
    get_order_details,
    get_all_items,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('items/', get_items_by_category, name='get_items_by_category'),
    path('items/<str:name>/', get_item_detail, name='get_item_detail'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('user/<str:username>/', UserDetailView.as_view(), name='user_detail'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/', get_user_orders, name='user_orders'), #sdfsdfssaafsdfasfasfasdfasdfasfasfasfasfasfasf
    path('search/', search_items, name='search_items'),
    path('sidebar-data/', get_sidebar_data, name='sidebar-data'),
    path('categories/', get_category_hierarchy, name='category-hierarchy'),#sdfsdfssaafsdfasfasfasdfasdfasfasfasfasfasfasf
    path('categories/hierarchy/', get_category_hierarchy, name='get_category_hierarchy'),#sdfsdfssaafsdfasfasfasdfasdfasfasfasfasfasfasf
    path('address/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('address/', AddressListCreateView.as_view(), name='address-list-create'),
    path('create-order/', create_order, name='create_order'),
    path('orders/<int:order_id>/', get_order_details, name='get_order_details'),
    path('allItems/',get_all_items,name='get_all_items'),
]