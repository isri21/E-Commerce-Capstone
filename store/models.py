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
		return total_ratings["total_rates"]

	@property
	def no_of_reviews(self):
		Review = apps.get_model("account", "Review")
		total_reviews = Review.objects.filter(product=self.id).aggregate(total_review=Count("review"))
		return total_reviews["total_review"]

	@property
	def avg_rating(self):
		Rating = apps.get_model("account", "Rating")

		avg_ratings = Rating.objects.filter(product=self.id).aggregate(avg_rates=Avg("rating"))
		return avg_ratings["avg_rates"]

	@property
	def total_items_sold(self):
		total_sold = Purchase.objects.filter(product=self.id).aggregate(total_sell=Sum("quantity"))
		return total_sold["total_sell"]

	@property
	def profit_made(self):
		# Usinf F object to calculate total price and then aggregating the sum of the total prices
		profit_made = Purchase.objects.filter(product=self.id).annotate(total_price=Case(
			When(discount__exact=0, then=F("price") * F("quantity")), # If the discount is 0, then just multiply price and quantity
			default=(F("discount")/100) * F("price") * F("quantity"), # Else divide discount by 100 and then multiply by price and quantity
			output_field=DecimalField()
		)).aggregate(total_profit=Sum("total_price"))
		return profit_made["total_profit"]
	
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