# -*- coding: utf-8 -*-
import gspread
import telebot
from datetime import datetime, timedelta
import re

print("=== Бот запущен ===")

# Конфигурация
SPREADSHEET_ID = '1qgpURcdEGOfeG9JQRPm-hWBBCY2GkSxR5u0gnolFd1E'
BOT_TOKEN = '8379596604:AAE50oyAXzRqvOBPRGAi8RYzPQp7tqZFYkU'

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

class ScheduleBot:
    def __init__(self):
        self.gc = gspread.service_account(filename=r'D:\unet_bot\credentials.json')
        self.sheet = self.gc.open_by_key(SPREADSHEET_ID)
        
    def get_current_month_sheet(self):
        current_month_ru = self._get_current_month_russian()
        print(f"Ищем лист: '{current_month_ru}'")
        
        try:
            # Получаем ВСЕ доступные листы
            all_worksheets = self.sheet.worksheets()
            print("Доступные листы:")
            for ws in all_worksheets:
                print(f"   - '{ws.title}'")
            
            # Пробуем найти лист
            worksheet = self.sheet.worksheet(current_month_ru)
            print(f"Найден лист: '{worksheet.title}'")
            return worksheet
            
        except Exception as e:
            print(f"Лист '{current_month_ru}' не найден: {e}")
            
            # Пробуем альтернативные варианты названий
            alternative_names = [
                current_month_ru,
                current_month_ru.replace("Noyabr", "Ноябрь"),
                current_month_ru.replace("Oktyabr", "Октябрь"),
                current_month_ru.replace("Sentyabr", "Сентябрь"),
                current_month_ru.replace("Avgust", "Август"),
                current_month_ru.replace("Iyul", "Июль"),
                current_month_ru.replace("Iyun", "Июнь"),
                current_month_ru.replace("May", "Май"),
                current_month_ru.replace("Aprel", "Апрель"),
                current_month_ru.replace("Mart", "Март"),
                current_month_ru.replace("Fevral", "Февраль"),
                current_month_ru.replace("Yanvar", "Январь"),
                current_month_ru.replace("Dekabr", "Декабрь")
            ]
            
            for name in alternative_names:
                try:
                    worksheet = self.sheet.worksheet(name)
                    print(f"Найден альтернативный лист: '{worksheet.title}'")
                    return worksheet
                except:
                    continue
            
            return None
    
    def _get_current_month_russian(self):
        months = {
            1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
            5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
            9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr"
        }
        now = datetime.now()
        return f"{months[now.month]} {now.year}"
    
    def find_employee_column(self, worksheet, employee_id):
        """Находит столбец сотрудника по ID"""
        try:
            header = worksheet.row_values(1)
            print(f"Ищем ID сотрудника {employee_id} в заголовках...")
            
            for col_idx, cell_value in enumerate(header, 1):
                print(f"   Столбец {col_idx}: '{cell_value}'")
                if str(employee_id) in str(cell_value):
                    print(f"Найден сотрудник {employee_id} в столбце {col_idx}")
                    return col_idx
            
            print(f"ID сотрудника {employee_id} не найден в заголовках")
            return None
            
        except Exception as e:
            print(f"Ошибка поиска сотрудника: {e}")
            return None
    
    def get_schedule_for_day(self, worksheet, emp_col, day):
        """Получает смену на конкретный день"""
        try:
            days_col = worksheet.col_values(1)
            print(f"Ищем день {day} в столбце А...")
            
            for row_idx, day_val in enumerate(days_col, 1):
                if str(day_val) == str(day):
                    cell_value = worksheet.cell(row_idx, emp_col).value
                    print(f"Найдена смена на день {day}: '{cell_value}'")
                    return cell_value if cell_value else "❌ Не назначено"
            
            print(f"День {day} не найден в расписании")
            return "❌ Не найдено"
            
        except Exception as e:
            print(f"Ошибка получения смены: {e}")
            return "❌ Ошибка"
    
    def get_schedule_for_week(self, worksheet, emp_col, start_date, end_date):
        """Получает расписание на неделю (только дни в текущем месяце)"""
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            schedule = {}
            current_date = start_date
            
            while current_date <= end_date:
                # Проверяем, что дата в текущем месяце
                if current_date.month == current_month and current_date.year == current_year:
                    day_schedule = self.get_schedule_for_day(worksheet, emp_col, current_date.day)
                    schedule[current_date] = day_schedule
                current_date += timedelta(days=1)
            
            return schedule
            
        except Exception as e:
            print(f"Ошибка получения расписания на неделю: {e}")
            return {}

