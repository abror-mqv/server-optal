# serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Product, ColorVariation


class ColorVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorVariation
        fields = ['id', 'color_name', 'color_code', 'image']


class ProductSerializer(serializers.ModelSerializer):
    color_variations = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'sizes', 'description', 'color_variations']

    def get_color_variations(self, product):
        # Получаем корзину из контекста
        cart = self.context.get('cart')
        if not cart:
            return []

        # Фильтруем CartItem по продукту
        cart_items = CartItem.objects.filter(cart=cart, product=product)

        # Создаём список цветовых вариаций с учётом количества
        color_variations = []
        for item in cart_items:
            color_variations.append({
                'id': item.color_variation.id,
                'color_name': item.color_variation.color_name,
                'color_code': item.color_variation.color_code,
                'image': item.color_variation.image.url,
                'quantity': item.quantity
            })
        return color_variations

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    color_variation = ColorVariationSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'color_variation', 'size', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']

    def get_items(self, cart):
        # Получаем список уникальных продуктов в корзине
        products = Product.objects.filter(cartitem__cart=cart).distinct()

        # Используем ProductSerializer для сериализации
        return ProductSerializer(products, many=True, context={'cart': cart}).data


class CartItemUpdateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    color_variation_id = serializers.IntegerField(write_only=True, required=False)
    size = serializers.CharField(write_only=True, required=False)
    quantity = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = CartItem
        fields = ['product_id', 'color_variation_id', 'size', 'quantity']

    def validate(self, data):
        print("HELLO WOKE")
        # Проверяем существование продукта
        product = Product.objects.filter(id=data['product_id']).first()
        if not product:
            raise serializers.ValidationError({"product_id": "Product not found."})

        # Проверяем существование цветовой вариации, если она указана
        if 'color_variation_id' in data:
            color_variation = ColorVariation.objects.filter(
                id=data['color_variation_id'], product=product
            ).first()
            if not color_variation:
                raise serializers.ValidationError(
                    {"color_variation_id": "Color variation not found for this product."}
                )
        
        return data

    def create(self, validated_data):
        cart = self.context['cart']
        product = Product.objects.get(id=validated_data['product_id'])
        color_variation = None

        if 'color_variation_id' in validated_data:
            color_variation = ColorVariation.objects.get(id=validated_data['color_variation_id'])

        # Создаём или обновляем элемент корзины
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color_variation=color_variation,
            size=validated_data.get('size'),
            defaults={'quantity': validated_data['quantity']}
        )

        # Если элемент уже существовал, обновляем его количество
        if not created:
            cart_item.quantity = validated_data['quantity']
            cart_item.save()

        return cart_item