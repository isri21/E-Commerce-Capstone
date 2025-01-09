from django.urls import path
from . import views

urlpatterns = [
	path("products/", views.list_product_view),
	path("products/<int:id>/", views.detail_product_view),
	path("products/<int:id>/wishlist/", views.wishlist_product),
	path("products/<int:id>/review/", views.review_product),
	path("products/<int:id>/reviews/", views.list_product_reviews),
	path("products/<int:id>/rate/", views.rate_product),
	path("categories/", views.list_all_categories),
]
