from django.urls import path

from .views import CatApiView, FactoryProductsView, FactoryProductsViewBoxViewD, ColorVariationUpdateImageView, ColorVariationDeleteView, FactoryDetailView, LoginFactoryView, GetOneProduct, SubCategoryDetailView, CategoryDetailView, UpdateAvatarView, UpdateFactoryView, RegisterFactoryView, CreateProductView, ColorVariationCreateView, FactoryProductsView, ProductDetailView, ProductDeleteView, UpdateProductView, ColorVariationUpdateView
from .shared_views.stock_update import UpdateProductStockView
from .shared_views.store_category import CreateStoreCategoryView, StoreCategoryUpdateDeleteView
from .shared_views.get_my_percentage import GetMyPercentage
from .shared_views.register_box import RegisterBoxView
from .shared_views.promotions import PromotionApplicationCreateView, PromotionListView, PromotionProductsView, RemoveProductFromPromotionView
from .shared_views.subscribe import SubscriptionViewSet, get_suppliers_info
from .shared_views.feed import LatestProductsView

from django.conf import settings
from django.conf.urls.static import static


subscription_create_view = SubscriptionViewSet.as_view({'post': 'create'})
subscription_list_view = SubscriptionViewSet.as_view(
    {'get': 'my_subscriptions'})
subscription_unsubscribe_view = SubscriptionViewSet.as_view(
    {'post': 'unsubscribe'})

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

    path("get-products-by-supplier-id/<str:supplier_id>/",
         FactoryProductsViewBoxViewD.as_view(), name="box-products"),

    path("box-create/", RegisterBoxView.as_view(), name="box_create"),
    path('products/<int:product_id>/update-stock/',
         UpdateProductStockView.as_view(), name='update-product-stock'),
    path("store-categories/create/", CreateStoreCategoryView.as_view(),
         name="create-store-category"),

    path('store-categories/eidt/<int:category_id>/',
         StoreCategoryUpdateDeleteView.as_view(), name='store-category-edit-delete'),
    path('get-my-percentage/', GetMyPercentage.as_view(), name='get-my-percentage'),
    path('promotions/apply/', PromotionApplicationCreateView.as_view(),
         name='promotion-apply'),
    path('promotions/getlist/<int:product_id>/',
         PromotionListView.as_view(), name='promotion-list'),
    path('promotions/<str:promotion_id>/products/',
         PromotionProductsView.as_view(), name='promotion-products'),
    path('promotions/remove-product/', RemoveProductFromPromotionView.as_view(),
         name='remove-product-from-promotion'),


    path('subscriptions/', subscription_create_view,
         name='subscription-create'),
    path('subscriptions/my/', subscription_list_view, name='subscription-list'),
    path('subscriptions/unsubscribe/',
         subscription_unsubscribe_view, name='subscription-unsubscribe'),
    path('get_suppliers_info/', get_suppliers_info),
    path('latest-products/', LatestProductsView.as_view(), name='latest-products'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
