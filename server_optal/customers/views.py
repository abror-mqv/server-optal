# views.py
import json
import telebot
from .models import CartItem, Order, QuickOrder
from django.db import transaction
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
from django.shortcuts import get_object_or_404
from .serializers import CartItemUpdateSerializer
from django.http import JsonResponse

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            customer_profile = user.customer_profile
            city = customer_profile.city
        except CustomerProfile.DoesNotExist:
            city = None
        orders_count = len(Order.objects.filter(user=user))

        user_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "date_joined": user.date_joined,
            "city": city,
            "orders_count": orders_count
        }
        return Response(user_data, status=200)


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

    def post(self, request):
        product_id = request.data.get("product_id")
        color_variation_id = request.data.get("color_variation_id")

        # Проверка наличия product_id
        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)

        # Проверка существования продукта
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        if not color_variation_id:
            color_variation = product.color_variations.first()
            if not color_variation:
                return Response({"error": "No color variations available for this product"}, status=400)
        else:
            try:
                color_variation = ColorVariation.objects.get(
                    id=color_variation_id)
            except ColorVariation.DoesNotExist:
                return Response({"error": "Color variation not found"}, status=404)

        # Получение или создание корзины
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Создание или обновление элемента корзины
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color_variation=color_variation
        )
        cart_item.save()

        return Response({"message": "Item added to cart"}, status=200)

    def get(self, request):
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all().select_related('product', 'color_variation')

        cart_data = []

        # Список всех товаров из корзины
        for item in cart_items:
            product = item.product

            # Собираем все цветовые вариации для продукта
            color_variations = product.color_variations.all()

            # Составляем данные о цветах
            colors_data = []
            for variation in color_variations:
                cart_item = cart_items.filter(
                    product=product, color_variation=variation
                ).first()
                colors_data.append({
                    "id": variation.id,
                    "color_hex": variation.color_code,
                    "color_name": variation.color_name,
                    "image": variation.image.url if variation.image else None,
                    "in_stock": True,
                    "quantity": cart_item.quantity if cart_item else 0
                })

            # Добавляем товар с его цветами
            # если в массиве cart_data ещё нет элемента, с полем product_id, равным полу product_id текущего product, то добавь туда текущий продукт
            if not any(item['product_id'] == product.id for item in cart_data):
                cart_data.append({
                    "product_id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price),
                    "sizes": product.sizes,
                    "color_variations": colors_data
                })

        return Response(cart_data, status=status.HTTP_200_OK)

    def delete(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        cart = get_object_or_404(Cart, user=request.user)
        deleted_count, _ = CartItem.objects.filter(
            cart=cart, product_id=product_id).delete()
        if deleted_count == 0:
            return Response({"message": "No items found for the given product ID."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": f"Deleted {deleted_count} item(s) from the cart."}, status=status.HTTP_200_OK)


class CartUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        data = request.data.get('cart', [])

        updated_items = []
        print("UPDAGIGN")
        print(str(data))

        for item in data:
            product_id = item.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            for color in item.get('colors', []):
                color_variation_id = color.get('color_id')
                quantity = color.get('quantity', 0)
                color_variation = get_object_or_404(
                    ColorVariation, id=color_variation_id)
                if quantity == 0:
                    CartItem.objects.filter(
                        cart=cart,
                        product=product,
                        color_variation=color_variation
                    ).delete()
                    continue

                cart_item, _ = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    color_variation=color_variation
                )

                cart_item.quantity = quantity
                cart_item.save()

        return Response({"message": "Cart updated successfully"}, status=status.HTTP_200_OK)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all().select_related('product', 'color_variation')

        cart_data = []

        # Список всех товаров из корзины
        for item in cart_items:
            product = item.product

            # Собираем все цветовые вариации для продукта
            color_variations = product.color_variations.all()

            # Составляем данные о цветах
            colors_data = []
            for variation in color_variations:
                cart_item = cart_items.filter(
                    product=product, color_variation=variation
                ).first()
                colors_data.append({
                    "id": variation.id,
                    "color_hex": variation.color_code,
                    "color_name": variation.color_name,
                    "image": variation.image.url if variation.image else None,
                    "in_stock": True,
                    "quantity": cart_item.quantity if cart_item else 0,
                    "color_cost": int(cart_item.quantity) * int(product.price) * int(len(product.sizes))
                })

            # Добавляем товар с его цветами
            # если в массиве cart_data ещё нет элемента, с полем product_id, равным полу product_id текущего product, то добавь туда текущий продукт
            if not any(item['product_id'] == product.id for item in cart_data):
                cart_data.append({
                    "product_id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price),
                    "sizes": product.sizes,
                    "color_variations": colors_data,
                    "total_cost": sum([color['color_cost'] for color in colors_data]),
                    "total_quantity": sum([color['quantity'] for color in colors_data]),
                    "overall_quantity": len(product.sizes)
                })

        return Response(cart_data, status=status.HTTP_200_OK)


class UpdateCityView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Пользователь не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)
        new_city = request.data.get('city')

        if not new_city:
            return Response({"error": "Название города не указано"}, status=status.HTTP_400_BAD_REQUEST)
        customer_profile = get_object_or_404(CustomerProfile, user=user)
        customer_profile.city = new_city
        customer_profile.save()
        return Response({"message": "Город успешно обновлен", "new_city": customer_profile.city}, status=status.HTTP_200_OK)


class UpdatePhoneNumberView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Пользователь не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)
        new_phone_number = request.data.get('phone_number')

        if not new_phone_number:
            return Response({"error": "Номер телефона не указан"}, status=status.HTTP_400_BAD_REQUEST)
        if not new_phone_number.isdigit() or len(new_phone_number) < 10 or len(new_phone_number) > 15:
            return Response({"error": "Неверный формат номера телефона"}, status=status.HTTP_400_BAD_REQUEST)
        user.username = new_phone_number
        user.save()
        return Response({"message": "Номер телефона успешно обновлен", "new_phone_number": user.username}, status=status.HTTP_200_OK)


