from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Category,
    Item,
    CustomUser,
    Order,
    OrderDetail,
    Address,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'get_full_hierarchy')
    search_fields = ('name',)
    list_filter = ('parent',)

    def get_full_hierarchy(self, obj):
        return str(obj)
    get_full_hierarchy.short_description = 'Full Hierarchy'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'image', 'release_date', 'contains')
    search_fields = ('name',)
    list_filter = ('categories',)
    filter_horizontal = ('categories',)  # Allow easy selection of categories in the admin panel
    readonly_fields = ('id',)


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
