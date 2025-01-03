from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import *
from .permissions import IsUser, IsCategoryOwner
from rest_framework.permissions import IsAuthenticated
from store.serializers import GeneralProductsSerializer, DetailCategorySerializer
from store.functions import BasicPagination
from store.models import Product, Category, Product_Category, Purchase
from account.models import Wishlist, Review, Rating

User = get_user_model()


# View for viewing and updating user profile
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def profile_info(request, username):
	# Try to get the user object, if can't return error
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return Response({
			"error": f"User with the username [{username}] does not exist."
		}, status=status.HTTP_404_NOT_FOUND)

	permission = IsUser() # Instantiate custom permission

	# Check if user is not the owner of the profile, if it is not return an error
	if not permission.has_object_permission(request, user):
		return Response({
			"error": "You can only access your own profile details."
		}, status=status.HTTP_401_UNAUTHORIZED)

	# Logic for GET method
	if request.method == "GET":
		serialized = ProfileSerializer(user) # Instantiate serializer with user data
		return Response(serialized.data, status=status.HTTP_200_OK) # Return serialized data
	
	# Logic for PATCH method
	if request.method == "PATCH":
		# Instantiate serializer, while binding it to the user object and allowing partial fields
		serialized = ProfileSerializer(instance=user, data=request.data, partial=True)
		if serialized.is_valid(raise_exception=True): # Check if the data sent is valid
			# If data is valid, save it and return the serialized data, along with a success message
			serialized.save()
			return Response({
				"status": f"Update succesfull.",
				"updated": serialized.data
			}, status=status.HTTP_200_OK)
		

# View for viewing and creating categoies
@api_view(["GET", "POST"])
def list_create_categories(request, username):
	# Try to get the user if they exist, else return an error
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

	# Logic for GET method
	if request.method == "GET":
		# instantiate the custom paginator
		paginator = BasicPagination()
		paginator.page_size = 5
		paginator.page_query_param = "per_page"

		# fetch the products the user created using prefetch_related for optimization, and only show product that are not marked deleted
		categories = Category.objects.filter(creator=user, is_deleted=False)

		# Check if the product queryset is not empty
		if not categories.exists():
			# If it is empty, return a 404 NOT FOUND
			return Response({"no_content": "User has not created any products yet."}, status=status.HTTP_204_NO_CONTENT)

		# Serialize the paginated queryset
		paginted = paginator.paginate_queryset(categories, request)
		serializer = DetailCategorySerializer(categories, many=True)

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
				"authentication_error": "You need to be authenticated in order to create a category.",
			}, status=status.HTTP_401_UNAUTHORIZED)

		# Deserialize incoming data
		serializer = DetailCategorySerializer(data=request.data)
		# Check if incoming data is valid, if it save and return it, else return error (raise_exception=True)
		if serializer.is_valid(raise_exception=True):
			serializer.save(user=user)
			return Response({
				"status": "You have successfully created the category.",
				"detail": serializer.data
			}, status=status.HTTP_200_OK)


# View for viewing and creating categoies
@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated]) # Only authenticated users can access view
def manage_categories(request, username, id):
	# Check if user doesn't have permission, it doesn't return error
	permission = IsCategoryOwner()
	if not permission.has_object_permission(request, category):
		return Response({
			"authorizatoin_error": "Only the owner of the category can manage it."
		}, status=status.HTTP_401_UNAUTHORIZED)
	
	# Try to get the user if they exist, else return an error
	try:
		User.objects.get(username=username)
	except User.DoesNotExist:
		return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
	
		
	# Try to get the cateogry if it exist, else return an error
	try:
		category = Category.objects.filter(id=id, is_deleted=False)
	except Category.DoesNotExist:
		return Response({"error": "Category does not exist."}, status=status.HTTP_404_NOT_FOUND)
	
		
	# Check if there are any associated products with a category
	if Product_Category.objects.filter(category=category).exists():
		return Response({
			"frobidden": "There are products associated with this category, there for you can not edit it."
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
def list_wishlist_items(request, username):
	# get user object
	user = request.user

	# Check if username in the path parameter is different
	if not username == user.username:
		return Response({
			"authorization_error": "You can not view another users wishlist.",
			"username": "Please specify your own username in the path parameter."
		}, status=status.HTTP_401_UNAUTHORIZED)
			
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
def delete_wishlist_item(request, username, id):
	# Get authenticated user
	user = request.user
	# Check if different user specified in pathparameter, if so return error
	if not user.username == username:
		return Response({
			"authorizatoin_error": "You can only manage products in your own wishlist",
			"username": "Please specify your own username in the path parameter."
		}, status=status.HTTP_401_UNAUTHORIZED)
	
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