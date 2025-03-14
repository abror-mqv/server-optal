# views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from ..models import PromotionApplication, Product, Promotion, FactoryProfile
from ..serializers import PromotionApplicationSerializer
from rest_framework.permissions import IsAuthenticated
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

        print('SKU_ID: '+str(product_id))
        print('PRO_ID: '+str(promotion_id))
        print("RQUS: "+str(request.user))
        print("RQUS: ")
        factory = FactoryProfile.objects.get(user=request.user)

        try:
            product = Product.objects.get(
                id=product_id, manufacter=factory)
            print("PRODUCT SUCCESS: ", str(product))
        except Product.DoesNotExist:
            raise PermissionDenied("Товар не найден или не принадлежит вам.")

        try:
            promotion = Promotion.objects.get(id=promotion_id)
            print("PROMO SUCCESS: "+str(promotion))
        except Promotion.DoesNotExist:
            return Response({"error": "Указанная акция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # Создание заявки
        application = PromotionApplication.objects.create(
            product=product,
            promotion=promotion,
            seller=factory,  # ВАЖНО! Устанавливаем текущего пользователя как продавца
            status='approved'
        )

        send_telegram_request(product, promotion, factory)

        return Response({"message": "Заявка успешно подана", "application_id": application.id}, status=status.HTTP_201_CREATED)


class PromotionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        promotions = Promotion.objects.all()
        response_data = []

        for promotion in promotions:
            factory = FactoryProfile.objects.get(user=request.user)
            user_products_in_promotion = PromotionApplication.objects.filter(
                promotion=promotion,
                product__manufacter=factory,
                status='approved'
            ).count()

            response_data.append({
                "title": promotion.title,
                "description": promotion.description,
                "description_for_factory": promotion.description_for_factory,
                "recommended_drop": promotion.recommended_drop,
                "user_products_count": user_products_in_promotion,
                "id": promotion.id
            })

        # for promotion in promotions:
        #     # Считаем количество одобренных заявок на товары текущего пользователя
        #     user_products_in_promotion = PromotionApplication.objects.filter(
        #         promotion=promotion,
        #         product__seller=request.user,
        #         status='approved'
        #     ).count()

        #     response_data.append({
        #         "id": str(promotion.id),  # Приводим к строке, чтобы не было проблем с сериализацией
        #         "title": promotion.title,
        #         "description": promotion.description,
        #         "banner_url": promotion.banner.url if promotion.banner else None,
        #         "user_products_count": user_products_in_promotion
        #     })

        return Response(response_data)
