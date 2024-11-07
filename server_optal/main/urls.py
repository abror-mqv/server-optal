from django.urls import path
from .views import CatApiView, FactoryDetailView, RegisterView, CreateProductView, ColorVariationCreateView, FactoryProductsView, ProductDetailView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cats', CatApiView.as_view(), name='category_tree'),
    path('register/', RegisterView.as_view(), name='register'),
    path('products/color-variation/', ColorVariationCreateView.as_view(),
         name='create-color-variation'),
    path('get-factory/', FactoryDetailView.as_view(), name='factory-detail'),
    path('factory/products/', FactoryProductsView.as_view(), name='factory-products'),
    path('products/', CreateProductView.as_view(), name='create-product'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
