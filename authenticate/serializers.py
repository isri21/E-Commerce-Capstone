from rest_framework import serializers
from .models import User
from .functions import create_token, get_token

# Serializer for user registration
class UserRegistrationSerializer(serializers.ModelSerializer):
	# Add an additoinal confirm_password field to make sure the user entered the password they want correctly
	confirm_password = serializers.CharField()
	class Meta:
		model = User
		fields = ["username", "first_name", "last_name", "email", "password", "confirm_password"]

	def validate(self, data):
		# Check if the two passwords provided match
		if data.get("password") != data.get("confirm_password"):
			# If they don't match raise a validaiton error
			raise serializers.ValidationError({"password": "The passwords provided do not match."})
		
		return data
	
	# Custom method to create a new user using the input data
	def create(self, validated_data):
		# Remove the confirm_password field from the validated_data dictionary
		validated_data.pop("confirm_password")
		# Create the new user using the validated_data without the confirm password field
		user = User.objects.create_user(**validated_data)
		# Save the new user
		user.save()
		# Create a token for the newly created user.
		create_token(user)
		return user
	

# Serializer for user login
class UserLoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField()
		

		