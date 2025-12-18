from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product
from .models import CartItem


@login_required
def add_to_cart(request, product_id):
    """
    Add a product to user's shopping cart.

    If the product is already in cart, increases quantity by 1.
    Only active products can be added to cart.

    Args:
        request: HttpRequest object containing user and session data.
        product_id (int): ID of the product to add to cart.

    Returns:
        HttpResponse: Redirects back to previous page or store list.
    """
    product = get_object_or_404(Product, id=product_id, active=True)
    item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f"added {product.name} to cart.")
    return redirect(request.META.get("HTTP_REFERER", "store_list"))


@login_required
def cart_detail(request):
    """
    Display user's shopping cart contents.

    Shows all items in cart with their quantities and total price.
    Uses select_related to optimize product data retrieval.

    Args:
        request: HttpRequest object containing user and session data.

    Returns:
        HttpResponse: Renders cart detail page with items and total.
    """
    items = request.user.cart_items.select_related("product").all()
    total = sum(i.line_total() for i in items)
    return render(
        request, "cart/cart_detail.html", {"items": items, "total": total}
    )


@login_required
def remove_from_cart(request, product_id):
    """
    Remove a product from user's shopping cart.

    Completely removes the cart item regardless of quantity.

    Args:
        request: HttpRequest object containing user and session data.
        product_id (int): ID of the product to remove from cart.

    Returns:
        HttpResponse: Redirects to cart details page.
    """
    item = get_object_or_404(
        CartItem, user=request.user, product_id=product_id
    )
    item.delete()
    return redirect("cart_details")
