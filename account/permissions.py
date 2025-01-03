from rest_framework.permissions import BasePermission

# Checks if the profile belongs to the authenticated user
class IsUser(BasePermission):
	def has_object_permission(self, request, user):
		return request.user.id == user.id
	
# Checks if the profile belongs to the authenticated user
class IsCategoryOwner(BasePermission):
	def has_object_permission(self, request, category):
		return request.user == category.creator
	
# Checks if the profile belongs to the authenticated user
class IsReviewOwner(BasePermission):
	def has_object_permission(self, request, review):
		return request.user == review.user