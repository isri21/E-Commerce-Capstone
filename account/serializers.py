from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wishlist
from store.models import Purchase

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

# Serializer for purchases
class ProfilePurchasesSerialzier(serializers.ModelSerializer):
	purchase_id = serializers.IntegerField(source="id")
	product = serializers.CharField(source="product.name")
	purchase_price = serializers.IntegerField(source="price")
	purchase_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
	class Meta:
		model = Purchase
		fields = ["purchase_id", "product", "discount", "purchase_price", "quantity", "purchase_date"]
