
from rest_framework.views import APIView
import json
from ..models import FactoryProfile, StoreCategory
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


class CreateStoreCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category_name = request.data.get("name")
        if not category_name:
            return Response({"error": "Название категории обязательно"}, status=HTTP_400_BAD_REQUEST)

        store_category = StoreCategory.objects.create(
            factory=FactoryProfile.objects.get(user=request.user), name=category_name)

        return Response({"id": store_category.id, "name": store_category.name}, status=HTTP_201_CREATED)

    def get(self, request):
        """ Получение списка категорий """
        categories = StoreCategory.objects.filter(
            factory=FactoryProfile.objects.get(user=request.user))
        categories_data = [{"id": category.id, "name": category.name}
                           for category in categories]

        return Response(categories_data, status=HTTP_200_OK)


class StoreCategoryUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, category_id):
        """ Изменение названия категории """
        category = get_object_or_404(
            StoreCategory, id=category_id, factory=FactoryProfile.objects.get(user=request.user))

        data = request.data
        new_name = data.get("name")
        if not new_name:
            return Response({"error": "Новое название обязательно"}, status=HTTP_400_BAD_REQUEST)

        category.name = new_name
        category.save()

        return Response({"message": "Название категории обновлено", "id": category.id, "name": category.name}, status=HTTP_200_OK)

    def delete(self, request, category_id):
        """ Удаление категории """
        category = get_object_or_404(
            StoreCategory, id=category_id, factory=FactoryProfile.objects.get(user=request.user))

        # Проверяем, есть ли у категории товары
        if category.products.exists():
            return Response({"error": "Нельзя удалить категорию, в которой есть товары"}, status=HTTP_403_FORBIDDEN)

        category.delete()
        return Response({"message": "Категория удалена"}, status=HTTP_200_OK)
