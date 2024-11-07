import json
from django.forms import JSONField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.serializers import serialize
from .models import Product, Category, SubCategory, Factory, ColorVariation
from .serializers import CategorySerializer, ProductSerializer, ColorVariationSerializer, FactorySerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.generic import DetailView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from telegram import Bot
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication

from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework.permissions import AllowAny


class CatApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class FactoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            factory = request.user
            serializer = FactorySerializer(factory)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Factory.DoesNotExist:
            return Response({"detail": "Factory not found."}, status=status.HTTP_404_NOT_FOUND)


User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        factory_name = request.data.get('factory_name')
        password = request.data.get('password')

        if not all([username, first_name, factory_name, password]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Создайте пользователя
        user = Factory.objects.create_user(
            username=username,
            first_name=first_name,
            factory_name=factory_name,
            password=password
        )

        # Создайте токен
        token = Token.objects.create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class CreateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_data = request.data
        product_data['manufacter'] = request.user.id
        serializer = ProductSerializer(data=product_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColorVariationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        print("Incoming data:", request.data)
        serializer = ColorVariationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Log serializer errors
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FactoryProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        factory = request.user
        products = Product.objects.filter(
            manufacter=factory).prefetch_related('color_variations')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
