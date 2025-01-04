from rest_framework.permissions import BasePermission

# Checks if the profile belongs to the authenticated user
class IsUser(BasePermission):
	def has_object_permission(self, request, user):
		return request.user.id == user.id
	
# Checks if the profile belongs to the authenticated user
class IsCategoryOwner(BasePermission):
	def has_object_permission(self, request, category):
		return request.user == category.creator
	
# Checks if the review belongs to the authenticated user
class IsReviewOwner(BasePermission):
	def has_object_permission(self, request, review):
		return request.user == review.user
	
# Checks if the rating belongs to the authenticated user
class IsRatingOwner(BasePermission):
	def has_object_permission(self, request, rating):
		return request.user == rating.user
	
# Checks if the product belongs to the authenticated user
class IsProductOwner(BasePermission):
	def has_object_permission(self, request, product):
		return request.user == product.owner