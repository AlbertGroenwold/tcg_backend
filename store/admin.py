from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'image', 'release_date', 'contains')  # Show key fields
    search_fields = ('name', 'category')
    list_filter = ('category',)
    readonly_fields = ('id',)  # Make ID read-only in the admin panel
