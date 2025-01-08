from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import *
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from store.serializers import DetailCategorySerializer, ReviewSerializer, RatingSerializer, GeneralProductsSerializer, CreateProductSerialzier, ViewDetailProdcutSerializer
from store.functions import BasicPagination
from store.models import Product, Category, Product_Category, Purchase
from .models import Wishlist, Review, Rating

User = get_user_model()


# View for viewing and updating user profile
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def profile_info(request):
	# Get the user
	user = request.user

	# Logic for GET method
	if request.method == "GET":
		serialized = ProfileSerializer(user) # Instantiate serializer with user data
		return Response(serialized.data, status=status.HTTP_200_OK) # Return serialized data
	
	# Logic for PATCH method
	if request.method == "PATCH":
		# Check if request data is empty
		if not request.data:
			return Response({
				"field": "No update fields were specified."
			}, status=status.HTTP_400_BAD_REQUEST)

		# Instantiate serializer, while binding it to the user object and allowing partial fields
		serialized = ProfileSerializer(instance=user, data=request.data, partial=True, context={"only_profile": True})
		if serialized.is_valid(raise_exception=True): # Check if the data sent is valid
			# If data is valid, save it and return the serialized data, along with a success message
			serialized.save()
			return Response({
				"status": f"Update succesfull.",
				"updated_profile": serialized.data
			}, status=status.HTTP_200_OK)
		

# View for viewing and creating categoies
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def list_create_categories(request):
	# Get user
	user = request.user

	# Logic for GET method
	if request.method == "GET":
		# instantiate the custom paginator
		paginator = BasicPagination()

		# fetch the products the user created using prefetch_related for optimization, and only show product that are not marked deleted
		categories = Category.objects.filter(creator=user, is_deleted=False)

		# Check if the product queryset is not empty
		if not categories.exists():
			# If it is empty, return a 404 NOT FOUND
			return Response({
				"no_categories": "You have not created any products yet."
			}, status=status.HTTP_204_NO_CONTENT)

		# Serialize the paginated queryset
		paginted = paginator.paginate_queryset(categories, request)
		serializer = DetailCategorySerializer(paginted, many=True)

		# Reutrn the serialized quieryset
		return paginator.get_paginated_response(serializer.data)

	# Logic for POST method
	if request.method == "POST":
		user = request.user
		# Instantiate an IsAuthenticated Instance
		permission = IsAuthenticated()
		# Check if user doesn't have permission, if not return error
		if not permission.has_permission(request, None):
			return Response({
				"detail": "Authentication credentials were not provided."
			}, status=status.HTTP_401_UNAUTHORIZED)

		# Deserialize incoming data
		serializer = DetailCategorySerializer(data=request.data)
		# Check if incoming data is valid, if it save and return it, else return error (raise_exception=True)
		if serializer.is_valid(raise_exception=True):
			serializer.save(user=user)
			return Response({
				"status": "You have successfully created the category.",
				"category": serializer.data
			}, status=status.HTTP_200_OK)


