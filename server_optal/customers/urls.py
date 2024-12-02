from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CartView, RegisterCustomerView, LoginCustomerView
urlpatterns = [
    path('cart', CartView.as_view(), name='category_tree'),
    path('register/', RegisterCustomerView.as_view(), name="customer_register"),
    path('login/', LoginCustomerView.as_view(), name="customer_login")


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
