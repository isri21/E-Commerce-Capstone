from django.db import models
from django.contrib.auth import get_user_model
import os
from django.db.models import Count, Avg, Sum, F, Case, When, DecimalField
from django.apps import apps # Used to get models without causing circular imports

User = get_user_model()
# Create your models here. 
# Image model

# Category name
class Category(models.Model):
	name = models.CharField(max_length=100)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	is_deleted = models.BooleanField(default=False)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["name"], name="unique_category_name")
		]

	def __str__(self):
		return self.name
	
	@property
	def no_products(self):
		products = Product_Category.objects.filter(category__name=self.name).aggregate(product_no=Count("id"))
		return products["product_no"]
	

# Product Model
class Product(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField()
	price = models.DecimalField(max_digits=6, decimal_places=2)
	discount = models.PositiveIntegerField()
	stock_quantity = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	category = models.ManyToManyField(Category, through="Product_Category", related_name="products", blank=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_products")
	is_deleted = models.BooleanField(default=False)

	@property
	def final_price(self):
		if self.discount:
			discounted_price = float(self.price) - ((self.discount/100) * float(self.price))
			return float(f"{discounted_price:.2f}")
		else:
			discounted_price = self.price
			return float(f"{discounted_price:.2f}")
		
	@property
	def no_of_ratings(self):
		Rating = apps.get_model("account", "Rating")
		total_ratings = Rating.objects.filter(product=self.id).aggregate(total_rates=Count("rating"))
		if total_ratings["total_rates"]:
			rating = total_ratings["total_rates"]
		else:
			rating = 0
		return float(rating)

	@property
	def no_of_reviews(self):
		Review = apps.get_model("account", "Review")
		total_reviews = Review.objects.filter(product=self.id).aggregate(total_review=Count("review"))
		if total_reviews["total_review"]:
			reviews = total_reviews["total_review"]
		else:
			reviews = 0
		return float(reviews)

	@property
	def avg_rating(self):
		Rating = apps.get_model("account", "Rating")

		avg_ratings = Rating.objects.filter(product=self.id).aggregate(avg_rates=Avg("rating"))
		if avg_ratings["avg_rates"]:
			average = avg_ratings["avg_rates"]
		else:
			average = 0
		return float(average)

	@property
	def total_items_sold(self):
		total_sold = Purchase.objects.filter(product=self.id).aggregate(total_sell=Sum("quantity"))
		if total_sold["total_sell"]:
			total = total_sold["total_sell"]
		else:
			total = 0
		return float(total)

	@property
	def profit_made(self):
		Purchase = apps.get_model("store", "Purchase")
		purchases =  Purchase.objects.filter(product=self.id)
		total_profit = 0
		for purchase in purchases:
			total_profit += purchase.total_price

		return total_profit
	
	def __str__(self):
		return self.name

def image_upload(instance, filename):
	"""
	Creates a custom path for the upload image
	Returns:
	str: the custom url for the path
	"""
	# Path will look like media/users/{user_name}/products/{product_id}/file.jpg
	return os.path.join("users", str(instance.product.owner.username), "products", str(instance.product.id), filename)

class Image(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
	image = models.ImageField(upload_to=image_upload)

	def __str__(self):
		return self.product.name

# Product_Category Many to Many field
class Product_Category(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_category")
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_product")

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["product", "category"], name="unique_product_category")
		]

	def __str__(self):
		return f"{self.product.name[:20]} | {self.category.name[:20]}"
	

# Purchase table
class Purchase(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	discount = models.PositiveIntegerField()
	quantity = models.PositiveIntegerField()
	purchase_date = models.DateTimeField(auto_now_add=True)

	@property
	def total_price(self):
		if self.discount == 0:
			return (float(self.price) * float(self.quantity))
		return ((1 - float(self.discount/100)) * float(self.quantity) * float(self.price))

	def __str__(self):
		return f"{self.user.username} | {self.product.name[:20]}"