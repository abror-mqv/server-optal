from django.urls import path
from .views import CatApiView, FactoryDetailView, LoginFactoryView, GetOneProduct, LatestProductsView, SubCategoryDetailView, CategoryDetailView, UpdateAvatarView, UpdateFactoryView, RegisterFactoryView, CreateProductView, ColorVariationCreateView, FactoryProductsView, ProductDetailView, ProductDeleteView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cats', CatApiView.as_view(), name='category_tree'),
    path('register/', RegisterFactoryView.as_view(), name='register'),
    path('login/', LoginFactoryView.as_view(), name='login'),


    path('products/color-variation/', ColorVariationCreateView.as_view(),
         name='create-color-variation'),
    path('get-factory/', FactoryDetailView.as_view(), name='factory-detail'),
    path('factory/products/', FactoryProductsView.as_view(),
         name='factory-products'),
    path('products/', CreateProductView.as_view(), name='create-product'),



    #     path('productsold/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/', GetOneProduct.as_view(), name='product-detail'),




    path('factory/products/<int:pk>/',
         ProductDeleteView.as_view(), name='delete-product'),
    path('factory/update/', UpdateFactoryView.as_view(), name='update-factory'),
    path('factory/update-avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('category/<int:category_id>/',
         CategoryDetailView.as_view(), name='category-detail'),
    path('latest-products/', LatestProductsView.as_view(), name='latest-products'),
    path('subcategory/<int:subcategory_id>/',
         SubCategoryDetailView.as_view(), name='subcategory-detail')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
