from rest_framework import serializers
from .models import SubCategory, Product, Category, ColorVariation, PromotionApplication
from main.models import User
from .models import FactoryProfile, Subscription


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
    price_with_commission = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', "price_with_commission", 'sizes', 'description',
                  'father', "store_category", "in_stock", 'manufacter', 'color_variations', "manufacter"]


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
        fields = ['user', 'factory_name',
                  'factory_description', "avatar", "supplier_id"]


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


class ProductInStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'in_stock']


class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class PromotionApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionApplication
        fields = ['product', 'promotion', 'status']
        read_only_fields = ['status']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'box', 'session_id', 'created_at']


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryProfile
        # supplier_id - это твой 6-значный номер
        fields = ['id', 'name', 'description', 'supplier_id']
