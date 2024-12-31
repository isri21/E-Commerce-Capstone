from .serializers import (
	UserRegistrationSerializer, # <= Used to deserialize registration data
	UserLoginSerializer # <= Used to deserialize login data
) 
from rest_framework.decorators import api_view # <= Used to handle api views
from rest_framework.response import Response # <= Used to convert the data to return into JSON
from rest_framework import status # <= Used for developer friendly status codes
from .functions import get_token, authenticate_user
# Create your views here.


# View for registering new users
@api_view(["POST"])
def register(request):
	# Deserialize the incoming registration data
	serializer = UserRegistrationSerializer(data=request.data)

	# Check if the data is valid, if not return serializer.errors with 400_BAD_REQUEST (handeld by the "raise_exception=True")
	if serializer.is_valid(raise_exception=True):
		# If data is valid, save it
		serializer.save()
		# Get the username form the submitted data
		username = serializer.validated_data["username"]

		# Get the authentication token for that user
		token = get_token(username)
		# Response data to be sent upon successfull registration
		response = {
			"status": "You have successfully registered!", 
			"token": token
		}
		return Response(response, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def login(request):
	# Deserialize the incoming login data
	serializer = UserLoginSerializer(data=request.data)

	# Check if the login data is valid
	if serializer.is_valid():
		# If it is valid, check if the user is authenticated
		credentials = authenticate_user(serializer.validated_data)
		if credentials != None:
			# If the user is authenticated return their token
			return Response({"token": credentials}, status=status.HTTP_200_OK)
		else:
			# If the user is not authenticated return the an error message along with status code of 400_BAD_REQUEST
			return Response({"error": "Incorrect username or password!"}, status=status.HTTP_400_BAD_REQUEST)

