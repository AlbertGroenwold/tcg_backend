from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Category,
    Item,
    CustomUser,
    Order,
    OrderDetail,
    Address,
    Supplier,
    Tag,
)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'date_created')  # Display name and creation date
    search_fields = ('name',)  # Allow search by name

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'get_full_hierarchy')
    search_fields = ('name',)
    list_filter = ('parent',)

    def get_full_hierarchy(self, obj):
        return str(obj)
    get_full_hierarchy.short_description = 'Full Hierarchy'

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'date_added')  # Fields to display in admin list view
    search_fields = ('name', 'contact_email')  # Fields to include in admin search
    list_filter = ('date_added',)  # Filters in admin panel

class CategoryInline(admin.TabularInline):
    """Inline display for categories related to an item."""
    model = Item.categories.through  # Access the through model for ManyToManyField
    extra = 1  # Number of empty inline forms to display
    verbose_name = "Category"
    verbose_name_plural = "Categories"

class TagInline(admin.TabularInline):
    """Inline display for tags related to an item."""
    model = Item.tags.through  # Access the through model for ManyToManyField
    extra = 1  # Number of empty inline forms to display
    verbose_name = "Tag"
    verbose_name_plural = "Tags"

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Custom admin interface for the Item model."""

    list_display = (
        'name', 'price', 'discount_price', 'stock', 'is_active', 'release_date', 'supplier', 'views', 'rating'
    )
    list_filter = (
        'is_active', 'categories', 'tags', 'supplier', 'release_date', 'date_added'
    )
    search_fields = ('name', 'sku', 'description')
    filter_horizontal = ('categories', 'tags')
    readonly_fields = ('date_added', 'views', 'rating', 'reviews_count')

    fieldsets = (
        ("General Information", {
            'fields': ('name', 'description', 'image', 'sku', 'categories', 'tags', 'supplier')
        }),
        ("Pricing and Stock", {
            'fields': ('price', 'discount_price', 'stock', 'weight', 'dimensions', 'contains')
        }),
        ("Additional Details", {
            'fields': ('release_date', 'is_active', 'date_added', 'views', 'rating', 'reviews_count')
        }),
    )

    #inlines = [CategoryInline, TagInline]

    def get_queryset(self, request):
        """Optimize the query for performance."""
        queryset = super().get_queryset(request)
        return queryset.select_related('supplier').prefetch_related('categories', 'tags')

    def supplier(self, obj):
        """Display supplier name in the admin list view."""
        return obj.supplier.name if obj.supplier else "None"

    supplier.short_description = "Supplier"

    def rating_display(self, obj):
        """Format rating with stars."""
        return f"{obj.rating} ★"  # Unicode for star

    rating_display.short_description = "Rating"


# Optional: Unregister the through models to clean up the admin
#admin.site.unregister(Item.categories.through)
#admin.site.unregister(Item.tags.through)


# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_staff', 'is_active')  # Customize User admin fields
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')},
         ),
    )


# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address_type', 'address', 'city', 'province', 'postal_code', 'country')
    list_filter = ('address_type', 'province', 'city')
    search_fields = ('address', 'city', 'postal_code', 'user__email')
    ordering = ('user', 'address_type')

    # Custom form to handle province as a dropdown and country defaulted to "South Africa"
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Province dropdown
        form.base_fields['province'].choices = [
            ("Eastern Cape", "Eastern Cape"),
            ("Free State", "Free State"),
            ("Gauteng", "Gauteng"),
            ("KwaZulu-Natal", "KwaZulu-Natal"),
            ("Limpopo", "Limpopo"),
            ("Mpumalanga", "Mpumalanga"),
            ("North West", "North West"),
            ("Northern Cape", "Northern Cape"),
            ("Western Cape", "Western Cape"),
        ]

        # Ensure country is always "South Africa" and not editable
        form.base_fields['country'].initial = "South Africa"
        form.base_fields['country'].disabled = True

        # User dropdown to select linked user
        form.base_fields['user'].queryset = CustomUser.objects.all()

        return form


# OrderDetail Inline (used within the Order admin)
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    fields = ('item', 'quantity', 'price')  # Show these fields in the inline view
    readonly_fields = ('price',)  # Make price read-only


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'payment_status', 'fulfillment_status', 'total', "address")
    list_filter = ('payment_status', 'fulfillment_status')
    search_fields = ('user__email', 'id')
    inlines = [OrderDetailInline]  # Include the OrderDetail inline


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', 'price')
    search_fields = ('order__id', 'item__name')
    list_filter = ('order__id',)
    readonly_fields = ('price',)  # Prevent changes to price directly
    ordering = ('-order',)  # Show most recent orders first


# Register CustomUser with the customized admin class
admin.site.register(CustomUser, CustomUserAdmin)
