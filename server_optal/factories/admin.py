from django.contrib import admin
from .models import CommissionSettings, FactoryProfile, Category, SellerCommission, SubCategory, Product, ColorVariation, StoreCategory


admin.site.register(FactoryProfile)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(ColorVariation)
admin.site.register(StoreCategory)
admin.site.register(CommissionSettings)
admin.site.register(SellerCommission)
