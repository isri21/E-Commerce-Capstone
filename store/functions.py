from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import BasePermission

# Pagniator with custom meta data
class CustomPagination(PageNumberPagination):
	page_size = 3
	page_size_query_param = "per_page"

	def get_paginated_response(self, data):
		return Response({
			'total_products': self.page.paginator.count,
			'total_pages': self.page.paginator.num_pages,
			'current_page': self.page.number,
			'products_per_page': self.page.paginator.per_page,
			'next_page': self.get_next_link(),
			'previous_page': self.get_previous_link(),
			'results': data
		})
# Config for basic paginator
class BasicPagination(PageNumberPagination):
	page_size = 3
	page_size_query_param = "per_page"


