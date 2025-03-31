from django.http import JsonResponse
from haystack.query import SearchQuerySet
from ..models import Product, FactoryProfile
from ..serializers import ProductSerializer
from rest_framework.response import Response
from urllib.parse import unquote


def search_view(request):
    query = request.GET.get('query', '').strip()
    query = unquote(query)

    # Поиск по товарам
    products = SearchQuerySet().models(Product).filter(content=query)
    has_matched_products = products.count() > 0

    if has_matched_products:
        product_ids = [result.pk for result in products]
        matched_products = Product.objects.filter(id__in=product_ids)
    else:
        matched_products = Product.objects.none()

    # Поиск по боксам
    boxes = FactoryProfile.objects.filter(factory_name__icontains=query)
    has_matched_boxes = boxes.exists()

    if not has_matched_boxes:
        boxes = FactoryProfile.objects.none()

    # 10 случайных товаров для рекомендаций
    random_products = Product.objects.order_by('?')[:10]

    # Формируем ответ
    response_data = {
        'has_matched_products': has_matched_products,
        'has_matched_boxes': has_matched_boxes,
        'matched_boxes': [{'id': box.id, 'factory_name': box.factory_name} for box in boxes] if has_matched_boxes else [],
        'matched_products': ProductSerializer(matched_products, many=True).data if has_matched_products else [],
        'random_products': ProductSerializer(random_products, many=True).data
    }

    return JsonResponse(response_data)
