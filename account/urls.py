from django.urls import path
from . import views

urlpatterns = [
	path("", views.profile_info),
	path("categories/", views.list_create_categories),
	path("category/<int:id>/", views.manage_categories),
	path("wishlist/", views.list_wishlist_items),
	path("wishlist/<int:id>/", views.delete_wishlist_item),
	path("purchases/", views.list_purchases),
]