# Простое хранилище пользователей
user_ids = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    print(f"Пользователь {user_id} начал диалог")
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📝 Ввести ID сотрудника"))
    
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для просмотра графика смен.\n"
        "Нажми '📝 Ввести ID сотрудника' чтобы начать.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    print(f"Получено сообщение от {user_id}: {text}")
    
    if text == "📝 Ввести ID сотрудника":
        bot.send_message(message.chat.id, "Введи свой ID сотрудника (только цифры, например: 213):")
        return
    
    if text.isdigit():
        user_ids[user_id] = text
        print(f"Сохранен ID {text} для пользователя {user_id}")
        bot.send_message(message.chat.id, f"✅ ID сотрудника {text} сохранен!")
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📅 Сегодня", "📅 Завтра")
        markup.row("📅 Текущая неделя", "📅 Следующая неделя")
        
        bot.send_message(message.chat.id, "Теперь выбери период:", reply_markup=markup)
        return
    
    if user_id not in user_ids:
        bot.send_message(message.chat.id, "❌ Сначала введи свой ID сотрудника")
        return
    
    employee_id = user_ids[user_id]
    print(f"Обрабатываем запрос для сотрудника {employee_id}: {text}")
    
    schedule_bot = ScheduleBot()
    worksheet = schedule_bot.get_current_month_sheet()
    
    if not worksheet:
        bot.send_message(message.chat.id, "❌ График на текущий месяц не найден. Проверь консоль для деталей.")
        return
    
    emp_col = schedule_bot.find_employee_column(worksheet, employee_id)
    if not emp_col:
        bot.send_message(message.chat.id, f"❌ Сотрудник с ID {employee_id} не найден в заголовках графика")
        return
    
    now = datetime.now()
    
    if text == "📅 Сегодня":
        schedule = schedule_bot.get_schedule_for_day(worksheet, emp_col, now.day)
        bot.send_message(message.chat.id, f"📅 Твоя смена на сегодня ({now.day}.{now.month}):\n{schedule}")
    
    elif text == "📅 Завтра":
        tomorrow = now + timedelta(days=1)
        if tomorrow.month != now.month:
            bot.send_message(message.chat.id, "❌ Данные на следующий месяц пока недоступны")
        else:
            schedule = schedule_bot.get_schedule_for_day(worksheet, emp_col, tomorrow.day)
            bot.send_message(message.chat.id, f"📅 Твоя смена на завтра ({tomorrow.day}.{now.month}):\n{schedule}")
    
    elif text == "📅 Текущая неделя":
        # Вычисляем текущую неделю (понедельник до воскресенья)
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        schedule = schedule_bot.get_schedule_for_week(worksheet, emp_col, start_of_week, end_of_week)
        
        if not schedule:
            bot.send_message(message.chat.id, "❌ На этой неделе нет дней в текущем месяце")
        else:
            # Словарь для русских сокращений дней недели
            weekdays_ru = {
                0: "ПН", 1: "ВТ", 2: "СР", 3: "ЧТ", 
                4: "ПТ", 5: "СБ", 6: "ВС"
            }
            
            response = "📅 Твое расписание на текущую неделю:\n\n"
            for date, shift in sorted(schedule.items()):
                weekday_ru = weekdays_ru[date.weekday()]
                response += f"{weekday_ru} {date.strftime('%d.%m')}: {shift}\n"
            bot.send_message(message.chat.id, response)
    
    elif text == "📅 Следующая неделя":
        # Вычисляем следующую неделю (понедельник до воскресенья)
        start_of_week = now - timedelta(days=now.weekday()) + timedelta(days=7)
        end_of_week = start_of_week + timedelta(days=6)
        
        schedule = schedule_bot.get_schedule_for_week(worksheet, emp_col, start_of_week, end_of_week)
        
        if not schedule:
            bot.send_message(message.chat.id, "❌ На следующей неделе нет дней в текущем месяце")
        else:
            # Словарь для русских сокращений дней недели
            weekdays_ru = {
                0: "ПН", 1: "ВТ", 2: "СР", 3: "ЧТ", 
                4: "ПТ", 5: "СБ", 6: "ВС"
            }
            
            response = "📅 Твое расписание на следующую неделю:\n\n"
            for date, shift in sorted(schedule.items()):
                weekday_ru = weekdays_ru[date.weekday()]
                response += f"{weekday_ru} {date.strftime('%d.%m')}: {shift}\n"
            bot.send_message(message.chat.id, response)
    
    else:
        bot.send_message(message.chat.id, "❌ Неизвестная команда")

if __name__ == '__main__':
    print("Бот запущен и ожидает сообщения...")
    bot.infinity_polling()