class UpdateNameView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Пользователь не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)
        new_name = request.data.get('name')

        if not new_name:
            return Response({"error": "Имя не указано"}, status=status.HTTP_400_BAD_REQUEST)
        user.first_name = new_name
        user.save()

        return Response({"message": "Имя успешно обновлено", "new_name": user.first_name}, status=status.HTTP_200_OK)


def format_detailed_snapshot(detailed_snapshot, customer_snapshot):
    """Форматируем detailed_snapshot для отправки в Telegram."""

    try:
        # Предполагаем, что detailed_snapshot уже является списком Python
        snapshot_list = detailed_snapshot
        message = "🛒 *Новый заказ*\n\n\n\n"

        for i, item in enumerate(snapshot_list, start=1):
            message += f"📦 # {i}\n"
            message += f"Название: {item['name']}\n"
            message += f"Общая стоимость: {item['total_cost']} руб.\n"
            message += f"Количество: {item['total_quantity']} линеек.\n"

            message += "\n🎨 *Вариации цветов:*\n"
            for color in item['color_variations']:
                message += f"  - {color['color_name']}\n"
                message += f"    К: {color['quantity']} линеек, Ц: {color['color_cost']} руб.\n"
                # message += f"    Ссылка на изображение: {color['image']}\n"

            message += "\n🏭 *Данные цеха:*\n"
            message += f"Имя: {item['manufacter']['name']}\n"
            message += f"Название цеха: {item['manufacter']['factory_name']}\n"
            message += f"Контакт: {item['manufacter']['phone_number']}\n\n\n\n"

        message += f"\nДанные заказчика:\n"
        message += f"    Имя: {customer_snapshot['user']['first_name']}\n"
        message += f"    Номер телефона: {customer_snapshot['user']['username']}\n"
        message += f"    Город доставки: {customer_snapshot['city_delivery']}\n"
        message += f"    Дата создания заказа: {customer_snapshot['order_meta']['created_at']}\n"

        return message
    except Exception as e:
        return f"Ошибка форматирования 123: {e}"


class ConfirmOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user
        snapshot = request.data
        if not snapshot:
            return JsonResponse({"error": "Snapshot is required"}, status=400)

        customer_snapshot = {
            "user": {
                "username": user.username,
                "first_name": user.first_name,
            },
            "city_delivery": user.customer_profile.city,
            "order_meta": {
                "created_at": None,  # Временно None, обновится после сохранения заказа
            },
        }
        simplified_snapshot = []  # Для клиента
        detailed_snapshot = []  # Для менеджера

        for product in snapshot.get("snapshot"):
            product_id = product.get("product_id")
            name = product.get("name")
            description = product.get("description")
            price = product.get("price")
            total_cost = product.get("total_cost")
            total_quantity = product.get("total_quantity")
            color_variations = product.get("color_variations", [])

            # Упрощенный снэпшот: только основные данные о товаре и цветах
            simplified_colors = [
                {
                    "id": variation["id"],
                    "color_name": variation["color_name"],
                    "color_hex": variation["color_hex"],
                    "image": variation["image"],
                    "quantity": variation["quantity"],
                    "color_cost": variation["color_cost"]
                }

                for variation in color_variations
            ]

            simplified_snapshot.append({
                "product_id": product_id,
                "name": name,
                "price": price,
                "total_quantity": total_quantity,
                "total_cost": total_cost,
                "color_variations": simplified_colors,
                "sizes": product.get("sizes"),
                "description": product.get("description"),
                "overall_quantity": product.get("overall_quantity")
            })

            detailed_colors = [
                {
                    "id": variation["id"],
                    "color_name": variation["color_name"],
                    "quantity": variation["quantity"],
                    "color_cost": variation["color_cost"],
                    "color_hex": variation["color_hex"],
                    "image": variation["image"],

                }
                for variation in color_variations
            ]
            product_md = Product.objects.get(id=product_id)
            detailed_snapshot.append({
                "product_id": product_id,
                "name": name,
                "description": description,
                "price": price,
                "total_quantity": total_quantity,
                "total_cost": total_cost,
                "color_variations": detailed_colors,
                "manufacter": {
                    "factory_name": product_md.manufacter.factory_name,
                    "name": product_md.manufacter.user.first_name,
                    "phone_number": product_md.manufacter.user.username,
                }
            })

        order = Order.objects.create(
            user=user,
            snapshot=simplified_snapshot,
            detailed_snapshot=detailed_snapshot,
            is_confirmed=False,
            city_delivery=user.customer_profile.city
        )
        customer_snapshot["order_meta"]["created_at"] = order.created_at.strftime(
            "%Y-%m-%d %H:%M:%S")
        order.customer_snapshot = customer_snapshot
        order.save()

        User = get_user_model()
        BOT_TOKEN = "7752839364:AAE0nw55hvfrl5G4UZKB5zNeLd_2-bebfRA"
        CHAT_IDS = ["7471817775", "1901696570"]
        bot = telebot.TeleBot(BOT_TOKEN)
        for chat_id in CHAT_IDS:
            message = format_detailed_snapshot(
                detailed_snapshot, customer_snapshot)
            print('123', message)
            try:
                bot.send_message(chat_id, message)
                print("Сообщение успешно отправлено!")
            except Exception as e:
                bot.send_message(chat_id, "Ошибка форматирования")
                print(f"Ошибка отправки сообщения: {e}")

        return JsonResponse({"message": "Order confirmed", "order_id": order.id}, status=201)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Текущий авторизованный пользователь
        orders = Order.objects.filter(user=user).order_by(
            '-created_at')  # Заказы пользователя

        # Формируем массив с заказами
        orders_list = [
            {
                "id": order.id,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": order.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                # Возвращает текстовое представление статуса
                "status": order.get_status_display(),
                "is_confirmed": order.is_confirmed,
                "snapshot": order.snapshot,  # JSON-объект
            }
            for order in orders
        ]

        return JsonResponse({"orders": orders_list}, status=200)


class QuickOrderForAuthenticatedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        user = request.user

        quick_order = QuickOrder.objects.create(
            product_id=product_id,
            user=user
        )
        self.send_telegram_notification(quick_order)
        return Response({"message": "Quick order created successfully."}, status=status.HTTP_201_CREATED)

    def send_telegram_notification(self, quick_order):
        bot_token = "7752839364:AAE0nw55hvfrl5G4UZKB5zNeLd_2-bebfRA"
        chat_ids = ["7471817775", "1901696570"]
        message = (
            f"🛒 Новый быстрый заказ:\n"
            f"Товар ID: {quick_order.product_id}\n"
            f"https://optal.ru/product/{quick_order.product_id}\n"
            f"User ID: {quick_order.user.id}\n"
            f"Номер: {quick_order.user}\n"
            f"Имя: {quick_order.user.first_name}\n"
            f"Время заказа: {quick_order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        bot = telebot.TeleBot(bot_token)
        for chat_id in chat_ids:
            try:
                bot.send_message(chat_id, message)
                print("Сообщение успешно отправлено!")
            except Exception as e:
                bot.send_message(chat_id, "Ошибка форматирования")
                print(f"Ошибка отправки сообщения: {e}")


class QuickOrderForAnonymousUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        product_id = request.data.get("product_id")
        phone_number = request.data.get("phone_number")
        quick_order = QuickOrder.objects.create(
            product_id=product_id,
            phone_number=phone_number
        )
        self.send_telegram_notification(quick_order)

        return Response({"message": "Quick order created successfully."}, status=status.HTTP_201_CREATED)

    def send_telegram_notification(self, quick_order):
        bot_token = "7752839364:AAE0nw55hvfrl5G4UZKB5zNeLd_2-bebfRA"
        chat_ids = ["7471817775", "1901696570"]
        message = (
            f"🛒 Новый быстрый заказ:\n"
            f"Товар ID: {quick_order.product_id}\n"
            f"https://optal.ru/product/{quick_order.product_id}\n"
            f"Телефон: {quick_order.phone_number}\n"
            f"Время заказа: {quick_order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot = telebot.TeleBot(bot_token)
        for chat_id in chat_ids:
            try:
                bot.send_message(chat_id, message)
                print("Сообщение успешно отправлено!")
            except Exception as e:
                bot.send_message(chat_id, "Ошибка форматирования")
                print(f"Ошибка отправки сообщения: {e}")
