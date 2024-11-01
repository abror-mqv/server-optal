import json
from django.forms import JSONField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.serializers import serialize
from .models import Product, Category, SubCategory, Factory
from django.views.generic import DetailView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from telegram import Bot
from django.contrib.auth import get_user_model
from .serializers import CategorySerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view


class CatApiView(APIView):
    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


User = get_user_model()

class RegisterView(APIView):
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