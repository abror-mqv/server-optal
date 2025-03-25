from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.core.serializers import serialize
from .models import Product, Category, StoreCategory, SubCategory, FactoryProfile, ColorVariation
from .serializers import CategorySerializer, FactoryAvatarSerializer, FactoryProfileSerializer, FactorySerializer, ProductSerializer, ColorVariationSerializer, CategoryWithProductsSerializer, SubCategoryWithProductsSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.generic import DetailView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from django.core import serializers
from rest_framework import viewsets
from django.contrib.auth import authenticate
import random
from django.db.models import Prefetch
from io import BytesIO
import qrcode

import telebot
import string


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
                "factory_description": factory.factory_description,
                "factory_avatar": request.build_absolute_uri(factory.avatar.url) if factory.avatar else None,
                "supplier_id": factory.supplier_id
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
        supplier_id = self.generate_unique_supplier_id()

        if not all([username, first_name, factory_name, password]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            password=password
        )
        FactoryProfile.objects.create(
            user=user, factory_name=factory_name,  supplier_id=supplier_id)
        token = Token.objects.create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)

    def generate_unique_supplier_id(self):
        while True:
            supplier_id = ''.join(random.choices('0123456789', k=6))
            if not FactoryProfile.objects.filter(supplier_id=supplier_id).exists():
                return supplier_id


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
        product_data = request.data.copy()
        try:
            product_data['manufacter'] = FactoryProfile.objects.get(
                user=request.user).id
        except FactoryProfile.DoesNotExist:
            return Response({"error": "Factory profile not found"}, status=status.HTTP_400_BAD_REQUEST)
        sizes_raw = product_data.get('sizes')
        if sizes_raw:
            try:
                sizes_json = [size.strip() for size in sizes_raw.split(',')]
                product_data['sizes'] = sizes_json
            except Exception as e:
                return Response({"error": f"Invalid sizes format: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(data=product_data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({"id": product.id, "message": "Product created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColorVariationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data.copy()
        product_id = data.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except (Product.DoesNotExist, ValueError):
            return Response({"error": "Invalid product ID provided"}, status=status.HTTP_400_BAD_REQUEST)
        data['product'] = product.id
        serializer = ColorVariationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, product_id):
        try:
            product = Product.objects.get(
                id=product_id, manufacter__user=request.user)
        except Product.DoesNotExist:
            return Response({"error": "Product not found or you do not have permission to edit this product"},
                            status=status.HTTP_404_NOT_FOUND)

        product_data = request.data.copy()

        # Преобразуем размеры в JSON-объект, если переданы
        sizes_raw = product_data.get('sizes')
        if sizes_raw:
            try:
                sizes_json = [size.strip() for size in sizes_raw.split(',')]
                product_data['sizes'] = sizes_json
            except Exception as e:
                return Response({"error": f"Invalid sizes format: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(
            product, data=product_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated successfully", "product": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColorVariationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, color_variation_id):
        try:
            color_variation = ColorVariation.objects.get(
                id=color_variation_id, product__manufacter__user=request.user)
        except ColorVariation.DoesNotExist:
            return Response({"error": "Color variation not found or you do not have permission to edit this color variation"},
                            status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        serializer = ColorVariationSerializer(
            color_variation, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Color variation updated successfully", "color_variation": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FactoryProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        factory = FactoryProfile.objects.get(user=request.user)
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
        avatar = product.manufacter.avatar
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "price_with_commission": str(product.price_with_commission),
            "sizes": product.sizes,
            "description": product.description,
            "father": product.father.id if product.father else None,
            "overall_rating": 4.7,
            "feedbacks": [],
            # "manufacter_id": product.manufacter.id if product.manufacter else None,
            "manufacter": {
                "factory_name": product.manufacter.factory_name,
                "factory_avatar": request.build_absolute_uri(avatar.url) if avatar else None,
                "factory_id": product.manufacter.id,
                "factory_description": product.manufacter.factory_description,
                "supplier_id": product.manufacter.supplier_id
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
        products = Product.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        user = FactoryProfile.objects.get(
            user=request.user)  # текущий пользователь
        serializer = FactoryAvatarSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Аватарка обновлена успешно", "avatar_url": user.avatar.url}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ColorVariationUpdateImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, color_variation_id):
        try:
            color_variation = ColorVariation.objects.get(id=color_variation_id)
        except ColorVariation.DoesNotExist:
            return Response({"error": "Color variation not found"}, status=status.HTTP_404_NOT_FOUND)

        image = request.FILES.get("image")
        if not image:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        color_variation.image = image
        color_variation.save()

        return Response({"message": "Image updated successfully", "image_url": color_variation.image.url}, status=status.HTTP_200_OK)


class ColorVariationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, color_variation_id):
        color_variation = get_object_or_404(
            ColorVariation, id=color_variation_id)
        if color_variation.product.manufacter.user != request.user:
            return Response({"error": "У вас нет прав на удаление этой вариации."}, status=status.HTTP_403_FORBIDDEN)

        color_variation.delete()
        return Response({"message": "Цветовая вариация удалена."}, status=status.HTTP_204_NO_CONTENT)


class FactoryProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        factory = FactoryProfile.objects.get(user=request.user)

        # Все товары фабрики
        all_products = Product.objects.filter(
            manufacter=factory).prefetch_related('color_variations')

        # Продукты без store_category
        uncategorized_products = all_products.filter(
            store_category__isnull=True)

        # Категории с их продуктами
        store_categories = StoreCategory.objects.filter(factory=factory).prefetch_related(
            Prefetch('products', queryset=all_products.filter(
                store_category__isnull=False))
        )

        # Формируем список категорий
        categories_data = [
            {
                "id": None,
                "name": "Без раздела",
                "products": ProductSerializer(uncategorized_products, many=True).data
            }
        ] + [
            {
                "id": category.id,
                "name": category.name,
                "products": ProductSerializer(category.products.all(), many=True).data
            }
            for category in store_categories
        ]

        return Response(categories_data, status=HTTP_200_OK)


class FactoryProductsViewBoxViewD(APIView):

    permission_classes = [AllowAny]

    def get(self, request, supplier_id):
        try:
            factory = FactoryProfile.objects.get(supplier_id=supplier_id)
            avatar = factory.avatar
        except FactoryProfile.DoesNotExist:
            return Response({"error": "Factory not found"}, status=status.HTTP_404_NOT_FOUND)
        factory.increment_visit_count()

        all_products = Product.objects.filter(
            manufacter=factory).prefetch_related('color_variations')
        uncategorized_products = all_products.filter(
            store_category__isnull=True)
        store_categories = StoreCategory.objects.filter(factory=factory).prefetch_related(
            Prefetch('products', queryset=all_products.filter(
                store_category__isnull=False))
        )
        categories_data = [
            {
                "id": None,  # Фейковый id для "Без раздела"
                "name": "Без раздела",
                "products": ProductSerializer(uncategorized_products, many=True).data
            }
        ] + [
            {
                "id": category.id,
                "name": category.name,
                "products": ProductSerializer(category.products.all(), many=True).data
            }
            for category in store_categories
        ]

        return Response({
            "factory_name": factory.factory_name,
            "factory_description": factory.factory_description,
            "visit_count": factory.visit_count,
            "factory_avatar": request.build_absolute_uri(avatar.url) if avatar else None,
            "supplier_id": supplier_id,

            "products": categories_data
        })
