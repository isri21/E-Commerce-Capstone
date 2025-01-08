from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from django.apps import apps

class User(AbstractUser):
	@property
	def products_purchased(self):
		Purchase = apps.get_model("store", "Purchase")
		total_purchase = Purchase.objects.filter(user=self.id).aggregate(purchase_num=Count("user"))
		return total_purchase

	@property
	def products_reviewed(self):
		Review = apps.get_model("account", "Review")
		total_review = Review.objects.filter(user=self.id).aggregate(review_num=Count("user"))
		return total_review
	@property
	def products_rated(self):
		Rating = apps.get_model("account", "Rating")
		total_rating = Rating.objects.filter(user=self.id).aggregate(rating_num=Count("user"))
		return total_rating

	@property
	def products_posted(self):
		Product = apps.get_model("store", "Product")
		total_posted = Product.objects.filter(owner=self.id, is_deleted=False).aggregate(post_num=Count("owner"))
		return total_posted

	@property
	def products_in_wishlist(self):
		Wishlist = apps.get_model("account", "Wishlist")
		total_wishlist = Wishlist.objects.filter(user=self.id).aggregate(wish_list=Count("user"))
		return total_wishlist

	@property
	def categories_created(self):
		Category = apps.get_model("store", "Category")
		total_categories = Category.objects.filter(creator=self.id).aggregate(category_count=Count("creator"))
		return total_categories

	@property
	def money_spent(self):
		Purchase = apps.get_model("store", "Purchase")
		purchases = Purchase.objects.filter(user=self.id)
		total_spent = 0
		for purchase in purchases:
			total_spent += purchase.total_price
		return total_spent

	@property
	def money_earned(self):
		Purchase = apps.get_model("store", "Purchase")
		purchases =  Purchase.objects.filter(product__owner=self.id)
		total_earned = 0
		for purchase in purchases:
			total_earned += purchase.total_price

		return total_earned