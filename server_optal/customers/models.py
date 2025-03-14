from django.conf import settings
from django.db import models
from main.models import User
from factories.models import Product, ColorVariation
from django.utils.timezone import now


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer_profile')
    city = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.first_name} ({self.user.username})"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    class Meta:
        verbose_name = "Корзина клиента"
        verbose_name_plural = "Корзины клиентов"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, null=False, related_name='items')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color_variation = models.ForeignKey(
        ColorVariation, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзинах"


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('sewing', 'В пошиве'),
        ('shipping', 'В пути'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='processing')
    is_confirmed = models.BooleanField(
        default=False)
    city_delivery = models.CharField(max_length=256, default="Город не указан")
    snapshot = models.JSONField(
        verbose_name="Order Snapshot", default=dict, blank=True)
    customer_snapshot = models.JSONField(
        verbose_name="Customer Snapshot", default=dict, blank=True)
    detailed_snapshot = models.JSONField(
        verbose_name="Detailed Snapshot", default=dict, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class QuickOrder(models.Model):
    product_id = models.IntegerField(verbose_name="ID товара")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="quick_orders",
        verbose_name="Пользователь"
    )
    phone_number = models.CharField(
        max_length=15, null=True, blank=True, verbose_name="Телефон анонимного пользователя"
    )
    created_at = models.DateTimeField(default=now, verbose_name="Время заказа")

    def __str__(self):
        return f"QuickOrder {self.id} for Product {self.product_id}"

    class Meta:
        verbose_name = "Быстрый заказ"
        verbose_name_plural = "Быстрые заказы"
