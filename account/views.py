from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import *
from .permissions import IsUser
from rest_framework.permissions import IsAuthenticated

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