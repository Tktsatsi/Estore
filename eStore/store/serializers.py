from rest_framework import serializers
from .models import Store, Product
from reviews.models import Review

# Review model is used by ReviewSerializer


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for the Store model.

    Converts Store model instances to JSON format and vice versa.
    Used for API endpoints that handle store data.
    """

    class Meta:
        model = Store
        fields = ["name", "description", "owner", "slug", "logo"]
        read_only_fields = ["slug", "owner", "slug", "description"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model.

    Converts Product model instances to JSON format and vice versa.
    Used for API endpoints that handle product data.
    """

    class Meta:
        model = Product
        fields = [
            "store",
            "category",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "active",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model.

    Converts Review model instances to JSON format and vice versa.
    Used for API endpoints that handle product reviews.

    Fields:
        product: The product being reviewed
        user: The user who wrote the review
        title: Review title (optional)
        comment: The main review text
        is_verified_purchase: Whether the reviewer has purchased the product
        created_at: When the review was created
        updated_at: When the review was last updated
    """

    class Meta:
        model = Review
        fields = [
            "product",
            "user",
            "title",
            "comment",
            "is_verified_purchase",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
