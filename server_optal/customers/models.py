from django.conf import settings
from django.db import models
from main.models import User
from factories.models import Product, ColorVariation


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer_profile')
    city = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.first_name} ({self.user.username})"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items",
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color_variation = models.ForeignKey(
        ColorVariation, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size} x {self.quantity} ({self.color_variation})"
