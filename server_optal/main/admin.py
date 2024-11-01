from django.contrib import admin
from .models import Factory, Category, SubCategory, Product, ColorVariation


admin.site.register(Factory)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(ColorVariation)

