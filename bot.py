# -*- coding: utf-8 -*-
import os
import telebot
import requests
import time
from datetime import datetime

print("=== Бот запущен ===")

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# ПРИНУДИТЕЛЬНОЕ ЗАКРЫТИЕ СЕССИЙ
try:
    if BOT_TOKEN:
        print("🔄 Закрываем предыдущие сессии бота...")
        requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/close')
        time.sleep(2)
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook')
        time.sleep(1)
        print("✅ Все сессии закрыты")
except Exception as e:
    print(f"⚠️ Ошибка при закрытии сессий: {e}")

print("⏳ Ждем 5 секунд перед запуском...")
time.sleep(5)

# Простое хранилище
user_ids = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📝 Ввести ID сотрудника"))
    
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для графика смен.\n"
        "Нажми '📝 Ввести ID сотрудника'",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    if text == "📝 Ввести ID сотрудника":
        bot.send_message(message.chat.id, "Временно в режиме теста.")
        return
    
    bot.send_message(message.chat.id, "Бот работает! ✅")

if __name__ == '__main__':
    print("🚀 Запускаем бота...")
    bot.infinity_polling()
