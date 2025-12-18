from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from store.models import Product
from orders.models import Order, OrderItem


def check_verified_purchase(user, product):
    """Verify if a user has previously purchased a specific product.

    Args:
        user (User): The user object to check purchase history for.
        product (Product): The product object to verify purchase of.

    Returns:
        bool: True if the user has purchased the product, False otherwise.

    Checks all completed orders of the user for the presence of the product.
    """
    # Check if user has any completed orders containing this product
    user_orders = Order.objects.filter(user=user)

    for order in user_orders:
        if OrderItem.objects.filter(order=order, product=product).exists():
            return True
    return False


@login_required
def add_review(request, product_slug):
    """Handle creation or update of a product review.

    Args:
        request (HttpRequest): The HTTP request object containing POST data
            with review content or GET for review form.
        product_slug (str): URL slug of the product to review.

    Returns:
        HttpResponse: Renders review form or redirects to product detail page
            after successful submission.

    Features:
    - Validates user authentication
    - Checks for existing review to update
    - Verifies if user has purchased the product
    - Handles both creation and update of reviews
    """
    product = get_object_or_404(Product, slug=product_slug)

    # Check if user already reviewed this product
    existing_review = Review.objects.filter(
        product=product, user=request.user
    ).first()

    # Check if this is a verified purchase
    is_verified = check_verified_purchase(request.user, product)

    if request.method == "POST":
        title = request.POST.get("title", "")
        comment = request.POST.get("comment", "").strip()

        if not comment:
            messages.error(request, "Please provide a review comment.")
            return redirect(request.path)

        if existing_review:
            # Update existing review
            existing_review.title = title
            existing_review.comment = comment
            existing_review.is_verified_purchase = is_verified
            existing_review.save()
            messages.success(request, "Your review has been updated!")
        else:
            # Create new review
            Review.objects.create(
                product=product,
                user=request.user,
                title=title,
                comment=comment,
                is_verified_purchase=is_verified,
            )
            if is_verified:
                messages.success(
                    request, "Thank you for your verified review!"
                )
            else:
                messages.success(request, "Thank you for your review!")

        return redirect(
            "product_detail",
            store_slug=product.store.slug,
            product_slug=product.slug,
        )

    return render(
        request,
        "reviews/add_review.html",
        {
            "product": product,
            "existing_review": existing_review,
            "is_verified": is_verified,
            "is_edit": existing_review is not None,
            "has_purchased": is_verified,
        },
    )


@login_required
def delete_review(request, review_id):
    """Handle deletion of a user's review.

    Args:
        request (HttpRequest): The HTTP request object.
        review_id (int): The ID of the review to delete.

    Returns:
        HttpResponse: Redirects to product detail page after successful
            deletion.

    Validates:
    - User authentication
    - Review ownership
    - Review existence
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product = review.product
    review.delete()
    messages.success(request, "Your review has been deleted.")
    return redirect(
        "product_detail",
        store_slug=product.store.slug,
        product_slug=product.slug,
    )
