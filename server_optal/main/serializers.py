from rest_framework import serializers
from .models import SubCategory, Product, Category


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


