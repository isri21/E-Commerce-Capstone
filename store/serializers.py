from rest_framework import serializers
from .models import Product, Product_Category, Image, Category



class ImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Image
		fields = ["image"]

	def to_representation(self, instance):
		data = super().to_representation(instance)
		return data["image"]

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["name"]

	def to_representation(self, instance):
		data = super().to_representation(instance)
		return data["name"]

class AllProductsSerializer(serializers.ModelSerializer):
	images = ImageSerializer(many=True)
	category = CategorySerializer(many=True)
	class Meta:
		model = Product
		fields = ["id", "name", "images", "category", "stock_quantity"]