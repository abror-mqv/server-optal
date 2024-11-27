from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CartView
urlpatterns = [
    path('cart', CartView.as_view(), name='category_tree'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
