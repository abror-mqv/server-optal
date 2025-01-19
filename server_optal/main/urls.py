from django.urls import path
from .views import ExchangeRateListView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('utils/exchange-rates',
         ExchangeRateListView.as_view(), name='exchange-rates'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
