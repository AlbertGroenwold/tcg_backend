import unicodedata
from django.db.models import Prefetch
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
from django.db.models import Sum


def home(request):
    return redirect('/admin')

def normalize_string(input_str):
    """Normalize a string to NFKD (Compatibility Decomposition)."""
    return unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')


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


def get_descendant_categories(category):
    """ Recursively fetch all descendant categories for the given category """
    descendants = []
    children = category.children.all()
    for child in children:
        descendants.append(child)
        descendants.extend(get_descendant_categories(child))
    return descendants


def get_items_by_category(request):
    category_name = request.GET.get('category', None)  # Fetch query parameter

    if not category_name:
        return JsonResponse({'error': 'Category parameter is required'}, status=400)

    try:
        # Normalize the category name for consistent comparison
        normalized_category_name = normalize_string(category_name)

        # Find categories ignoring case and normalization
        base_category = Category.objects.filter(
            name__iexact=category_name
        ).first() or Category.objects.filter(
            name__iexact=normalized_category_name
        ).first()

        if not base_category:
            return JsonResponse({'error': 'Category not found'}, status=404)

        # Get all descendant categories
        descendant_categories = get_descendant_categories(base_category)
        all_categories = [base_category] + descendant_categories

        # Query items belonging to these categories
        items = Item.objects.filter(categories__in=all_categories).distinct()

        # Format response
        data = [
            {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'categories': [cat.name for cat in item.categories.all()],
                'image': request.build_absolute_uri(item.image.url) if item.image else None,
            }
            for item in items
        ]
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



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
        item = Item.objects.prefetch_related('categories').get(name__iexact=name)
        discounted_price = float(item.discount_price) if item.discount_price else 0
        final_price = float(item.price) - discounted_price

        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'categories': [
                {'id': category.id, 'name': category.name, 'parent': category.parent.name if category.parent else None}
                for category in item.categories.all()
            ],
            'description': item.description,
            'price': final_price,
            'original_price': float(item.price),
            'discount_price': discounted_price,
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

@api_view(['GET'])
def get_all_items(request):    
    items = Item.objects.all()
    item_names = [item.name for item in items]
    return Response(item_names)

@api_view(['GET'])
def homepage_sections(request):
    # Helper function to calculate the effective price
    def calculate_effective_price(item):
        return float(item.price) - float(item.discount_price or 0)

    # Fetch the required items for each section
    new_items = Item.objects.filter(is_active=True).order_by('-date_added')[:8]
    on_sale_items = Item.objects.filter(is_active=True, discount_price__isnull=False)[:8]
    best_sellers = Item.objects.annotate(
        total_sold=Sum('orderdetail__quantity')
    ).filter(is_active=True).order_by('-total_sold')[:8]
    top_rated = Item.objects.filter(is_active=True).order_by('-rating', '-reviews_count')[:8]

    # Fallback: if no items exist for the categories, fetch 8 random items
    fallback_items = []
    if not new_items and not on_sale_items and not best_sellers and not top_rated:
        fallback_items = Item.objects.filter(is_active=True).order_by('?')[:8]

    # Prepare response data
    data = {
        "new": [
            {
                "id": item.id,
                "name": item.name,
                "price": calculate_effective_price(item),
                "original_price": float(item.price),
                "discount_price": float(item.discount_price) if item.discount_price else None,
                "image": item.image.url if item.image else None,
            }
            for item in new_items
        ],
        "on_sale": [
            {
                "id": item.id,
                "name": item.name,
                "price": calculate_effective_price(item),
                "original_price": float(item.price),
                "discount_price": float(item.discount_price) if item.discount_price else None,
                "image": item.image.url if item.image else None,
            }
            for item in on_sale_items
        ],
        "best_sellers": [
            {
                "id": item.id,
                "name": item.name,
                "price": calculate_effective_price(item),
                "original_price": float(item.price),
                "discount_price": float(item.discount_price) if item.discount_price else None,
                "image": item.image.url if item.image else None,
            }
            for item in best_sellers
        ],
        "top_rated": [
            {
                "id": item.id,
                "name": item.name,
                "price": calculate_effective_price(item),
                "original_price": float(item.price),
                "discount_price": float(item.discount_price) if item.discount_price else None,
                "image": item.image.url if item.image else None,
            }
            for item in top_rated
        ],
        "fallback": [
            {
                "id": item.id,
                "name": item.name,
                "price": calculate_effective_price(item),
                "original_price": float(item.price),
                "discount_price": float(item.discount_price) if item.discount_price else None,
                "image": item.image.url if item.image else None,
            }
            for item in fallback_items
        ],
    }

    return JsonResponse(data)



def latest_items(request):
    latest_items = Item.objects.order_by('-date_added')[:5]
    data = {
        "latest_items": [
            {
                "id": item.id,
                "name": item.name,
                "price": float(item.price - (item.discount_price or 0)),
                "original_price": float(item.price),
                "discount_price": float(item.discount_price) if item.discount_price else None,
                "image": item.image.url if item.image else None,
            }
            for item in latest_items
        ]
    }
    return JsonResponse(data)
