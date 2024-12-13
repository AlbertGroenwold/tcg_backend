from .models import Item
from rest_framework import serializers
from .models import CustomUser, UserProfile

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'category']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['primary_address', 'secondary_address', 'order_ids']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Encrypt the password
        user.save()

        UserProfile.objects.create(user=user, **profile_data)
        return user