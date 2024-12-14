from .models import Item, CustomUser, UserProfile, Order, OrderDetail
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'image', 'release_date', 'contains')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    readonly_fields = ('id',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_address', 'secondary_address')
    search_fields = ('user__email', 'primary_address', 'secondary_address')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)  # Link UserProfile with CustomUser in the admin
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


# OrderDetail Inline (used within the Order admin)
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    fields = ('item', 'quantity', 'price')  # Show these fields in the inline view
    readonly_fields = ('price',)  # Make price read-only


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'payment_status', 'fulfillment_status', 'total')
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
