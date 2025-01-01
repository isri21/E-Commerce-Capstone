from django.urls import path
from . import views

urlpatterns = [
	path("product/", views.list_product_view),
	path("product/<int:id>", views.detail_product_view)
]
