from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "is_verified_purchase", "created_at"]
    list_filter = ["is_verified_purchase", "created_at"]
    search_fields = ["user__username", "product__name", "title", "comment"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Review Information",
            {"fields": ("user", "product", "rating", "title", "comment")},
        ),
        ("Verification", {"fields": ("is_verified_purchase",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
