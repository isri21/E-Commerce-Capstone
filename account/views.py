from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import *
from .permissions import IsUser
from rest_framework.permissions import IsAuthenticated
from store.serializers import GeneralProductsSerializer
from store.functions import CustomPagination
from store.models import Product

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
		
# View for viewing and updating user profile
@api_view(["GET", "POST"])
def list_posted_products(request, username):
	
	# Try to get the user if they exist, else return an error
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

	# instantiate the custom paginator
	paginator = CustomPagination()

	# fetch the products the user created using prefetch_related for optimization, and only show product that are not marked deleted
	products = Product.objects.prefetch_related("category").filter(owner=user, is_deleted=False)

	# Check if there is an invalid query parameter
	for key in request.GET:
		if key not in ["page", "per_page"]:
			return Response({f"{key}": "Invalid query parameter"}, status=status.HTTP_400_BAD_REQUEST)

	# Check if the product queryset is not empty
	if not products.exists():
		# If it is empty, return a 404 NOT FOUND
		return Response({"no_content": "User has not posted any products yet."}, status=status.HTTP_204_NO_CONTENT)

	# Paginate the queryset
	paginated = paginator.paginate_queryset(products, request)

	# Serialize the paginated queryset
	serializer = GeneralProductsSerializer(paginated, many=True)

	# Reutrn the serialized quieryset along with addtional information (meta-data)
	return paginator.get_paginated_response(serializer.data)
