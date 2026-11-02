from telegram_bot.handlers.auth import handle_telegram_login


@bot.message_handler(commands=["start"])
def start(message):

    # Авторизация через сайт
    if handle_telegram_login(bot, message):
        return

    # Здесь оставь свою обычную логику /start
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в Mafia!"
    )