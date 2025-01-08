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
		fields = [
			"username", "first_name", "last_name", "email",
			"products_purchased", "products_reviewed", "products_rated", "products_posted",
			"products_in_wishlist", "categories_created", "money_spent", "money_earned"
		]
		read_only_fields = [
			"username", "products_purchased", "products_reviewed", "products_rated",
			"products_posted", "products_in_wishlist", "categories_created", "money_spent", "money_earned"
		]

	def to_representation(self, instance):
		only_profile = self.context.get("only_profile", False)
		data =  super().to_representation(instance)
		profile_details = {}
		financial_details = {}
		stat = {}
		profile_details["username"] = data.pop("username")
		profile_details["first_name"] = data.pop("first_name")
		profile_details["last_name"] = data.pop("last_name")
		profile_details["email"] = data.pop("email")
		data["profile_details"] = profile_details
		if not only_profile:
			financial_details["money_spent"] = str(data.pop("money_spent")) + " ETB"
			financial_details["money_earned"] = str(data.pop("money_earned")) + " ETB"

			stat["products_purchased"] = data.pop("products_purchased")
			stat["products_reviewed"] = data.pop("products_reviewed")
			stat["products_rated"] = data.pop("products_rated")
			stat["products_posted"] = data.pop("products_posted", 0)
			stat["products_in_wishlist"] = data.pop("products_in_wishlist")
			stat["categories_created"] = data.pop("categories_created")
			
			data["financial_details"] = financial_details
			data["stat"] = stat
		
		return data["profile_details"]

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
	purchase_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", read_only=True)
	class Meta:
		model = Purchase
		fields = ["purchase_id", "product", "discount", "purchase_price", "quantity", "purchase_date"]
