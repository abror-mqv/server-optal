# views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from ..models import PromotionApplication, Product, Promotion, FactoryProfile
from ..serializers import ProductSerializer, PromotionApplicationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import status
import telebot

CHAT_ID = "-1002335132603"
TOPIC_PROMO_APPROVE = 177
bot_token = "7752839364:AAE0nw55hvfrl5G4UZKB5zNeLd_2-bebfRA"


def send_telegram_request(product, promotion, factory):
    bot = telebot.TeleBot(bot_token)
    ms = (
        f"Товар: {product.name}\n"
        f"Ссылка на товар: https://optal.ru/product/{product.id}\n"
        f"Акция: {promotion.title}\n"
        f"Поставщик: {factory.factory_name}\n"
    )
    bot.send_message(CHAT_ID, ms,
                     message_thread_id=TOPIC_PROMO_APPROVE)


class PromotionApplicationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        promotion_id = request.data.get('promotion')

        if not product_id or not promotion_id:
            return Response({"error": "Необходимо указать product и promotion"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            factory = FactoryProfile.objects.get(user=request.user)
        except FactoryProfile.DoesNotExist:
            return Response({"error": "Ваш профиль фабрики не найден"}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(id=product_id, manufacter=factory)
        except Product.DoesNotExist:
            raise PermissionDenied("Товар не найден или не принадлежит вам.")

        try:
            promotion = Promotion.objects.get(id=promotion_id)
        except Promotion.DoesNotExist:
            return Response({"error": "Указанная акция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # Проверка: существует ли уже заявка для этого товара и акции
        if PromotionApplication.objects.filter(product=product, promotion=promotion).exists():
            return Response(
                {"error": "Товар уже подан на эту акцию"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создание заявки
        application = PromotionApplication.objects.create(
            product=product,
            promotion=promotion,
            seller=factory,
            status='approved'
        )

        send_telegram_request(product, promotion, factory)

        return Response({"message": "Заявка успешно подана", "application_id": application.id}, status=status.HTTP_201_CREATED)


class RemoveProductFromPromotionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        product_id = request.data.get('product_id')
        promotion_id = request.data.get('promotion_id')

        if not product_id or not promotion_id:
            return Response({"error": "Необходимо указать product_id и promotion_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            factory = FactoryProfile.objects.get(user=request.user)
        except FactoryProfile.DoesNotExist:
            return Response({"error": "Ваш профиль фабрики не найден"}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(id=product_id, manufacter=factory)
            print(str(product))
        except Product.DoesNotExist:
            return Response({"error": "Товар не найден или не принадлежит вам"}, status=status.HTTP_404_NOT_FOUND)

        try:
            print("DOSHLI DOSYUDA")
            application = PromotionApplication.objects.get(
                product=product, promotion=promotion_id)
            print("DOSHLI DOSYUDA 222")

            application.delete()
            return Response({"message": "Товар успешно удалён из акции"}, status=status.HTTP_204_NO_CONTENT)
        except PromotionApplication.DoesNotExist:
            return Response({"error": "Товар не найден в указанной акции"}, status=status.HTTP_404_NOT_FOUND)


class PromotionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        factory = FactoryProfile.objects.get(user=request.user)
        promotions = Promotion.objects.all()
        response_data = []
        for promotion in promotions:
            user_products_in_promotion = PromotionApplication.objects.filter(
                promotion=promotion,
                product__manufacter=factory,
                status='approved'
            ).count()

            promotion_data = {
                "title": promotion.title,
                "description": promotion.description,
                "description_for_factory": promotion.description_for_factory,
                "recommended_drop": promotion.recommended_drop,
                "user_products_count": user_products_in_promotion,
                "id": promotion.id
            }

            if product_id:  # Проверяем, был ли передан product_id
                try:
                    product = Product.objects.get(
                        id=product_id, manufacter=factory)
                    promotion_data["product_name"] = product.name
                    promotion_data["exist"] = PromotionApplication.objects.filter(
                        product=product,
                        promotion=promotion
                    ).exists()
                except Product.DoesNotExist:
                    return Response({"error": "Товар не найден или не принадлежит вам"}, status=400)

            response_data.append(promotion_data)

        return Response(response_data)


class PromotionProductsView(APIView):
    permission_classes = [AllowAny]  # Доступ открыт для всех

    def get(self, request, promotion_id):
        try:
            promotion = Promotion.objects.get(id=promotion_id)
        except Promotion.DoesNotExist:
            return Response({"error": "Акция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # Выбираем одобренные заявки (товары) для данной акции
        applications = PromotionApplication.objects.filter(
            promotion=promotion, status='approved')

        # Формируем список товаров
        pp = []

        for app in applications:
            product = app.product
            pp.append(product)

        serializer = ProductSerializer(pp, many=True)
        products = serializer.data

        # Формируем ответ с учетом новой модели Promotion
        return Response({
            "promotion_id": str(promotion.id),
            "promotion_title": promotion.title,
            "promotion_description": promotion.description,
            "promotion_type": promotion.promotion_type,
            "description_for_factory": promotion.description_for_factory,
            "recommended_drop": promotion.recommended_drop,
            "products": products
        })
