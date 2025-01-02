from django.urls import path
from . import views

urlpatterns = [
	path("", views.profile_info),
	path("categories/", views.list_create_categories),
	path("category/<int:id>/", views.manage_categories),
]