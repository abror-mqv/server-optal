from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from ..models import Category, Product, SubCategory
from ..serializers import CategoryWithProductsSerializer, ProductSerializer, SubCategorySerializer


class CategoryProductsPagination(PageNumberPagination):
    page_size = 10  # Количество продуктов на одной странице
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id):
        try:
            # Находим категорию
            category = Category.objects.get(id=category_id)

            # Получаем все субкатегории текущей категории
            subcategories = SubCategory.objects.filter(father=category)
            subcategories_data = SubCategorySerializer(
                subcategories, many=True).data

            # Собираем продукты из всех субкатегорий
            subcategory_ids = subcategories.values_list('id', flat=True)
            products = Product.objects.filter(
                father__in=subcategory_ids).order_by('-created_at')

            # Пагинация продуктов
            paginator = CategoryProductsPagination()
            paginated_products = paginator.paginate_queryset(products, request)
            products_data = ProductSerializer(
                paginated_products, many=True).data

            # Формируем ответ
            response_data = {
                "category_name": category.cat_name,  # Добавляем название категории в респонс
                "subcategories": subcategories_data,
                "products": products_data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            return Response({"error": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)


class SubCategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, subcategory_id):
        try:
            # Находим нужную субкатегорию
            subcategory = SubCategory.objects.get(id=subcategory_id)

            # Получаем головную категорию (father)
            parent_category = subcategory.father

            # Получаем список соседних подкатегорий (в той же головной категории)
            sibling_subcategories = SubCategory.objects.filter(
                father=parent_category).exclude(id=subcategory_id)

            # Получаем продукты для данной субкатегории
            products = Product.objects.filter(
                father=subcategory).order_by('-created_at')

            # Пагинация товаров
            paginator = CategoryProductsPagination()
            paginated_products = paginator.paginate_queryset(products, request)
            products_data = ProductSerializer(
                paginated_products, many=True).data

            # Формируем ответ
            response_data = {
                "subcategory_name": subcategory.subcat_name,
                "parent_category_name": parent_category.cat_name,  # Название головной категории
                # Соседние подкатегории
                "sibling_subcategories": SubCategorySerializer(sibling_subcategories, many=True).data,
                "products": products_data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except SubCategory.DoesNotExist:
            return Response({"error": "Субкатегория не найдена"}, status=status.HTTP_404_NOT_FOUND)
