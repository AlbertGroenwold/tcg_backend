from .models import Item, CustomUser, Order, OrderDetail, Category, Address
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']  # Include parent for nested hierarchy


# Item Serializer
class ItemSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)  # Include related categories

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'stock', 'image', 'release_date', 'contains', 'categories']


# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'address', 'city', 'province', 'postal_code', 'country']

    def validate(self, data):
        user = self.context['request'].user  # Access the user from the request context
        address_type = data.get('address_type')

        # Ensure only one primary or secondary address exists
        if Address.objects.filter(user=user, address_type=address_type).exists():
            raise serializers.ValidationError(
                f"{address_type.capitalize()} address already exists for this user."
            )
        return data


# Custom User Serializer
class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, source='address_set')  # Include related addresses

    class Meta:
        model = CustomUser
        fields = ['email', 'addresses']  # Include the user’s email and addresses

    def create(self, validated_data):
        address_data = validated_data.pop('address_set', [])
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Encrypt the password
        user.save()

        # Create linked addresses
        for address in address_data:
            Address.objects.create(user=user, **address)
        return user


# Order Detail Serializer
class OrderDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer()  # Serialize the related Item object

    class Meta:
        model = OrderDetail
        fields = ['id', 'item', 'quantity', 'price']


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, source='order_details.all')

    class Meta:
        model = Order
        fields = ['id', 'date', 'payment_status', 'fulfillment_status', 'total', 'order_details']


# Custom Token Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            # Use email internally for SimpleJWT
            attrs["username"] = user.email
            return super().validate(attrs)

        raise serializers.ValidationError({"error": "Invalid email or password."})


