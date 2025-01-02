from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wishlist

# Get the user model
User = get_user_model()

# Serializer for the user profile
class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["username", "first_name", "last_name", "email"]
		read_only_fields = ["username"] # Set username to read only

# Serializer for wishlist
class WishListSerializer(serializers.ModelSerializer):
	product = serializers.CharField(source="product.name")
	wishlisted_at = serializers.DateField(format="%Y-%m-%d")
	class Meta:
		model = Wishlist
		fields = ["id", "product", "wishlisted_at"]