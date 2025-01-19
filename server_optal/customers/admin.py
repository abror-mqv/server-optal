from django.contrib import admin
from customers.models import CustomerProfile, Cart, CartItem, Order
# Register your models here.

admin.site.register(CustomerProfile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
