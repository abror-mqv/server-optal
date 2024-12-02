# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Product, ColorVariation
from .serializers import CartSerializer

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from customers.models import CustomerProfile
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

User = get_user_model()


class RegisterCustomerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username') 
        first_name = request.data.get('first_name')
        password = request.data.get('password')
        if not all([username, first_name, password]):
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "User with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            password=password
        )
        CustomerProfile.objects.create(user=user)

        token = Token.objects.create(user=user)

        return Response(
            {"token": token.key},
            status=status.HTTP_201_CREATED
        )


class LoginCustomerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not all([username, password]):
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED 
            )
        if not hasattr(user, 'customer_profile'):
            return Response(
                {"error": "User is not a customer."},
                status=status.HTTP_403_FORBIDDEN
            )
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key},
            status=status.HTTP_200_OK
        )


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
