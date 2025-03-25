from django.http import JsonResponse
from haystack.query import SearchQuerySet
from ..models import Product, FactoryProfile
from ..serializers import ProductSerializer
from rest_framework.response import Response


def search_view(request):
    query = request.GET.get('query', '').strip()

    # Поиск по товарам с использованием Django-Haystack
    products = SearchQuerySet().filter(content=query)

    # Поиск по боксам
    boxes = FactoryProfile.objects.filter(factory_name__icontains=query)

    # Если нет точных совпадений, возвращаем случайные товары и боксы
    if not products:
        products = Product.objects.all().order_by('?')[:10]
    if not boxes:
        boxes = FactoryProfile.objects.all().order_by('?')[:2]

    # Сериализация товаров с учетом цветовых вариаций
    product_data = []
    for product in products:
        # Сериализация каждого продукта
        serializer = ProductSerializer(product)
        product_data.append(serializer.data)

    # Сериализация боксов
    box_data = []
    for box in boxes:
        box_data.append({
            'id': box.id,
            'factory_name': box.factory_name,
        })

    # Возвращаем JSON-ответ
    response_data = {
        'products': product_data,
        'boxes': box_data,
    }

    return JsonResponse(response_data)