# View for updating and deleting categoies
@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def manage_categories(request, id):

	# Try to get the cateogry if it exist, else return an error
	try:
		category = Category.objects.get(id=id, is_deleted=False)
	except Category.DoesNotExist:
		return Response({"error": "Category does not exist."}, status=status.HTTP_404_NOT_FOUND)
	

	# Check if user doesn't have permission, it doesn't return error
	permission = IsCategoryOwner()
	if not permission.has_object_permission(request, category):
		return Response({
			"authorizatoin_error": "Only the owner of the category can manage it."
		}, status=status.HTTP_401_UNAUTHORIZED)
	
		
	# Check if there are any associated products with a category
	if Product_Category.objects.filter(category=category).exists():
		return Response({
			"forbidden": "There are products associated with this category, there for you can not edit it."
		}, status=status.HTTP_403_FORBIDDEN)
	
	# Logic for PUT method
	if request.method == "PUT":
		serializer = DetailCategorySerializer(instance=category, data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response({
				"status": "You have successfully updated the category.",
				"updated": serializer.data
			}, status=status.HTTP_200_OK)
		
	# Logic for DELETE method
	if request.method == "DELETE":
		category.is_deleted = True
		category.save()
		return Response(status=status.HTTP_204_NO_CONTENT)


# View for viewing wishlist item of authenticated user
@api_view(["GET"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def list_wishlist_items(request):
	# get user object
	user = request.user

	# Query wishlist based on user
	wishlist = Wishlist.objects.filter(user=user)
	
	# If queryset empty return error
	if not wishlist.exists():
		return Response({
			"no_products": "You have no products in you wishlist."
		}, status=status.HTTP_204_NO_CONTENT)
	
	# If not empty reutrn data
	serializer = WishListSerializer(wishlist, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)

# View for deleting wish list item of authenticated user
@api_view(["DELETE"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def delete_wishlist_item(request, id):
	# Get authenticated user
	user = request.user
	
	# Try to get the wishlist item, if can't return error
	try:
		item = Wishlist.objects.get(id=id, user=user)
	except Wishlist.DoesNotExist:
		return Response({
			"error": "This product is not in your wishlst"
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Delete wish list item 
	item.delete()
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def list_purchases(request):
	# Get the user
	user = request.user

	# Instantiate paginator
	paginator = BasicPagination()

	# Query purchase based on user
	purchases = Purchase.objects.filter(user=user).order_by("-purchase_date")

	# Check if empty and return status
	if not purchases.exists():
		return Response({
			"no_items": "You have no purchased products."
		}, status=status.HTTP_204_NO_CONTENT)

	# Paginate data
	paginated = paginator.paginate_queryset(purchases, request)
	# Serialized the paginated data
	serializer = ProfilePurchasesSerialzier(paginated, many=True)

	# Return paginated data
	return paginator.get_paginated_response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def list_reviews(request):
	# Get the user
	user = request.user

	# Query reviews based on user
	reviews = Review.objects.filter(user=user)

	# Check if queryset is empty
	if not reviews.exists():
		return Response({
			"no_reviews": "You have not reviewd any products yet."
		}, status=status.HTTP_204_NO_CONTENT)
	
	# Paginate the query
	paginator = BasicPagination()
	paginated = paginator.paginate_queryset(reviews, request)

	# Serialize the paginated queryset
	serializer = ReviewSerializer(paginated, many=True, context={"include_user": False})
	# return the data
	return paginator.get_paginated_response(serializer.data)

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def manage_reviews(request, id):
	# Try to get the review, if not exist return error
	try:
		review = Review.objects.get(id=id)
	except Review.DoesNotExist:
		return Response({
			"error": "Review does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if the user is the owner of the review
	permission = IsReviewOwner()
	if not permission.has_object_permission(request, review):
		return Response({
			"authorization_error": "Only the owner of the review can manage it."
		}, status=status.HTTP_401_UNAUTHORIZED)

	# Logic for updating a review
	if request.method == "PATCH":
		# Serialize the incoming data, the review
		serializer = ReviewSerializer(instance=review, data=request.data, context={"include_user": True})
		# Check if data is valid and send error if not.
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response({
				"status": "You have succesfully updated your review.",
				"updated_review": serializer.data
			}, status=status.HTTP_200_OK)
		
	# Logic of deleting a reiview
	if request.method == "DELETE":
		review.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
	
@api_view(["GET"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def list_ratings(request):
	# Get the user
	user = request.user

	# Query ratings based on user
	ratings = Rating.objects.filter(user=user)

	# Check if queryset is empty
	if not ratings.exists():
		return Response({
			"no_ratings": "You have not rated any products yet."
		}, status=status.HTTP_204_NO_CONTENT)
	
	# Paginate the query
	paginator = BasicPagination()
	paginated = paginator.paginate_queryset(ratings, request)

	# Serialize the paginated queryset
	serializer = RatingSerializer(paginated, many=True, context={"include_user": False})
	# return the data
	return paginator.get_paginated_response(serializer.data)

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def manage_ratings(request, id):
	# Try to get the ratings, if not exist return error
	try:
		rating = Rating.objects.get(id=id)
	except Rating.DoesNotExist:
		return Response({
			"error": "Rating does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if the user is the owner of the rating
	permission = IsRatingOwner()
	if not permission.has_object_permission(request, rating):
		return Response({
			"authorization_error": "Only the owner of the rating can manage it."
		}, status=status.HTTP_401_UNAUTHORIZED)

	# Logic for updating a rating
	if request.method == "PATCH":
		# Serialize the incoming data, the rating
		serializer = RatingSerializer(instance=rating, data=request.data, context={"include_user": False})
		# Check if data is valid and send error if not.
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response({
				"status": "You have succesfully updated your rating.",
				"updated_rating": serializer.data
			}, status=status.HTTP_200_OK)
		
	# Logic of deleting a reiview
	if request.method == "DELETE":
		rating.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def list_create_products(request):
	# get the user
	user = request.user
	if request.method == "GET":
	
		# Query the model based on the user
		products = Product.objects.filter(owner=user, is_deleted=False)

		# Check if the Query is empty, if it is return an error
		if not products.exists():
			return Response({
				"no_products": "You have not created any products yet."
			}, status=status.HTTP_204_NO_CONTENT)
		
		# Paginate the queryset
		paginator = BasicPagination()
		paginated = paginator.paginate_queryset(products, request)

		# If it is not empty serialize and return it
		serializer = GeneralProductsSerializer(paginated, many=True)
		return paginator.get_paginated_response(serializer.data)
	
	if request.method == "POST":
		# print(request.data)
		serializer = CreateProductSerialzier(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save(owner=user) # Save the product if valid
			id = serializer.data["id"] # Get the prodcut id of saved product
			new_product = Product.objects.get(id=id) # Get the saved prodcut form the model
			new_serializer = ViewDetailProdcutSerializer(new_product, context={"only_product": True}) # Serialize the new product
			return Response({
				"status": "Successfully Created a New Product",
				"product": new_serializer.data # Return the new product details
			}, status=status.HTTP_201_CREATED)

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view	
def manage_products(request, id):
	# Get the user
	user = request.user

	# Try to get the product, if not exist return error
	try:
		product = Product.objects.get(id=id, is_deleted=False)
	except Product.DoesNotExist:
		return Response({
				"no_product": "Product does not exist.",
			}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if user has permission to manage product
	permission = IsProductOwner()
	if not permission.has_object_permission(request, product):
		return Response({
				"authorization_error": "Only the owner of the product can manage it.",
			}, status=status.HTTP_401_UNAUTHORIZED)
	
	# Logic for Updating product
	if request.method == "PATCH":
		
		# Check if request data is empty
		if not request.data:
			return Response({
				"field": "No update fields were specified."
			}, status=status.HTTP_400_BAD_REQUEST)

		# Serialize incoming data while bining it to the product and enabling partial update
		serializer = CreateProductSerialzier(instance=product, data=request.data, partial=True)
		# Check incoming data validity, if not return error
		if serializer.is_valid(raise_exception=True):
			serializer.save(owner=user) # Save the product if valid
			id = serializer.data["id"] # Get the prodcut id of saved product
			new_product = Product.objects.get(id=id) # Get the saved prodcut form the model
			new_serializer = ViewDetailProdcutSerializer(new_product, context={"only_product": True}) # Serialize the new product
			return Response({
				"status": "Successfully Updated the Product",
				"product": new_serializer.data # Return the new product details
			}, status=status.HTTP_200_OK)
		
	# Logic for deleting a product
	if request.method == "DELETE":
		# Mark the product as deleted
		product.is_deleted = True
		product.save()
		return Response(status=status.HTTP_204_NO_CONTENT)
