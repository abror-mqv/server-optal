from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser, UserManager
from django.utils import timezone
# from django.contrib.auth.models import User
from main.models import User


class FactoryProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='factory_profile')
    factory_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    factory_description = models.TextField(null=True, blank=True)
    visit_count = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True, verbose_name="Аватарка", default=None)
    supplier_id = models.CharField(
        max_length=6, editable=True, unique=True)
    imagoco = models.CharField(
        max_length=255, null=True, blank=True, default="")

    def get_commission(self):
        custom_commission = SellerCommission.objects.filter(
            seller=self).first()
        if custom_commission:
            return custom_commission.custom_percentage
        return CommissionSettings.objects.first().percentage

    def increment_visit_count(self):
        self.visit_count += 1
        self.save(update_fields=["visit_count"])

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


class StoreCategory(models.Model):
    factory = models.ForeignKey(
        "FactoryProfile", on_delete=models.CASCADE, related_name="store_categories")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.factory.factory_name} - {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def price_with_commission(self):
        commission_percentage = self.manufacter.get_commission() / 100
        return self.price * (1 + commission_percentage)
    
    in_stock = models.BooleanField(default=True)
    sizes = models.JSONField(
        verbose_name='Размеры',
        default=list,
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name="Описание", max_length=255, default=None)
    father = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    store_category = models.ForeignKey(
        StoreCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

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
        upload_to='color_variant_images/', null=True, blank=True, max_length=255)

    def __str__(self):
        return f"{self.color_name} - {self.product.name}"


class CommissionSettings(models.Model):
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.0)

    def __str__(self):
        return f"Текущая комиссия: {self.percentage}%"


class SellerCommission(models.Model):
    seller = models.OneToOneField(FactoryProfile, on_delete=models.CASCADE)
    custom_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.seller.name} - {self.custom_percentage}%"
