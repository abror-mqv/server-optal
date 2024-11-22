from django.contrib.auth.models import AbstractUser
from django.db import models


class Customer(AbstractUser):
    city = models.CharField(max_length=100, verbose_name="Город")
    phone_number = models.CharField(
        max_length=15, verbose_name="Номер телефона")
    registration_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации")

    # Переопределяем related_name, чтобы избежать конфликта
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_groups',  # Уникальное имя
        blank=True,
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_user_permissions',  # Уникальное имя
        blank=True,
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username
