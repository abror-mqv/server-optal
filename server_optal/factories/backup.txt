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
from django.core import serializers

from rest_framework import viewsets
from django.contrib.auth import authenticate

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


class LoginFactoryView(APIView):
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
        print(str(user))
        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not hasattr(user, 'factory_profile'):
            return Response(
                {"error": "User is not a factory."},
                status=status.HTTP_403_FORBIDDEN
            )
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


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
    # print(str(serializer_class))
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class GetOneProduct(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product_qs = Product.objects.filter(
            pk=pk
        ).prefetch_related('color_variations')
        if not product_qs.exists():
            return JsonResponse({"error": "Product not found"}, status=404)
        product = product_qs.first()
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "sizes": product.sizes,
            "description": product.description,
            "father": product.father.id if product.father else None,
            "overall_rating": 4.7,
            "feedbacks": [],
            # "manufacter_id": product.manufacter.id if product.manufacter else None,
            "manufacter": {
                "factory_name": product.manufacter.factory_name,
                "factory_avatar": None,
                "factory_id": product.manufacter.id
            },
            "category": {
                "category": {
                    "id": product.father.father.id,
                    "name": product.father.father.cat_name
                },
                "subcategory":  {
                    "id": product.father.id,
                    "name": product.father.subcat_name
                },
            },
            "created_at": product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "color_variations": [
                {
                    "id": variation.id,
                    "color_name": variation.color_name,
                    "color_code": variation.color_code,
                    "image": request.build_absolute_uri(variation.image.url) if variation.image else None,
                }
                for variation in product.color_variations.all()
            ],
        }
        return JsonResponse(product_data, status=200)


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
        print("HEELLO", str(factory.factory_name))
        print("HEELLO", str(factory.factory_description))
        print("REQUEST", str(request.data["factory_description"]))

        try:
            factory.factory_name = request.data["factory_name"]
            factory.factory_description = request.data["factory_description"]
            factory.save()
            return Response({"desc_n": factory.factory_description, "name_n": factory.factory_name}, status=status.HTTP_200_OK)

        except:
            print("EEFHEHHFEHFHEH")
            return Response("BAD", status=status.HTTP_400_BAD_REQUEST)


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
