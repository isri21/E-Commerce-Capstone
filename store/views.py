from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .functions import CustomPagination, BasicPagination
from rest_framework.permissions import IsAuthenticated
from account.models import *
from django.db import IntegrityError

# Handle getting all the products in the store that are not deleted
@api_view(["GET"])
def list_product_view(request):
	# Prepare paginator
	paginator = CustomPagination()

	# Get all the products that are not deleted
	products = Product.objects.prefetch_related("category").filter(is_deleted=False)

	# Prepare the query parameters
	search = request.GET.get("search", None)
	category = request.GET.get("category", None)
	in_stock = request.GET.get("in_stock", None)
	min_price = request.GET.get("min_price", None)
	max_price = request.GET.get("max_price", None)

	# Check if the user entered an invalid query parameter, and respond accordingly
	for key in request.GET:
		if key not in ["search", "category", "in_stock", "min_price", "max_price", "page", "per_page"]:
			return Response({f"{key}": "Invalid query parameter"}, status=status.HTTP_400_BAD_REQUEST)

	# Check if the query parameters are entered by the user and filter the queryset accordngly
	if search:
		products = products.filter(Q(name__icontains=search) | Q(category__name__icontains=search)).distinct()

	if category:
		products = products.filter(category__name__icontains=category)
	
	if in_stock:
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
			# If the values of "min_price" and "max_price" can't be converted to float return an error
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
			max_price = float(max_price)
		except ValueError:
			# If can't be converted return an error
			return Response({"max_price": "The max_price query must be a float or an integer value."}, status=status.HTTP_400_BAD_REQUEST)
		# If it is a vaid value filter the queryset by the "max_price" parameter
		products = products.filter(price__lte=max_price)

	# Check if the filtered product queryset is not empty, if it is empty respond accordingly
	if not products.exists():
		return Response({"not_found": "There are no items that match your filters."}, status=status.HTTP_404_NOT_FOUND)

	# Paginate the queryset
	paginated = paginator.paginate_queryset(products, request)

	# Serialize the paginated queryset
	serializer = GeneralProductsSerializer(paginated, many=True)

	# Reutrn the serialized quieryset along with addtional information (meta-data)
	return paginator.get_paginated_response(serializer.data)

# Handle getting a specific product and purchasing a product
@api_view(["GET", "POST"])
def detail_product_view(request, id):
	# Try to get the specific product, else return an error if it doesn't exist
	try:
		product = Product.objects.get(id=id)
	except:
		return Response({"not_found": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if product is marked deleted, if it is, return a not found
	if product.is_deleted == True:
		return Response({"not_found": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)

	# Logic for getting a product details
	if request.method == "GET":
		# If product exists, serialize it and return serialized data along with a 200 OK
		serializer = ViewDetailProdcutSerializer(product)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
	# Logic for purchasing a product
	if request.method == "POST":
		# Prepare the IsAuthenticated permission
		permission = IsAuthenticated()

		# Check if the user doesn't have the permission, if they don't respond accordingly
		if not permission.has_permission(request, None):
			return Response({
				"authentication_error": "You must be authenticated in order to purchase a product, please send you authentication token in the request header."
			}, status=status.HTTP_401_UNAUTHORIZED)
		
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
	
# Handle adding a product to wishlist
@api_view(["POST"])
def wishlist_product(request, id):
	# Instantiate an IsAuthenticated permisison
	permission = IsAuthenticated()

	# Check if the user doesn't have the permisison, if they don't respond accordingly
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
			"not_found": "Product does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if product is marked deleted, if it is, return a not found
	if product.is_deleted == True:
		return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
	
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
	
# Handle reviewing a product
@api_view(["POST"])
def review_product(request, id):
	# Instantiate an IsAuthenticated permisison
	permission = IsAuthenticated()

	# Check if the user doesn't have the permisison, if they don't respond accordingly
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
			"error": "Product does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if product is marked deleted, if it is, return a not found
	if product.is_deleted == True:
		return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)

	# Check if the user has purchased the product to review, if they havent respond accordingly
	purchased = Purchase.objects.filter(product=product, user=user)
	if not purchased.exists():
		return Response({
			"error": "In order to review a product, you must first purchase it."
		}, status=status.HTTP_403_FORBIDDEN)
	
	# Deserialized the incoming data (the review)
	serializer = ReviewSerializer(data=request.data)

	# Check if the incoming data is valid, and respond accordingly
	if serializer.is_valid(raise_exception=True):
		# Pass the user object and the prodcut reviewed when saving,  to create the review instance
		serializer.save(user=user, product=product)
		return Response({
			"status": "You have successfully reviewed the product."
		}, status=status.HTTP_201_CREATED)

# Handle getting the reviews for a product
@api_view(["GET"])
def list_product_reviews(request, id):

	# Try to get the specific product, else return an error if it doesn't exist
	try:
		product = Product.objects.get(id=id)
	except:
		return Response({
			"error": "Product does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Get reviews, and check if they are empty, if they are respond accordingly
	reviews = Review.objects.filter(product=product)
	if not reviews.exists():
		return Response({
			"no_reviews": "There are no reviews for this product",
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Prepare Paginator and paginate the queryset
	paginator = BasicPagination()
	paginated = paginator.paginate_queryset(reviews, request)

	# Serialize paginated reviews
	serializer = ReviewSerializer(paginated, many=True)

	return paginator.get_paginated_response(serializer.data)

# Handle rating a product	
@api_view(["POST"])
def rate_product(request, id):
	# Instantiate an IsAuthenticated permisison
	permission = IsAuthenticated()

	# Check if the user doesn't have the permisison, if they don't respond accordingly
	if not permission.has_permission(request, None):
		return Response({
			"error": "You must be authenticated in order to rate this product, please send you authentication token in the request header."
		}, status=status.HTTP_401_UNAUTHORIZED)
	
	# Get the user object
	user = request.user

	# Try to get the specific product, else return an error if it doesn't exist
	try:
		product = Product.objects.get(id=id)
	except:
		return Response({
			"error": "Product does not exist."
		}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if product is marked deleted, if it is, return a not found
	if product.is_deleted == True:
		return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
	
	# Check if the user has purchased the product to rate, if they havent respond accordingly
	purchased = Purchase.objects.filter(product=product, user=user)
	if not purchased.exists():
		return Response({
			"error": "In order to rate a product, you must first purchase it."
		}, status=status.HTTP_403_FORBIDDEN)
	
	# Deserialize the incoming data (the rating)
	serializer = RatingSerializer(data=request.data)
	# Check if incoming data is valid, and respond accordingly
	if serializer.is_valid(raise_exception=True):
		# Pass the user object and the prodcut reviewd to create the review instance 
		serializer.save(user=user, product=product)
		return Response({
			"status": "You have successfully rated the product."
		}, status=status.HTTP_201_CREATED)
	
# Handle getting all the categories created	
@api_view(["GET"])
def list_all_categories(request):
	# Prepare a paginator
	paginator = BasicPagination()

	# Get all the categories that are not deleted
	categories = Category.objects.filter(is_deleted=False)

	# Check if the category queryset is not empty, if it is respond accordingly
	if not categories.exists():
		return Response({
			"no_categories": "There are not categories in the store yet."
		}, status=status.HTTP_204_NO_CONTENT)

	# Paginate the queryset
	paginated = paginator.paginate_queryset(categories, request)

	# Serialize the paginated queryset
	serializer = DetailCategorySerializer(paginated, many=True)

	# Return serialized data, and status of 200
	return paginator.get_paginated_response(serializer.data)