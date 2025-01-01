from rest_framework import serializers
from django.contrib.auth import get_user_model


# Get the user model
User = get_user_model()

# Serializer for the user profile
class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["username", "first_name", "last_name", "email"]
		read_only_fields = ["username"] # Set username to read only