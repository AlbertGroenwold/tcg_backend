from rest_framework.decorators import api_view, permission_classes
from .serializers import ItemSerializer, OrderSerializer, UserProfileSerializer, UserSerializer
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Item, Order, OrderDetail
from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

def home(request):
    return redirect('/admin')

@api_view(['GET'])
def get_user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_profile(request, email):
    try:
        user_profile = UserProfile.objects.select_related('user').get(user__email=email)
        user_orders = Order.objects.filter(user=user_profile.user)
        profile_serializer = UserProfileSerializer(user_profile)
        order_serializer = OrderSerializer(user_orders, many=True)
        return Response({
            'profile': profile_serializer.data,
            'orders': order_serializer.data
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    details = OrderDetail.objects.filter(order=order)
    response = {
        "id": order.id,
        "items": [
            {
                "name": detail.item.name,
                "quantity": detail.quantity,
                "price": detail.price,
            }
            for detail in details
        ],
    }
    return Response(response)


@api_view(['GET'])
def get_items_by_category(request):
    category = request.query_params.get('category', None)
    if category:
        print("Filtering for category:", category)  # Debugging log
        items = Item.objects.filter(category__iexact=category)  # Case-insensitive match
        print("Items found:", items)  # Debugging log
    else:
        items = Item.objects.all()
        print("No category provided; returning all items.")  # Debugging log

    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

def get_item_detail(request, id):
    try:
        item = Item.objects.get(pk=id)
        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'description': item.description,
            'price': float(item.price),
            'stock': item.stock,
            'image': request.build_absolute_uri(item.image.url) if item.image else None,  # Full URL
            'contains': item.contains,
            'release_date': item.release_date,
        })
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

User = get_user_model()  # Use the custom user model if defined

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = CustomUser.objects.get(email=username)
            profile = user.profile  # Access the related UserProfile instance
            orders = Order.objects.filter(user=user)

            profile_serializer = UserProfileSerializer(profile)
            orders_serializer = OrderSerializer(orders, many=True)

            response_data = {
                "email": user.email,
                "profile": profile_serializer.data,
                "orders": orders_serializer.data,
            }

            return Response(response_data, status=200)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class RegisterUserView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if the user already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = CustomUser.objects.create_user(email=email, password=password)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)  # Use email as the username

        if user is not None:
            # Successful login
            return Response({"email": user.email, "message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            # Failed login
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
