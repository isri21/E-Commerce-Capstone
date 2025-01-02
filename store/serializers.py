from rest_framework import serializers
from .models import *
from account.models import *
from django.db import IntegrityError
from rest_framework import status

# Serializer for the Image model to be nested into the GeneralProductsSerializer
class ImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Image
		fields = ["image"] # Only include the image field of the model

	# On deserialization return only the image url as a string, not the image object.
	def to_representation(self, instance):
		data = super().to_representation(instance)
		return data["image"]

# Serializer for the Category model to be nested into the GeneralProductsSerializer
class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["name"] # Only include the name field of the model

	# On deserialization return only the image url as a string, not the image object.
	def to_representation(self, instance):
		data = super().to_representation(instance)
		return data["name"]


# Serializer for the list view of all the products
class GeneralProductsSerializer(serializers.ModelSerializer):
	images = ImageSerializer(many=True)
	category = CategorySerializer(many=True)
	class Meta:
		model = Product
		fields = ["id",	"name", "images", "category", "stock_quantity"]


# Serializer for detail view of specific products
class DetailProdcutSerializer(serializers.ModelSerializer):
	original_price = serializers.IntegerField(source="price") # Change the name of the price field to original price
	posted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", source="created_at") # Change the name of the created_date field to posted_at
	images = ImageSerializer(many=True) 
	category = CategorySerializer(many=True)
	discount_percent = serializers.IntegerField(source="discount") # Change the name of the discount field to discount_percent
	class Meta:
		model = Product
		fields = [
			"id",
			"owner",
			"name",
			"description",
			"original_price",
			"discount_percent",
			"final_price",
			"stock_quantity",
			"category",
			"images",
			"posted_at"
		]

# Serializer for purchasing products
class PurchaseSerializer(serializers.ModelSerializer):
	# Display the actual name of the user, insted of it's id
	user = serializers.CharField(source="user.username", read_only=True)
	# Display the actual name fo the product, instead of it's id
	product = serializers.CharField(source="product.name", read_only=True)
	# Use the final price derived from the discount and original_price and name the field "purchase_price"
	purchase_price = serializers.DecimalField(source="price", max_digits=6, decimal_places=2, read_only=True)
	# Format the data time field as YYYY-MM-DD HH-MM-SS
	purchase_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
	
	class Meta:
		model = Purchase
		fields = ["user", "product", "purchase_price", "discount", "quantity", "purchase_date"]
		read_only_fields = ["user", "product", "purchase_price", "discount", "purchase_date"]

	# Validate the quantity that the user entered
	def validate_quantity(self, value):
		product = self.context["product"] # Get the product form the context passed during serializer instantiation
		if value <= 0: # Check if quantity is not greater than 0
			raise serializers.ValidationError("Purchase amount must be greater than 0.")
		if value > product.stock_quantity: # Check if the quantity enetered is not greater than the avalable stock of the prodcut
			raise serializers.ValidationError(f"The amount you specified is greater than the available stock, which is {product.stock_quantity}")
		return value

	# Custom create method for purchase
	def create(self, validated_data):
		user = self.context["request"].user # Get the user from the context provided during serializer instantiation
		product = self.context["product"] # Get the product form the context passed during serializer instantiation

		# Create the purchase, using the user, product, and quantity the user specified
		purchase = Purchase.objects.create(
			user=user,
			product=product,
			price=product.final_price, # Set the purchase price to the final_price of the product
			discount=product.discount,
			**validated_data
		)

		# After creating the purchase, reduce the avaliable stock quantity of the product by the amount purchased
		product.stock_quantity -= validated_data.get("quantity")
		product.save() # Save the product instance
		return purchase # Return the purchase object
	
	# Modify the presentaiton of data
	def to_representation(self, instance):
		data = super().to_representation(instance)
		purchase_price = float(data["purchase_price"]) # Set a purchase price variable with a float value of the purchase price
		data["purchase_price"] = purchase_price # Convert the purchase price into a float type
		return {"message": "Purchase Successful", "purchase_info": data} # Return custom strucutre

# Serializer for the review model
class ReviewSerializer(serializers.ModelSerializer):
	# Display the actual name of the user, instead of it's id
	user = serializers.CharField(source="user.username", read_only=True)
	# Display the actual name of the product, instead of it's id
	product = serializers.CharField(source="product.name", read_only=True)
	class Meta:
		model = Review
		fields = ["user", "product", "review", "review_date", "edited_at"]
		# Specify read only fields
		read_only_fields = ["review_date", "edited_at"]

	# Create custom create method
	def create(self, validated_data):
		# Try to create the review, if integrity error is raised, return an error stating that.
		try:
			return Review.objects.create(**validated_data)
		except IntegrityError:
			res = serializers.ValidationError({"error": "You have already reviewed this product."})
			res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
			raise res # raise the validation error with the custom exception.

# Serializer for the review model
class RatingSerializer(serializers.ModelSerializer):
	# Display the actual name of the user, instead of it's id
	user = serializers.CharField(source="user.username", read_only=True)
	# Display the actual name of the product, instead of it's id
	product = serializers.CharField(source="product.name", read_only=True)
	class Meta:
		model = Rating
		fields = ["user", "product", "rating", "rating_date", "edited_at"]
		# Specify read only fields
		read_only_fields = ["rating_date", "edited_at"]

	# Create custom create method
	def create(self, validated_data):
		# Try to create the review, if integrity error is raised, return an error stating that.
		try:
			return Rating.objects.create(**validated_data)
		except IntegrityError as e:
			# Since if it is a unique constraint error raised the follwoing string will be in that error -
			# message we set it to a variable.
			unique_constraint_error = "UNIQUE constraint failed: account_rating.product_id, account_rating.user_id"
			# Check if the exception raised was a unique constraint error
			if unique_constraint_error in str(e):
				res = serializers.ValidationError({"error": "You have already rated this product."})
				res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
				raise res # raise the validation error with the custom exception.
			else: # Else it must be a check constraint error
				raise serializers.ValidationError({"rating": "Value must be between 1 and 10."})
			
class DetailCategorySerializer(serializers.ModelSerializer):
	creator = serializers.CharField(source="creator.username", read_only=True)
	class Meta:
		model = Category
		fields = ["id", "creator", "name"]
		read_only_fields = ["id"]

	# Custom created method
	def create(self, validated_data):
		user = validated_data.pop("user") # get the user object passed during .save()
		name = validated_data.get("name").lower() # convert the name sent in request to lower case

		# Try to create the category object, if unable return error
		# Reason converted to lower case is to check for duplicates, and since -
		# there is unique constraint on the field if unable to create the category -
		# the reason is duplicate names.
		try:
			category = Category.objects.create(creator=user, name=name)
		except IntegrityError as e:
			res = serializers.ValidationError({"name": "There already exists a category with this name."})
			res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
			raise res # raise the validation error with the custom exception.
		return category
	
	def update(self, instance, validated_data):
		# convert the name sent in request to lower case
		validated_data["name"] = validated_data.get("name").lower()

		for field, value in validated_data.items():
			try:
				setattr(instance, field, value)
			except IntegrityError as e:
				res = serializers.ValidationError({"name": "There already exists a category with this name."})
				res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
				raise res # raise the validation error with the custom exception.
		instance.save()
		return instance
	
	# Capitalize the category name when sending it back in the response, or when serializing it.
	def to_representation(self, instance):
		data = super().to_representation(instance)
		data["name"] = data["name"].capitalize()
		return data