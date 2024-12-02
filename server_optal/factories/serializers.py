from rest_framework import serializers
from .models import SubCategory, Product, Category, ColorVariation
from main.models import User
from .models import FactoryProfile


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
                  'father', 'manufacter', 'color_variations', "manufacter"]


class FactoryRegistrationSerializer(serializers.ModelSerializer):
    factory_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'factory_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        factory_name = validated_data.pop('factory_name')
        user = User.objects.create_user(**validated_data)
        FactoryProfile.objects.create(user=user, factory_name=factory_name)
        return user


class FactoryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryProfile
        fields = ['user', 'factory_name', 'factory_description']


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryProfile
        fields = ['username', 'first_name', 'factory_name', 'date_joined']
        read_only_fields = ['date_joined']


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
        model = FactoryProfile
        fields = ['avatar']
