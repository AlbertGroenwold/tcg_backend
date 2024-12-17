from rest_framework.decorators import api_view, permission_classes
from .serializers import ItemSerializer, OrderSerializer, UserSerializer, AddressSerializer
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Item, Order, OrderDetail, Category, Address
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
        # Fetch the user by email
        user = CustomUser.objects.get(email=email)

        # Fetch orders for the user
        user_orders = Order.objects.filter(user=user)

        # Fetch addresses for the user
        addresses = Address.objects.filter(user=user)

        # Serialize orders
        order_serializer = OrderSerializer(user_orders, many=True)

        # Prepare address data
        addresses_data = [
            {
                'id': address.id,
                'address': address.address,
                'city': address.city,
                'province': address.province,
                'postal_code': address.postal_code,
                'country': address.country,
                'address_type': address.address_type,
            }
            for address in addresses
        ]

        return Response({
            'email': user.email,
            'addresses': addresses_data,
            'orders': order_serializer.data,
        })
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    try:
        # Get the order and ensure it belongs to the logged-in user
        order = Order.objects.get(id=order_id, user=request.user)
        order_details = OrderDetail.objects.filter(order=order)

        response_data = {
            "id": order.id,
            "date": order.date,
            "payment_status": order.payment_status,
            "fulfillment_status": order.fulfillment_status,
            "total": order.total,
            "address": order.address,
            "items": [
                {
                    "name": detail.item.name,
                    "quantity": detail.quantity,
                    "price": detail.price,
                }
                for detail in order_details
            ],
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({"error": "Order not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def get_items_by_category(request):
    category_query = request.GET.get('category', None)
    if category_query:
        # Split the category query into parent and child if they exist
        if '/' in category_query:
            parent_name, category_name = category_query.split('/', 1)
            items = Item.objects.filter(
                categories__name__icontains=category_name,
                categories__parent__name__icontains=parent_name
            ).distinct()
        else:
            items = Item.objects.filter(categories__name__icontains=category_query).distinct()
    else:
        items = Item.objects.all()

    # Serialize the items
    items_data = [
        {
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'categories': [category.name for category in item.categories.all()]  # Include all categories for the item
        }
        for item in items
    ]
    return JsonResponse(items_data, safe=False)

def get_category_counts(request):
    categories = Category.objects.all()
    category_counts = []

    for category in categories:
        item_count = category.item_set.count()  # Get the count of items linked to this category
        category_counts.append({
            'id': category.id,
            'name': category.name,
            'parent': category.parent.name if category.parent else None,
            'item_count': item_count,
        })

    return JsonResponse({'categories': category_counts})


def get_item_detail(request, name):
    try:
        # Fetch the item by name (case-insensitive) and prefetch its related categories
        item = Item.objects.prefetch_related('categories').get(name__iexact=name)

        # Serialize the item data including related categories
        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'categories': [
                {'id': category.id, 'name': category.name, 'parent': category.parent.name if category.parent else None}
                for category in item.categories.all()
            ],
            'description': item.description,
            'price': float(item.price),
            'stock': item.stock,
            'image': request.build_absolute_uri(item.image.url) if item.image else None,
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
            # Fetch the user based on the provided email (username)
            user = CustomUser.objects.get(email=username)

            # Fetch the user's addresses
            addresses = Address.objects.filter(user=user)
            address_serializer = AddressSerializer(addresses, many=True)

            # Fetch the user's orders
            orders = Order.objects.filter(user=user)
            orders_serializer = OrderSerializer(orders, many=True)

            # Build the response
            response_data = {
                "email": user.email,
                "addresses": address_serializer.data,
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
    
@api_view(['GET'])
def search_items(request):
    item = request.query_params.get('item', None)
    if item:
        print("Filtering for Item:", item)  # Debugging log
        items = Item.objects.filter(name__icontains=item)  # Case-insensitive match
        print("Items found:", items)  # Debugging log
    else:
        items = []
        print("No category provided; No results found.")  # Debugging log

    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)


def get_sidebar_data(request):
    def build_hierarchy(parent=None):
        # Retrieve categories with the given parent
        categories = Category.objects.filter(parent=parent)
        hierarchy = {}

        for category in categories:
            # Recursively build for child categories
            children = build_hierarchy(category)
            hierarchy[category.name] = {"children": children}

        return hierarchy

    data = build_hierarchy()
    return JsonResponse({"sidebar": data})

def get_category_hierarchy(request):
    def build_hierarchy(parent=None):
        categories = Category.objects.filter(parent=parent).order_by('name')
        return [
            {
                "id": category.id,
                "name": category.name,
                "parent": category.parent.id if category.parent else None,
                "children": build_hierarchy(category)  # Recursively include children
            }
            for category in categories
        ]

    data = build_hierarchy()
    return JsonResponse(data, safe=False)

class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk, *args, **kwargs):
        try:
            address = Address.objects.get(pk=pk)
            address.delete()
            return Response({"message": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Address.DoesNotExist:
            return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        user = request.user
        cart_items = request.data.get('cart_items')
        delivery_address = request.data.get('delivery_address')  # Address from frontend
        billing_address = request.data.get('billing_address')
        total = request.data.get('subtotal')

        # Ensure delivery address fields exist
        formatted_address = ", ".join([
            delivery_address.get('address', '').strip(),
            delivery_address.get('city', '').strip(),
            delivery_address.get('province', '').strip(),
            delivery_address.get('postalCode', '').strip()
        ]).strip(", ")

        if not formatted_address:
            return Response({"error": "Delivery address is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order = Order.objects.create(
            user=user,
            total=total,
            address=formatted_address,  # Save formatted address
            payment_status="Pending",
            fulfillment_status="Processing"
        )

        # Create order details
        for item in cart_items:
            OrderDetail.objects.create(
                order=order,
                item_id=item['id'],
                quantity=item['quantity'],
                price=item['price'] * item['quantity']
            )

        return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
