from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from django.apps import apps # <= Used to get models while avoiding circular imports

class User(AbstractUser):
	@property
	def products_purchased(self):
		# Get the Purchase model
		Purchase = apps.get_model("store", "Purchase")
		# Get the Count the number of times a user purchased an item
		total_purchase = Purchase.objects.filter(user=self.id).aggregate(purchase_num=Count("user"))
		# Return the actual value rather than the dict
		return total_purchase["purchase_num"]

	@property
	def products_reviewed(self):
		# Get the Review model
		Review = apps.get_model("account", "Review")
		
		# Get the number of items a user reviewd
		total_review = Review.objects.filter(user=self.id).aggregate(review_num=Count("user"))

		# Return the actual value rather than the dict
		return total_review["review_num"]
	@property
	def products_rated(self):
		# Get the Rating  model
		Rating = apps.get_model("account", "Rating")

		# Get the number of items a user rated
		total_rating = Rating.objects.filter(user=self.id).aggregate(rating_num=Count("user"))

		# Return the actual value rather than the dict
		return total_rating["rating_num"]

	@property
	def products_posted(self):
		# Get the Product model
		Product = apps.get_model("store", "Product")

		# From the product model get the number of product the user owns that is not deleted
		total_posted = Product.objects.filter(owner=self.id, is_deleted=False).aggregate(post_num=Count("owner"))
		
		# Return the actual value rather than the dict
		return total_posted["post_num"]

	@property
	def products_in_wishlist(self):
		# Get the Wishlist Model
		Wishlist = apps.get_model("account", "Wishlist")

		# Get the number of products in the wishlist by the user
		total_wishlist = Wishlist.objects.filter(user=self.id).aggregate(wish_list=Count("user"))
		
		# Return the actual value rather than the dict
		return total_wishlist["wish_list"]

	@property
	def categories_created(self):
		# Get the Category model
		Category = apps.get_model("store", "Category")

		# From the category model get the categories created by the user
		total_categories = Category.objects.filter(creator=self.id).aggregate(category_count=Count("creator"))
		
		# Return the actual value rather than the dict
		return total_categories["category_count"]

	@property
	def money_spent(self):
		# Get the Purchase model
		Purchase = apps.get_model("store", "Purchase")

		# Filter the Purhcase records by the user
		purchases = Purchase.objects.filter(user=self.id)

		# Initialize a variable to calculate total spending
		total_spent = 0

		# Loop through each purchase record and get the total price attribute, then add it to the total spent variable
		for purchase in purchases:
			total_spent += purchase.total_price

		# Return the money total_spent
		return total_spent

	@property
	def money_earned(self):
		# Get the Purchase model
		Purchase = apps.get_model("store", "Purchase")

		# Filter the Purhcase records by the product whose owner is the user
		purchases =  Purchase.objects.filter(product__owner=self.id)

		# Initialize a variable to calculate total earning
		total_earned = 0

		# Loop through each purchase record and get the total price attribute, then add it to the total earning variable
		for purchase in purchases:
			total_earned += purchase.total_price

		# Return the total earning
		return total_earned