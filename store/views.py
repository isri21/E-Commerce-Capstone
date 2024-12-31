from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Product
from .serializers import AllProductsSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .functions import CustomPagination

@api_view(["GET"])
def list(request):
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
			return Response({"error": f"Invalid query parameter [{key}]."}, status=status.HTTP_400_BAD_REQUEST)


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
			return Response({"error": "The in_stock filter must be a 'yes' or 'no' value."}, status=status.HTTP_400_BAD_REQUEST)
	
	# Check if both "min_price" and "max_price" parameters are given
	if min_price != None and max_price != None:
		# Try to convert them to float values for a comparision expression
		try:
			min_price = float(min_price)
			max_price = float(max_price)
		except ValueError:
			# It the values of "min_price" and "max_price" can't be converted to float return an error
			return Response({"error": "Both the min_price and max_price filters must be numbers."}, status=status.HTTP_400_BAD_REQUEST)
		
		# Check if "min_price" is greater than "max_price"
		if min_price > max_price:
			# If it is return an error
			return Response({"error": "The minimum price, can not be greater than the maximum price."}, status=status.HTTP_400_BAD_REQUEST)

	# Check if only min_price is given
	if min_price:
		# Try to convert it into float
		try:
			min_price = float(min_price)
		except ValueError:
			# If can't be converted return an error
			return Response({"error": "The min_price filter must be a float or an integer value."}, status=status.HTTP_400_BAD_REQUEST)
		# If it is a vaid value filter the queryset by the "min_price" parameter
		products = products.filter(price__gte=min_price)

	# Check if only the max_price is given
	if max_price:
		# Try to convert it into float
		try:
			min_price = float(min_price)
		except ValueError:
			# If can't be converted return an error
			return Response({"error": "The max_price query must be a float or an integer value."}, status=status.HTTP_400_BAD_REQUEST)
		# If it is a vaid value filter the queryset by the "max_price" parameter
		products = products.filter(price__lte=max_price)

	# Check if the product queryset is not empty
	if not products.exists():
		# If it is empty, return a 404 NOT FOUND
		return Response({"error": "There are no items that match your filters."}, status=status.HTTP_404_NOT_FOUND)

	# Paginate the queryset
	paginated = paginator.paginate_queryset(products, request)

	# Serialize the paginated queryset
	serializer = AllProductsSerializer(paginated, many=True)

	# Reutrn the serialized quieryset along with addtional information (meta-data)
	return paginator.get_paginated_response(serializer.data)

