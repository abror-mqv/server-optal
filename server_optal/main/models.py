from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Phone Number must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

    class Meta:
        verbose_name = "Диспетчер пользователей"
        verbose_name_plural = "Сущности пользователей"


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=15, unique=True, verbose_name="Phone Number")
    first_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Сущность пользователя"
        verbose_name_plural = "Сущности пользователей"


class ExchangeRate(models.Model):
    currency_code = models.CharField(max_length=3, unique=True)
    rate_to_kgs = models.DecimalField(
        max_digits=10, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.currency_code}: {self.rate_to_kgs}"

    class Meta:
        verbose_name = "Курс валют"
        verbose_name_plural = "Курсы валют"
