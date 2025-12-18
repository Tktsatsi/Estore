from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import OrderItem, Order


def send_invoice_email(order):
    """
    Send an order confirmation email to the customer.

    Args:
        order: Order instance containing the order details.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    subject = f"Order Confirmation #{order.id} - eStore"

    # Render HTML email
    html_content = render_to_string(
        "orders/email_invoice.html",
        {
            "order": order,
        },
    )

    # Render plain text email
    text_content = render_to_string(
        "orders/email_invoice.txt",
        {
            "order": order,
        },
    )

    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.user.email],
    )

    # Attach HTML version
    email.attach_alternative(html_content, "text/html")

    # Send email
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@login_required
def checkout(request):
    """
    Process user checkout from cart to create an order.

    Creates an order from cart items, sends confirmation email,
    and clears the cart. Requires user authentication.

    Args:
        request: HttpRequest object containing user and session data.

    Returns:
        HttpResponse: Renders checkout success page or redirects to cart
        if empty.
    """
    items = request.user.cart_items.select_related("product").all()
    if not items:
        return redirect("cart_detail")

    total = sum(item.product.price * item.quantity for item in items)

    # Create order
    order = Order.objects.create(user=request.user, total=total)

    # Create order items
    for i in items:
        OrderItem.objects.create(
            order=order,
            product=i.product,
            price=i.product.price,
            quantity=i.quantity,
        )

    # Clear cart
    items.delete()

    # Send invoice email
    email_sent = send_invoice_email(order)

    if email_sent:
        message_text = (
            f"Order #{order.id} placed successfully! "
            "Check your email for the invoice."
        )
        messages.success(request, message_text)
    else:
        messages.success(request, f"Order #{order.id} placed successfully!")
        messages.warning(
            request,
            "There was an issue sending the invoice email, "
            "but your order was recorded.",
        )

    return render(request, "orders/checkout_success.html", {"order": order})


@login_required
def my_orders(request):
    """
    Display list of user's orders.

    Shows all orders for the authenticated user, ordered by most recent first.

    Args:
        request: HttpRequest object containing user and session data.

    Returns:
        HttpResponse: Renders orders list page with user's order history.
    """
    orders = request.user.orders.all().order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})
