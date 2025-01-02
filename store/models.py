from django.db import models
from django.contrib.auth import get_user_model
import os

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
	

# Product Model
class Product(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField()
	price = models.DecimalField(max_digits=6, decimal_places=2)
	discount = models.PositiveIntegerField()
	stock_quantity = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	category = models.ManyToManyField(Category, through="Product_Category", related_name="products")
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_products")
	is_deleted = models.BooleanField(default=False)

	@property
	def final_price(self):
		if self.discount:
			discounted_price = float(self.price) - ((self.discount/100) * float(self.price))
			return discounted_price
		else:
			return self.price
		
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

	def __str__(self):
		return f"{self.user.username} | {self.product.name[:20]}"