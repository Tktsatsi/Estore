from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    renderer_classes,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Store, Product
from reviews.models import Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer


# ========== WEB PAGE VIEWS ==========


def store_list(request):
    """Display list of all stores."""
    stores = Store.objects.all()
    return render(request, "store/store_list.html", {"stores": stores})


def store_detail(request, slug):
    """Display store details and its active products."""
    store = get_object_or_404(Store, slug=slug)
    products = store.products.filter(active=True)
    return render(
        request,
        "store/store_detail.html",
        {"store": store, "products": products},
    )


def product_detail(request, store_slug, product_slug):
    """Display detailed product information."""
    product = get_object_or_404(
        Product, store__slug=store_slug, slug=product_slug, active=True
    )
    return render(request, "store/product_detail.html", {"product": product})


# VENDOR ENDPOINTS (Authentication Required)


@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_store(request):
    """
    Create a new store.
    Protected endpoint - requires authentication.
    Owner is automatically set to the authenticated user.
    Automatically tweets about the new store.
    """
    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        # Save the store
        store = serializer.save(owner=request.user)

        # Tweet about the new store
        try:
            from .twitter_utils import tweet_new_store

            print("🐦 Attempting to tweet about new store: %s" % store.name)
            success = tweet_new_store(store)
            if success:
                print("✅ Tweet sent successfully!")
            else:
                print("❌ Tweet failed (but store was created)")
        except Exception as e:
            print(f"❌ Error tweeting: {e}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_add_product(request, store_id):
    """
    Vendor adds a product to their store.
    Protected endpoint - requires authentication and store ownership.
    Automatically tweets about the new product.
    """
    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if user owns the store
    if store.owner != request.user:
        return Response(
            {
                "error": (
                    "You don't have permission to add products to this "
                    "store"
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        # Save the product
        product = serializer.save(store=store)

        # Tweet about the new product
        try:
            from .twitter_utils import tweet_new_product

            print(
                "🐦 Attempting to tweet about new product: %s" % product.name
            )
            success = tweet_new_product(product)
            if success:
                print("✅ Tweet sent successfully!")
            else:
                print("❌ Tweet failed (but product was created)")
        except Exception as e:
            print("❌ Error tweeting: %s" % e)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_vendor_reviews(request):
    """
    Vendor retrieves all reviews for their products.
    Protected endpoint - requires authentication.
    """
    # Get all stores owned by this vendor
    vendor_stores = Store.objects.filter(owner=request.user)
    # Get all products from those stores
    vendor_products = Product.objects.filter(store__in=vendor_stores)
    # Get all reviews for those products
    reviews = Review.objects.filter(product__in=vendor_products)

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# PUBLIC ENDPOINTS (No Authentication Required)


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def view_store(request):
    """
    List all stores in the system.
    Public access endpoint - no authentication required.
    """
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def api_vendor_stores(request, vendor_username):
    """
    Retrieve all stores for a specific vendor.
    Public access endpoint - no authentication required.
    """
    try:
        vendor = User.objects.get(username=vendor_username)
        stores = Store.objects.filter(owner=vendor)
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def api_store_products(request, store_id):
    """
    Retrieve all active products for a specific store.
    Public access endpoint - no authentication required.
    """
    try:
        store = Store.objects.get(id=store_id)
        products = Product.objects.filter(store=store, active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND
        )
