# admin.py
from django.contrib import admin
from .models import ExchangeRate, User

admin.site.register(User)

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency_code', 'rate_to_kgs', 'updated_at')  # Отображаемые поля
    list_editable = ('rate_to_kgs',)  # Поля, которые можно редактировать прямо в списке
    search_fields = ('currency_code',)  # Поиск по коду валюты