# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Product, ColorVariation
from .serializers import CartSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        size = request.data.get('size')
        color_id = request.data.get('color_id')
        quantity = request.data.get('quantity')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        color_variation = None
        if color_id:
            try:
                color_variation = ColorVariation.objects.get(
                    id=color_id, product=product)
            except ColorVariation.DoesNotExist:
                return Response({"error": "Color variation not found"}, status=404)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, size=size, color_variation=color_variation)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Item added to cart"}, status=200)

    def delete(self, request):
        product_id = request.data.get('product_id')
        size = request.data.get('size')
        color_id = request.data.get('color_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        color_variation = None
        if color_id:
            try:
                color_variation = ColorVariation.objects.get(
                    id=color_id, product=product)
            except ColorVariation.DoesNotExist:
                return Response({"error": "Color variation not found"}, status=404)

        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.filter(
            cart=cart, product=product, size=size, color_variation=color_variation).first()

        if cart_item:
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=200)
        return Response({"error": "Item not in cart"}, status=404)
