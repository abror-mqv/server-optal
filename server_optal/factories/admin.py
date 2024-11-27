from django.contrib import admin
from .models import FactoryProfile, Category, SubCategory, Product, ColorVariation


admin.site.register(FactoryProfile)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(ColorVariation)
