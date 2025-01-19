from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CartView, RegisterCustomerView, LoginCustomerView, CartView, CartUpdateView, CheckoutView, UserProfileView, UpdateCityView, UpdatePhoneNumberView, UpdateNameView, ConfirmOrder, OrderListView, QuickOrderForAuthenticatedUserView, QuickOrderForAnonymousUserView
urlpatterns = [
    path('cart', CartView.as_view(), name='category_tree'),
    path('register/', RegisterCustomerView.as_view(), name="customer_register"),
    path('login/', LoginCustomerView.as_view(), name="customer_login"),
    path('cart/', CartView.as_view(), name="cart"),
    path('cart-update/', CartUpdateView.as_view(), name="cartupdate"),
    path('cart/checkout/', CheckoutView.as_view(), name="checkout"),
    path("get-user-info", UserProfileView.as_view(), name="get-user-info"),
    path("update-city-view", UpdateCityView.as_view(), name="update-city-view"),
    path("update-phone-number", UpdatePhoneNumberView.as_view(),
         name="update-phone-number"),
    path('update-first-name', UpdateNameView.as_view(),
         name="update-first-name"),
    path("cart/checkout/confirm-order/",
         ConfirmOrder.as_view(), name="confirm_order"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("quick-buy-user", QuickOrderForAuthenticatedUserView.as_view(),
         name="quick-buy-user"),
    path("quick-buy-anon", QuickOrderForAnonymousUserView.as_view(),
         name="quick-buy-anon")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
