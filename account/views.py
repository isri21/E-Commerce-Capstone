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
