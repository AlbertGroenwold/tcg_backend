from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from django.shortcuts import redirect

def home(request):
    return redirect('/api/items/')

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

