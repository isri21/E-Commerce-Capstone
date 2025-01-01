from rest_framework.permissions import BasePermission

# Checks if the profile belongs to the authenticated user
class IsUser(BasePermission):
	def has_object_permission(self, request, user):
		return request.user.id == user.id