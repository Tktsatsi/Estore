from django.db import models
from django.conf import settings
from store.models import Product


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"

    def line_total(self):
        """Calculate the total price for this cart item (price × quantity)"""
        return self.product.price * self.quantity
