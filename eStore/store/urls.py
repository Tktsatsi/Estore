from django.urls import path
from . import views

urlpatterns = [
    # Vendor End points
    path(
        "api/vendor/stores/create/", views.add_store, name="api_create_store"
    ),
    path(
        "api/vendor/stores/<int:store_id>/products/add/",
        views.api_add_product,
        name="api_add_product",
    ),
    path(
        "api/vendor/reviews/",
        views.api_vendor_reviews,
        name="api_vendor_reviews",
    ),
    # Public End points
    path("api/stores/", views.view_store, name="view_store"),
    path(
        "api/vendors/<str:vendor_username>/stores/",
        views.api_vendor_stores,
        name="api_vendor_stores",
    ),
    path(
        "api/stores/<int:store_id>/products/",
        views.api_store_products,
        name="api_store_products",
    ),
    path("add_store/stores", views.add_store, name="add_store"),
    path("", views.store_list, name="store_list"),
    path("<slug:slug>/", views.store_detail, name="store_detail"),
    path(
        "<slug:store_slug>/<slug:product_slug>/",
        views.product_detail,
        name="product_detail",
    ),
]
