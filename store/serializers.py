from .models import Item, CustomUser, UserProfile, Order, OrderDetail
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Item Serializer
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'price', 'stock', 'image']

# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['primary_address', 'secondary_address']  # Removed order_ids, as orders are linked via Order model

# Custom User Serializer
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['email', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Encrypt the password
        user.save()

        # Create a UserProfile linked to this user
        UserProfile.objects.create(user=user, **profile_data)
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



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            # Use username internally for SimpleJWT
            attrs["username"] = user.email
            return super().validate(attrs)

        raise serializers.ValidationError({"error": "Invalid email or password."})

