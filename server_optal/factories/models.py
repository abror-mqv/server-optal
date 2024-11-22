from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser, UserManager
# Create your models here.

from django.utils import timezone


class Factory(AbstractUser):
    factory_name = models.CharField(max_length=255, verbose_name="Описание")
    first_name = models.CharField(max_length=255, verbose_name="Имя цеховика")
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True, verbose_name="Аватарка")
    factory_description = models.TextField(
        verbose_name="Описание", null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='factory_groups',  # Уникальное имя
        blank=True,
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='factory_user_permissions',  # Уникальное имя
        blank=True,
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    cat_name = models.CharField(verbose_name='Категория', max_length=127)

    def __str__(self):
        return self.cat_name


class SubCategory(models.Model):
    subcat_name = models.CharField(verbose_name='Подкатегория', max_length=127)
    father = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.father.cat_name} -> {self.subcat_name}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sizes = models.CharField(
        verbose_name='Размеры', default=None, max_length=63, null=True, blank=True)
    description = models.TextField(
        verbose_name="Описание", max_length=255, default=None)
    father = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    manufacter = models.ForeignKey(Factory, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ColorVariation(models.Model):
    product = models.ForeignKey(
        Product, related_name='color_variations', on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7)
    image = models.ImageField(
        upload_to='color_variant_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.color_name} - {self.product.name}"
