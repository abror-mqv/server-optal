from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import FactoryProfile
from rest_framework.authtoken.models import Token
from rest_framework import status
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import telebot
import qrcode
import random
import os
from django.conf import settings
import string

CHAT_ID = "-1002335132603"
TOPIC_QRACCOUNT = 3
TOPIC_QRCATALOG = 5

TEMPLATE_PATH = os.path.join(
    settings.MEDIA_ROOT, "templates/template.png")

TEMPLATE_ACCOUNT_PATH = os.path.join(
    settings.MEDIA_ROOT, "templates/account_template.png")

# Путь к шрифту (замени на свой)
FONT_PATH = os.path.join(settings.MEDIA_ROOT, "templates/oswald.ttf")

FONT_SIZE = 400  # Размер шрифта
QR_POSITION = (490, 1355)  # Координаты вставки QR-кода
QR_ACCOUNT_POSITIONS = (58, 52)
TEXT_POSITION = (2200, 4400)  # Координаты вставки supplier_id

QR_SIZE = 3000  # Размер QR-кода
QR_ACCOUNT_SIZE = 720

User = get_user_model()


def generate_password():
    # Генерация двух случайных букв
    letters = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))

    # Генерация шести случайных цифр
    digits = ''.join(random.choice(string.digits) for _ in range(6))

    # Соединение букв и цифр в пароль
    password = letters + digits
    return password


def create_qr_design(supplier_id):
    template = Image.open(TEMPLATE_PATH).convert("RGB")
    qr_url = f"https://optal.ru/box/{supplier_id}"
    qr_code = generate_qr_code(qr_url, QR_SIZE)
    template.paste(qr_code, QR_POSITION)
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw.text(TEXT_POSITION, f"{supplier_id}", fill="white", font=font)
    output = BytesIO()
    template.save(output, format="PNG", quality=100)
    output.seek(0)
    return output


def create_qr_design_account(box_data):
    template = Image.open(TEMPLATE_ACCOUNT_PATH).convert("RGB")
    qr_url = f"https://optal.ru/bl/{box_data['number']}/{box_data['imagoco']}"
    qr_code = generate_qr_code(qr_url, QR_ACCOUNT_SIZE)

    template.paste(qr_code, QR_ACCOUNT_POSITIONS)
    draw = ImageDraw.Draw(template)
    output = BytesIO()
    template.save(output, format="PNG", quality=100)
    output.seek(0)
    return output


def send_to_qr_accont(box_data, bot):

    # qr_url_2 = f"https://optal.ru/bl/{box_data['number']}/{box_data['imagoco']}"
    # qr_code_2 = generate_qr_code(qr_url_2)
    # qr_code_2.seek(0)

    image = create_qr_design_account(box_data)
    message = gen_message(box_data)

    bot.send_message(CHAT_ID, message, message_thread_id=TOPIC_QRACCOUNT)
    bot.send_photo(CHAT_ID, image, message_thread_id=TOPIC_QRACCOUNT,
                   caption="QR-код 2: Ссылка на вход")


def send_to_qr_catalog(box_data, bot):
    image = create_qr_design(box_data["supplier_id"])
    message = gen_message(box_data)

    bot.send_message(CHAT_ID, message, message_thread_id=TOPIC_QRCATALOG)
    bot.send_photo(CHAT_ID, image, message_thread_id=TOPIC_QRCATALOG,
                   caption=f"QR-код для {box_data['supplier_id']}")


def generate_qr_code(url, size):
    """Генерирует QR-код"""
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#CD0000",
                           back_color="white").convert("RGB")
    qr_img = qr_img.resize((size, size))  # Устанавливаем размер
    return qr_img

# def generate_qr_code_account(url, size=QR_SIZE):
#     """Генерирует QR-код"""
#     qr = qrcode.QRCode(box_size=10, border=2)
#     qr.add_data(url)
#     qr.make(fit=True)
#     qr_img = qr.make_image(fill_color="#CD0000",
#                            back_color="white").convert("RGB")
#     qr_img = qr_img.resize((size, size))  # Устанавливаем размер
#     return qr_img


def gen_message(box_data):
    ms = (
        f"Новый бокс\n"
        f"ID: {box_data['supplier_id']}\n"
        f"Номер: {box_data['number']}\n"
        f"Имя: {box_data['first_name']}\n"
        f"Бокс: {box_data['box_name']}\n"
        f"Пароль: {box_data['password']}"
    )
    return ms


class RegisterBoxView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("ПРИНЯЛ ЗАПРОСА")
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        factory_name = request.data.get('factory_name')
        password = generate_password()
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
        print('CAME HERE')
        FactoryProfile.objects.create(
            user=user, factory_name=factory_name,  supplier_id=supplier_id, imagoco=password)
        token = Token.objects.create(user=user)
        box_data = {
            "supplier_id": supplier_id,
            "number": username,
            "first_name": first_name,
            "box_name": factory_name,
            "password": password,
            "imagoco": password
        }
        self.send_telegram_new_box_created(box_data)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)

    def send_telegram_new_box_created(self, box_data):
        print("TELEGRAM STARTER")
        bot_token = "7752839364:AAE0nw55hvfrl5G4UZKB5zNeLd_2-bebfRA"
        bot = telebot.TeleBot(bot_token)
        try:
            send_to_qr_catalog(box_data, bot)
            send_to_qr_accont(box_data, bot)
            print(f"Сообщение и QR-коды успешно отправлены в чат!")

        except Exception as e:
            print(f"Ошибка отправки в чат: {e}")

    def generate_unique_supplier_id(self):
        while True:
            supplier_id = ''.join(random.choices('0123456789', k=6))
            if not FactoryProfile.objects.filter(supplier_id=supplier_id).exists():
                return supplier_id
