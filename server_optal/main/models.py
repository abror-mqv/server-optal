from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser, UserManager
# Create your models here.


class Factory(AbstractUser):
    factory_name = models.CharField(max_length=255)

    # Вы можете добавить дополнительные методы или свойства, если нужно
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
    siezes = models.CharField(
        verbose_name='Размеры', default=None, max_length=63, null=True, blank=True)
    description = models.TextField(
        verbose_name="Описание", max_length=255, default=None)
    father = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    manufacter = models.ForeignKey(Factory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ColorVariation(models.Model):
    product = models.ForeignKey(
        Product, related_name='color_variations', on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)
    # Для хранения HEX-кода, например #FFFFFF
    color_code = models.CharField(max_length=7)
    # Изображение товара в данном цвете
    image = models.ImageField(upload_to='media/products/colors/')

    def __str__(self):
        return f"{self.color_name} - {self.product.name}"
