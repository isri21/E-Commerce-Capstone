from django.urls import path
from . import views

urlpatterns = [
	path("", views.profile_info),
	path("products/", views.list_posted_products),
]