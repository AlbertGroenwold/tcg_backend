from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ItemSerializer
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Item

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