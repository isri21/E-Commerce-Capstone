from django.db import models
from django.db.models import Q
from store.models import Product
from django.contrib.auth import get_user_model


User = get_user_model()
# Create your models here.

class Review(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewed")
	review = models.TextField()
	review_date = models.DateTimeField(auto_now_add=True)
	edited_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["product", "user"], name="unique_product_user_review")
		]

	def __str__(self):
		return f"{self.user.username} - {self.review[:20]}"
	

class Rating(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rated")
	rating = models.DecimalField(max_digits=2, decimal_places=1)
	rating_date = models.DateTimeField(auto_now_add=True)
	edited_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["product", "user"], name="unique_product_user_rating"),
			models.CheckConstraint(check=Q(rating__gte=1) & Q(rating__lte=10), name="rating_between_1_&_10")
		]

	def __str__(self):
		return f"{self.user.username} - {self.product.name[:20]} | {self.rating}"
	
class Wishlist(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
	wishlisted_at = models.DateField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["product", "user"], name="unique_product_user_wishlis")
		]

	def __str__(self):
		return f"{self.user.username} - {self.product.name}"
