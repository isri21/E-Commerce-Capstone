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

	# # Custom structure of the output data
	def to_representation(self, instance):
		# Check if the only_profile key is passed as a context, this will be passed when using serializer for updating data
		only_profile = self.context.get("only_profile", False)
		# Call the main to_representation method
		data =  super().to_representation(instance)
		# Prepare a profile_details dict for grouping fields
		profile_details = {}
		# Move fields realted to profile info to product_detials dict
		profile_details["username"] = data.pop("username")
		profile_details["first_name"] = data.pop("first_name")
		profile_details["last_name"] = data.pop("last_name")
		profile_details["email"] = data.pop("email")
		
		# Add the profile_detials dict to the output data dict
		data["profile_details"] = profile_details

		# Check if the only_profile key is False, meaning it was not specified
		if only_profile == False:
			# Prepare a financial_details and stats dict for grouping fields
			financial_details = {}
			stats = {}

			# Move fields realted to finance info to financial_detials dict
			financial_details["money_spent"] = str(data.pop("money_spent")) + " ETB"
			financial_details["money_earned"] = str(data.pop("money_earned")) + " ETB"

			# Move fields realted to statistical info to stats dict
			stats["products_purchased"] = data.pop("products_purchased")
			stats["products_reviewed"] = data.pop("products_reviewed")
			stats["products_rated"] = data.pop("products_rated")
			stats["products_posted"] = data.pop("products_posted", 0)
			stats["products_in_wishlist"] = data.pop("products_in_wishlist")
			stats["categories_created"] = data.pop("categories_created")
			
			# Add the financial_details and stats dict to the output data dict
			data["financial_details"] = financial_details
			data["stats"] = stats

			# Return the entire output data dict
			return data
		
		# Return only the profile_details (when serializer used for update)
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
