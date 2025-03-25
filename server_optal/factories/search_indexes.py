from haystack import indexes
from .models import Product


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)  # Основное поле для поиска
    price = indexes.DecimalField(model_attr='price')  # Цена
    description = indexes.CharField(model_attr='description')  # Описание
    store_category = indexes.CharField(model_attr='store_category__name')  # Категория магазина

    def get_model(self):
        return Product