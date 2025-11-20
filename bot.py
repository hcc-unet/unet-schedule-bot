import os
import json
import telebot
from datetime import datetime

print("=== Бот запущен ===")

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Простое хранилище
user_ids = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    print(f"Пользователь {user_id} начал диалог")
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📝 Ввести ID сотрудника"))
    
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для графика смен.\n"
        "Сейчас проверяем подключение...\n"
        "Нажми '📝 Ввести ID сотрудника'",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    print(f"Получено сообщение от {user_id}: {text}")
    
    if text == "📝 Ввести ID сотрудника":
        bot.send_message(message.chat.id, "Временно в режиме теста. Google Sheets отключен.")
        return
    
    if text.isdigit():
        user_ids[user_id] = text
        bot.send_message(message.chat.id, f"✅ ID {text} сохранен! (Google Sheets отключен)")
        return
        
    bot.send_message(message.chat.id, "Бот работает, но Google Sheets временно отключен")

if __name__ == '__main__':
    print("✅ Бот запускается без Google Sheets...")
    bot.infinity_polling()
