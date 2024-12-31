from rest_framework.authtoken.models import Token
from .models import User
from django.contrib.auth import authenticate

def get_token(username):
	"""
	Gets the authentication token of a user

	Parameters:
	username (str): The username of the user to get the token for

	Returns:
	str: The authentication token of the user.
	"""

	# Get the user instance
	user = User.objects.get(username=username)
	# Get the token for that user
	token = Token.objects.get(user=user)
	# Return the token string
	return token.key

def create_token(user):
	"""
	Creates an authentication token for a user

	Parameters:
	user (User): The user instance to create the token for

	Returns:
	str: The newly created authentication token of the user.
	"""
	# Create a token for the user
	token = Token.objects.create(user=user)

	# Return the token stirng
	return token.key


def authenticate_user(validated_data):
	"""
	Checks if a user is authenticated based on validated serialized data

	Parameters:
	validate_data (dict): validated_data dictionary from serializer.is_valid()

	Returns:
	str or None: The return value depends on wheter the user is authenticated or not
	- If the user is authenticated:
		- Returns the authorization token key of the user
	- If the user is not authenticated:
		- Returns None
	"""
	# Get the username and password from the validated_data dictionary passed
	username = validated_data.get("username")
	password = validated_data.get("password")
	# Check if the user is authenticated
	if authenticate(username=username, password=password):
		# If authenticated return the token string of the user
		return get_token(username)
	else:
		# If not authenticated return None
		return None