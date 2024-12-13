from rest_framework.decorators import api_view
from .serializers import ItemSerializer
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Item
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

def home(request):
    return redirect('/admin')

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
    def get(self, request, username):
        try:
            # Replace 'username' with 'email' if using email as the unique identifier
            user = User.objects.get(email=username)  # Adjust query to match your identifier
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)