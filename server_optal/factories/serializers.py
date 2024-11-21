from rest_framework import serializers
from .models import SubCategory, Factory, Product, Category, ColorVariation


class SubcatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('subcat_name', 'father')


class SubcatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('product_name', 'father')


class CatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('cat_name')


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'subcat_name']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'cat_name', 'subcategories']


class ColorVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorVariation
        fields = ['color_name', 'color_code', 'image', "product"]


class ProductSerializer(serializers.ModelSerializer):
    # Добавляем поле color_variations как вложенный сериализатор
    color_variations = ColorVariationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'sizes', 'description',
                  'father', 'manufacter', 'color_variations']


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ['username', 'first_name',
                  'factory_name', "factory_description"]


class SubCategoryWithProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer(source='product_set', many=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'subcat_name', 'products']


class CategoryWithProductsSerializer(serializers.ModelSerializer):
    subcategories = SubCategoryWithProductsSerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'cat_name', 'subcategories']


class FactoryAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ['avatar']
