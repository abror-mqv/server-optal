import telebot
BOT_TOKEN = "7752839364:AAE0nw55hvfrl5G4UZKB5zNeLd_2-bebfRA"
bot = telebot.TeleBot(BOT_TOKEN)

updates = bot.get_updates()
for update in updates:
    print(update.message.chat.id)

print("AAAAAAAAAAA")

bot.send_message(7471817775, "Hello, world!")
bot.send_message(1901696570, "Адымар, салам алейкум")
