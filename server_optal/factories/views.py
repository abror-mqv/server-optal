import json
from django.forms import JSONField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.serializers import serialize
from .models import Product, Category, SubCategory, FactoryProfile, ColorVariation
from .serializers import CategorySerializer, FactoryAvatarSerializer, FactoryProfileSerializer, FactorySerializer, ProductSerializer, ColorVariationSerializer, CategoryWithProductsSerializer, SubCategoryWithProductsSerializer

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
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.generics import RetrieveDestroyAPIView
User = get_user_model()


class CatApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class FactoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            factory = FactoryProfile.objects.get(user=request.user)
            response = {
                "first_name": factory.user.first_name,
                "factory_name": factory.factory_name,
                "factory_description": factory.factory_description
            }
            return Response(response, status=200)
        except FactoryProfile.DoesNotExist:
            return Response({"detail": "Factory not found."}, status=404)


class RegisterFactoryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        factory_name = request.data.get('factory_name')
        password = request.data.get('password')

        if not all([username, first_name, factory_name, password]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            password=password
        )
        FactoryProfile.objects.create(user=user, factory_name=factory_name)
        token = Token.objects.create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class CreateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_data = request.data
        product_data['manufacter'] = FactoryProfile.objects.get(
            user=request.user).id
        # print(str(product_data["manufacter"].id))
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
        factory = FactoryProfile.objects.get(user=request.user)
        print("EFEFEF", factory)
        products = Product.objects.filter(
            manufacter=factory).prefetch_related('color_variations')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class ProductDeleteView(RetrieveDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UpdateFactoryView(APIView):
    def put(self, request, *args, **kwargs):
        factory = FactoryProfile.objects.get(user=request.user)
        serializer = FactorySerializer(
            factory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductsBySubCategoryView(APIView):
    def get(self, request, subcat_id):
        try:
            products = Product.objects.filter(father__id=subcat_id)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SubCategory.DoesNotExist:
            return Response({"error": "Подкатегория не найдена"}, status=status.HTTP_404_NOT_FOUND)


class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            serializer = CategoryWithProductsSerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"error": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)


class SubCategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, subcategory_id):
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
            serializer = SubCategoryWithProductsSerializer(subcategory)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SubCategory.DoesNotExist:
            return Response({"error": "SubКатегория не найдена"}, status=status.HTTP_404_NOT_FOUND)


class LatestProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all().order_by('-created_at')  # Order by newest
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = FactoryProfile.objects.get(
            user=request.user)  # текущий пользователь
        serializer = FactoryAvatarSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Аватарка обновлена успешно", "avatar_url": user.avatar.url}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
