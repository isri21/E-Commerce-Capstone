from django.urls import path
from . import views

urlpatterns = [
	path("products/", views.list_product_view),
	path("product/<int:id>/", views.detail_product_view),
	path("product/<int:id>/wishlist/", views.wishlist_product),
	path("product/<int:id>/review/", views.review_product)
]
