# serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Product, ColorVariation


class ColorVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorVariation
        fields = ['id', 'color_name', 'color_code', 'image']


class ProductSerializer(serializers.ModelSerializer):
    color_variations = ColorVariationSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'sizes',
                  'description', 'color_variations']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    color_variation = ColorVariationSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'color_variation', 'size', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
