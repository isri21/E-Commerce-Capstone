from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .functions import CustomPagination
from rest_framework.permissions import IsAuthenticated
from account.models import *
from django.db import IntegrityError


# View for getting all the proucts in the store
@api_view(["GET"])
def list_product_view(request):
	# instantiate the custom paginator
	paginator = CustomPagination()

	# fetch all the products using prefetch_related for optimization
	products = Product.objects.prefetch_related("category")

	# get the query parameters
	search = request.GET.get("search", None)
	category = request.GET.get("category", None)
	in_stock = request.GET.get("in_stock", None)
	min_price = request.GET.get("min_price", None)
	max_price = request.GET.get("max_price", None)

	# Check if there is an invalid query parameter
	for key in request.GET:
		if key not in ["search", "category", "in_stock", "min_price", "max_price", "page", "per_page"]:
			return Response({f"{key}": "Invalid query parameter"}, status=status.HTTP_400_BAD_REQUEST)


	# Check if the search query parameter is specified
	if search:
		# filter the queryset based on the search parameter
		products = products.filter(Q(name__icontains=search) | Q(category__name__icontains=search))

	# Check if the category query parameter is specified
	if category:
		# filter the queryset based on the category parameter
		products = products.filter(category__name__icontains=category)
	
	# Check if the category query parameter is specified
	if in_stock:
		# Check if the value for the parameter is "yes" or "no" and filter accordingly
		if in_stock.lower() == "yes":
			products = products.filter(stock_quantity__gt=0)
		elif in_stock.lower() == "no":
			products = products.filter(stock_quantity=0)
		else:
			# if the value for the in_stock parameter is not "yes" or "no", return an error
			return Response({"in_stock": "The in_stock filter must be a 'yes' or 'no' value."}, status=status.HTTP_400_BAD_REQUEST)
	
	# Check if both "min_price" and "max_price" parameters are given
	if min_price != None and max_price != None:
		# Try to convert them to float values for a comparision expression
		try:
			min_price = float(min_price)
			max_price = float(max_price)
		except ValueError:
			# It the values of "min_price" and "max_price" can't be converted to float return an error
			return Response({"range_error": "Both the min_price and max_price filters must be numbers."}, status=status.HTTP_400_BAD_REQUEST)
		
		# Check if "min_price" is greater than "max_price"
		if min_price > max_price:
			# If it is return an error
			return Response({"range_error": "The minimum price, can not be greater than the maximum price."}, status=status.HTTP_400_BAD_REQUEST)

	# Check if only min_price is given
	if min_price:
		# Try to convert it into float
		try:
			min_price = float(min_price)
		except ValueError:
			# If can't be converted return an error
			return Response({"min_price": "The min_price filter must be a float or an integer value."}, status=status.HTTP_400_BAD_REQUEST)
		# If it is a vaid value filter the queryset by the "min_price" parameter
		products = products.filter(price__gte=min_price)

	# Check if only the max_price is given
	if max_price:
		# Try to convert it into float
		try:
			min_price = float(min_price)
		except ValueError:
			# If can't be converted return an error
			return Response({"max_price": "The max_price query must be a float or an integer value."}, status=status.HTTP_400_BAD_REQUEST)
		# If it is a vaid value filter the queryset by the "max_price" parameter
		products = products.filter(price__lte=max_price)

	# Check if the product queryset is not empty
	if not products.exists():
		# If it is empty, return a 404 NOT FOUND
		return Response({"not_found": "There are no items that match your filters."}, status=status.HTTP_404_NOT_FOUND)

	# Paginate the queryset
	paginated = paginator.paginate_queryset(products, request)

	# Serialize the paginated queryset
	serializer = GeneralProductsSerializer(paginated, many=True)

	# Reutrn the serialized quieryset along with addtional information (meta-data)
	return paginator.get_paginated_response(serializer.data)


# View for getting a products details
@api_view(["GET", "POST"])
def detail_product_view(request, id):
	# LOGIC for POST method
	if request.method == "POST":
		permission = IsAuthenticated() # Instantiate an IsAuthenticated permission
		# Check if the use doesn't have the permission, if not return an error
		if not permission.has_permission(request, None):
			return Response({
				"authentication_error": "You must be authenticated in order to purchase a product, please send you authentication token in the request header."
			}, status=status.HTTP_401_UNAUTHORIZED)
		
		# Try to get the specific product, else return an error if it doesn't exist
		try:
			product = Product.objects.get(id=id)
		except:
			return Response({"not_found": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
		
		# Serialize the incoming, data (quantity to purchase)
		serializer = PurchaseSerializer(
			data=request.data,
			context={ # Send request and product object to serializer for validation and creation
				"request": request, 
				"product": product
			})
		
		# Check if the data entered is valid, if it is save the object, and return the serialized data and a 201 Created
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)

	# LOGIC for GET method
	if request.method == "GET":
		# Try to get the specifc product, if not exist, return an error
		try:
			product = Product.objects.get(id=id)
		except:
			return Response({"not_found": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
	
	# If product exists, serialize it and return serialized data along with a 200 OK
	serializer = DetailProdcutSerializer(product)
	return Response(serializer.data, status=status.HTTP_200_OK)

# View for adding a product to a wishlist
@api_view(["POST"])
def wishlist_product(request, id):
	permission = IsAuthenticated() # Instantiate an IsAuthenticated permisison
	# Check if the user doesn't have the permisison, if not retrun an error
	if not permission.has_permission(request, None):
		return Response({
			"error": "You must be authenticated in order to purchase a product, please send you authentication token in the request header."
		}, status=status.HTTP_401_UNAUTHORIZED)
	
	# Get the user object
	user = request.user

	# Try to get the specific product, else return an error if it doesn't exist
	try:
		product = Product.objects.get(id=id)
	except:
		return Response({
			"not_found": f"A product with an id [{id}] does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Try to create the wishlist item, if integrity error is raised, return an error stating that.
	try:
		Wishlist.objects.create(user=user, product=product)
		return Response({
			"status": f"Product '{product.name}' added to wish list",
		}, status=status.HTTP_201_CREATED)
	except IntegrityError:
		return Response({
			"error": "You have already added this product to your wish list."
		}, status=status.HTTP_409_CONFLICT)
	

@api_view(["POST"])
def review_product(request, id):
	permission = IsAuthenticated() # Instantiate an IsAuthenticated permisison
	# Check if the user doesn't have the permisison, if not retrun an error
	if not permission.has_permission(request, None):
		return Response({
			"error": "You must be authenticated in order to add a product to your wish list, please send you authentication token in the request header."
		}, status=status.HTTP_401_UNAUTHORIZED)
	
	# Get the user object
	user = request.user

	# Try to get the specific product, else return an error if it doesn't exist
	try:
		product = Product.objects.get(id=id)
	except:
		return Response({
			"not_found": f"A product with an id [{id}] does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if the data sent is a text/string
	if not isinstance(request.data.get("review"), str):
		return Response({
			"error": "The review must be a string value."
		}, status=status.HTTP_400_BAD_REQUEST)
	
	# Check if the user has purchased the product to review
	purchased = Purchase.objects.filter(product=product, user=user)
	if not purchased.exists():
		return Response({
			"error": "In order to review a product, you must first purchase it."
		}, status=status.HTTP_403_FORBIDDEN)
	
	serializer = ReviewSerializer(data=request.data)
	if serializer.is_valid(raise_exception=True):
		serializer.save(user=user, product=product)
		return Response({
			"status": "You have successfully reviewed the product."
		}, status=status.HTTP_201_CREATED)

	