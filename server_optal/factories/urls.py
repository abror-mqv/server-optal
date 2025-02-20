from django.urls import path
from .views import CatApiView, FactoryProductsView, RegisterBoxView, FactoryProductsViewBoxViewD, ColorVariationUpdateImageView, ColorVariationDeleteView, FactoryDetailView, LoginFactoryView, GetOneProduct, LatestProductsView, SubCategoryDetailView, CategoryDetailView, UpdateAvatarView, UpdateFactoryView, RegisterFactoryView, CreateProductView, ColorVariationCreateView, FactoryProductsView, ProductDetailView, ProductDeleteView, UpdateProductView, ColorVariationUpdateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cats', CatApiView.as_view(), name='category_tree'),
    path('register/', RegisterFactoryView.as_view(), name='register'),
    path('login/', LoginFactoryView.as_view(), name='login'),
    path('get-factory/', FactoryDetailView.as_view(), name='factory-detail'),
    path('factory/products/', FactoryProductsView.as_view(),
         name='factory-products'),

    path('products/', CreateProductView.as_view(), name='create-product'),
    path('products/color-variation/', ColorVariationCreateView.as_view(),
         name='create-color-variation'),

    path("products/update/<int:product_id>/",
         UpdateProductView.as_view(), name='update_product'),
    path("products/color-variation/update/<int:color_variation_id>/",
         ColorVariationUpdateView.as_view(), name='update_color_variation'),
    path("product/color-variation/update-image/<int:color_variation_id>/",
         ColorVariationUpdateImageView.as_view(), name="update_color_variation_image"),
    path("product/color-variation/delete-color-variation/<int:color_variation_id>/",
         ColorVariationDeleteView.as_view(), name="color_variation_delete"),

    path('products/<int:pk>/', GetOneProduct.as_view(), name='product-detail'),
    path('factory/products/<int:pk>/',
         ProductDeleteView.as_view(), name='delete-product'),
    path('factory/update/', UpdateFactoryView.as_view(), name='update-factory'),
    path('factory/update-avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('category/<int:category_id>/',
         CategoryDetailView.as_view(), name='category-detail'),
    path('latest-products/', LatestProductsView.as_view(), name='latest-products'),
    path('subcategory/<int:subcategory_id>/',
         SubCategoryDetailView.as_view(), name='subcategory-detail'),

    path("get-products-by-supplier-id/<int:supplier_id>/",
         FactoryProductsViewBoxViewD.as_view(), name="box-products"),

    path("box-create/", RegisterBoxView.as_view(), name="box_create")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
