from rest_framework import serializers
from .models import *
from account.models import *
from django.db.utils import IntegrityError
from rest_framework import status
import os

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
class ViewDetailProdcutSerializer(serializers.ModelSerializer):
	original_price = serializers.IntegerField(source="price") # Change the name of the price field to original price
	posted_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", source="created_at") # Change the name of the created_date field to posted_at
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
			"posted_at",
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
	# Format the dates
	review_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", read_only=True)
	edited_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", read_only=True)
	review_id = serializers.CharField(source="id", read_only=True)
	class Meta:
		model = Review
		fields = ["review_id", "user", "product", "review", "review_date", "edited_at"]

	# Create custom create method
	def create(self, validated_data):
		# Try to create the review, if integrity error is raised, return an error stating that.
		try:
			return Review.objects.create(**validated_data)
		except IntegrityError:
			res = serializers.ValidationError({"error": "You have already reviewed this product."})
			res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
			raise res # raise the validation error with the custom exception.
		
	def update(self, instance, validated_data):
		# Get the review from the validated data
		updated_review = validated_data["review"]

		# Update the reiview of the instance
		instance.review = updated_review
		instance.save()
		
		return instance
	
	def to_representation(self, instance):
		data =  super().to_representation(instance)

		# Check if the include user context was passed
		# If passed it will be sent ase {"include_user": False}
		# If we it is False remove it from serializer.data, if it is not specified keep it
		include_user = self.context.get("include_user", True)
		include_id = self.context.get("include_id", True)
		if not include_user:
			data.pop("user")
		
		if not include_id:
			data.pop("id")

		return data


# Serializer for the review model
class RatingSerializer(serializers.ModelSerializer):
	# Display the actual name of the user, instead of it's id
	user = serializers.CharField(source="user.username", read_only=True)
	# Display the actual name of the product, instead of it's id
	product = serializers.CharField(source="product.name", read_only=True)
	# Format the dates 
	rating_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", read_only=True)
	edited_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", read_only=True)
	class Meta:
		model = Rating
		fields = ["id", "user", "product", "rating", "rating_date", "edited_at"]
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
		
	def update(self, instance, validated_data):
		# Get the rating from the validated data
		updated_rating = validated_data["rating"]

		# Update the reiview of the instance
		instance.rating = updated_rating
		instance.save()
		
		return instance
	
	def to_representation(self, instance):
		data =  super().to_representation(instance)

		# Check if the include user context was passed
		# If passed it will be sent ase {"include_user": False}
		# If we it is False remove it from serializer.data, if it is not specified keep it
		include_user = self.context.get("include_user", True)
		include_id = self.context.get("include_id", True)
		if not include_user:
			data.pop("user")
		
		if not include_id:
			data.pop("id")

		return data
			
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
		except IntegrityError:
			res = serializers.ValidationError({"name": "There already exists a category with this name."})
			res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
			raise res # raise the validation error with the custom exception.
		return category
	
	def update(self, instance, validated_data):
		# convert the name sent in request to lower case
		print(validated_data)
		validated_data["name"] = validated_data.get("name").lower()

		# Try to update the instance name
		try:
			instance.name = validated_data["name"]
			instance.save()
		except IntegrityError:
			res = serializers.ValidationError({"name": "There already exists a category with this name."})
			res.status_code = status.HTTP_409_CONFLICT # Specify custom status code for the validaiton error
			raise res # raise the validation error with the custom exception.
	
		return instance
	
	# Capitalize the category name when sending it back in the response, or when serializing it.
	def to_representation(self, instance):
		data = super().to_representation(instance)
		data["name"] = data["name"].capitalize()
		return data
	
# Serializer for the list view of all the products
class GeneralProductsSerializer(serializers.ModelSerializer):
	images = ImageSerializer(many=True)
	category = CategorySerializer(many=True)
	class Meta:
		model = Product
		fields = ["id",	"name", "images", "category", "stock_quantity"]


# Serializer for creating a product
class CreateProductSerialzier(serializers.ModelSerializer):
	original_price = serializers.IntegerField(source="price") # Change the name of the price field to original price
	posted_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S (%p)", source="created_at", read_only=True) # Change the name of the created_date field to posted_at
	images = serializers.ListField(child=serializers.ImageField()) # Use a list field since the image will be sent as a list
	category = serializers.ListField(child=serializers.CharField(), write_only=True) # Use a list field since the categories will be sent as a list
	discount_percent = serializers.IntegerField(source="discount") # Change the name of the discount field to discount_percent
	class Meta:
		model = Product
		fields = [
			"id", "owner", "name",	"description",	"original_price", "discount_percent",
			"final_price", "stock_quantity", "category", "images", "posted_at"
		]
		read_only_fields = ["owner"]

	# Check if the price entered is greater than 0
	def validate_original_price(self, value):
		if value <= 0:
			raise serializers.ValidationError("Must be a number greater than 0.")
		return value
	
	# Check if the discount percent is between 0 and 100
	def validate_discount_percent(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError("Must be a percentage value between 0 and 100.")
		return value
	
	# Check if the stock quantity is not less than 0
	def validate_stock_quantity(self, value):
		if value < 0:
			raise serializers.ValidationError("Can not be a number less than 0.")
		return value

	# Check if the categories specifed all exist
	def validate_category(self, value):
		for category in value:
			category_lower = category.lower()
			try:
				Category.objects.get(name=category_lower)
			except Category.DoesNotExist:
				print(category)
				raise serializers.ValidationError({f"{category}": "This category does not exist. If you want to use it, create it first."})
		return value
	
	# Check if the image is jpg or png
	def validate_images(self, value):
		for image in value:
			if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
				raise serializers.ValidationError(f"[{os.path.basename(image.name)}] is not a JPG, JPEG or PNG file.")
		return value

	def create(self, validated_data):
		print(validated_data)
		# Extract and remove images and category from validated data
		images = validated_data.pop("images")
		category = validated_data.pop("category")

		# Create the product instance				
		product = Product.objects.create(**validated_data)

		# Add the categories to the product
		for item in category:
			category_item = Category.objects.get(name=item.lower())
			product.category.add(category_item)

		# Relate the images with the product
		for image in images:
			try:
				Image.objects.create(product=product, image=image)
			except Exception as e:
				raise serializers.ValidationError(f"Unable to create image: {e}")
		return product
	
	def update(self, instance, validated_data):
		# Remove category and images from the validated_data if they exist
		categories = validated_data.pop("category", None)
		images = validated_data.pop("images", None)

		# Save the rest of the validated_data
		for field, value in validated_data.items():
			setattr(instance, field, value)

		# If category exist 
		if categories:
			# Remove their previous relations
			instance.category.clear()
	
			# Creat new relation with new categoires
			for category in categories:
				category_item = Category.objects.get(name=category.lower())
				instance.category.add(category_item)
		
		# Save the instance
		instance.save()

		# If images exist 
		if images:
			# Delete the previous product image relation
			Image.objects.filter(product=instance).delete()

			# Creat the relation again.
			for image in images:
				try:
					Image.objects.create(product=instance, image=image)
				except Exception as e:
					raise serializers.ValidationError(f"Unable to create image: {e}")
				
		return instance
				
	
	def to_representation(self, instance):
		# When calling .data attribute only return the id of the instance created/updated
		# This is used to use another serializer to serialize the detail product.
		data = {"id": instance.id}
		return data