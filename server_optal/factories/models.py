from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser, UserManager
from django.utils import timezone
# from django.contrib.auth.models import User
from main.models import User


class FactoryProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    factory_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    factory_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Factory: {self.factory_name} ({self.user.username})"


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
    manufacter = models.ForeignKey(FactoryProfile, on_delete=models.CASCADE)

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
