import telebot
from telebot import types
from datetime import datetime
import sqlite3
import logging
import os


# Устанавливаем уровень логирования
logging.basicConfig(level=logging.DEBUG)

# Включаем логгирование для модуля telebot
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Токен твоего бота
TOKEN = '6938769291:AAHYrBMS9CyjPro-j9xKMkMGStaCJ-JPfsk'
bot = telebot.TeleBot(TOKEN)

# Define a dictionary to store the workday status for each user
workday_status = {}

# Глобальная переменная для product_id
product_id = None

def get_connection():
    return sqlite3.connect('employees.db')

# Flask-приложение для обработки вебхука от Телеграма
app = Flask(__name__)

# URL для вебхука, замени 'your_domain' на свой домен или IP-адрес
WEBHOOK_URL = '45.144.31.194' + TOKEN
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)


# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создаем новое соединение и курсор для каждого запроса
    with get_connection() as conn:
        cursor = conn.cursor()

        user_id = message.from_user.id

        # Проверяем, есть ли информация о сотруднике в базе данных
        cursor.execute("SELECT * FROM employees WHERE user_id = ?", (user_id,))
        existing_employee = cursor.fetchone()

        if existing_employee:
            # Если информация о сотруднике уже есть, просто приветствуем его
            bot.send_message(message.chat.id, f"Добро пожаловать, !")
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            start_work_button = types.KeyboardButton('Начать рабочий день')
            sell_button = types.KeyboardButton('Добавить продажу')
            end_work_button = types.KeyboardButton('Закончить рабочий день')

            markup.add(start_work_button, sell_button, end_work_button)

            bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
        else:
            # Если информации нет, предлагаем ввести ФИО
            bot.send_message(message.chat.id, "Добро пожаловать! Пожалуйста, введите свои ФИО в формате 'Фамилия Имя Отчество'.")

            # Регистрируем следующий шаг для обработки ввода ФИО
            bot.register_next_step_handler(message, process_fio_input)

def process_fio_input(message):
    # Создаем новое подключение к базе данных и курсор для каждого потока
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()

    user_id = message.from_user.id
    fio = message.text

    # Записываем информацию о сотруднике в базу данных
    cursor.execute("INSERT INTO employees (user_id, fio) VALUES (?, ?)", (user_id, fio))
    conn.commit()

    # После вставки ФИО, предлагаем меню с командами
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    start_work_button = types.KeyboardButton('Начать рабочий день')
    sell_button = types.KeyboardButton('Добавить продажу')
    end_work_button = types.KeyboardButton('Закончить рабочий день')

    markup.add(start_work_button, sell_button, end_work_button)

    bot.send_message(message.chat.id, "Спасибо, {}! Теперь вы зарегистрированы.".format(fio), reply_markup=markup)

    # Закрываем соединение с базой данных
    conn.close()


@bot.message_handler(func=lambda message: message.text == "Начать рабочий день")
def handle_start_work(message):
    user_id = message.from_user.id

    with get_connection() as conn:
        cursor = conn.cursor()

        # Проверяем, начал ли сотрудник уже рабочий день
        cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))
        existing_attendance = cursor.fetchone()

        if existing_attendance:
            bot.send_message(message.chat.id, "Ты уже начал рабочий день.")
        else:
            # Получаем список магазинов из базы данных
            cursor.execute("SELECT * FROM stores")
            stores = cursor.fetchall()

            # Создаем клавиатуру с названиями магазинов
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for store in stores:
                markup.add(types.KeyboardButton(store[1]))

            markup.add(types.KeyboardButton('Отмена'))

            bot.send_message(message.chat.id, "Выберите магазин, в котором вы сегодня работаете:", reply_markup=markup)
            bot.register_next_step_handler(message, process_store_selection, user_id=user_id)

def process_store_selection(message, user_id):
    store_name = message.text
    with get_connection() as conn:
        cursor = conn.cursor()

        # Находим ID магазина по имени
        cursor.execute("SELECT id FROM stores WHERE name = ?", (store_name,))
        result = cursor.fetchone()  # Сохраняем результат запроса в переменную result

        # Проверяем, получили ли мы результат
        if result:
            store_id = result[0]
            # Продолжайте с вашей текущей логикой...
        else:
            # Обработка случая, когда магазин не найден
            bot.send_message(message.chat.id, "Магазин не найден. Пожалуйста, выберите магазин из списка.")
            # Можете вернуть пользователя к выбору магазина или предпринять другие действия

        # Теперь запросим селфи
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        bot.send_message(message.chat.id, "Пожалуйста, сделайте селфи и отправьте его мне.", reply_markup=markup)
        bot.register_next_step_handler(message, process_selfie, conn=conn, cursor=cursor, user_id=user_id, store_id=store_id)

# Обработка селфи
def process_selfie(message, conn, cursor, user_id, store_id):
    markup = None  # Или какое-то значение по умолчанию

    # Проверка, прикреплено ли фото
    if message.photo or message.document:
        # Фото прикреплено
        if message.photo:
            # Получаем file_id из фото
            file_id = message.photo[-1].file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости
        elif message.document:
            # Получаем file_id из документа
            file_id = message.document.file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"documents/{file_id}"  # Измените путь по необходимости



        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        bot.send_message(message.chat.id, "Спасибо за селфи! Теперь сделай фото полок.", reply_markup=markup)
        # Registering the next step handler with the correct arguments
        bot.register_next_step_handler(message, process_shelf_photo, store_id=store_id)
    else:
        # Фото не прикреплено, уведомляем пользователя и обрабатываем соответственно
        bot.send_message(message.chat.id, "Вы не прикрепили фото. Рабочий день не начат.")

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        start_work_button = types.KeyboardButton('Начать рабочий день')
        sell_button = types.KeyboardButton('Добавить продажу')
        end_work_button = types.KeyboardButton('Закончить рабочий день')

        markup.add(start_work_button, sell_button, end_work_button)

        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)



# Обработка фото полок
def process_shelf_photo(message, store_id):
    markup = None  # Или какое-то значение по умолчанию

    # Проверка, прикреплено ли фото
    if message.photo or message.document:
        # Фото прикреплено
        if message.photo:
            # Получаем file_id из фото
            file_id = message.photo[-1].file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости
        elif message.document:
            # Получаем file_id из документа
            file_id = message.document.file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"documents/{file_id}"  # Измените путь по необходимости

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        bot.send_message(message.chat.id, "Спасибо за фото полок! Теперь сделай фото подиума.", reply_markup=markup)
        bot.register_next_step_handler(message, process_podium_photo, store_id=store_id)
    else:
        # Фото не прикреплено, уведомляем пользователя и обрабатываем соответственно
        bot.send_message(message.chat.id, "Вы не прикрепили фото. Процесс продолжается.")

# Обработка фото подиума
def process_podium_photo(message, store_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        user_id = message.from_user.id
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markup = None  # Или какое-то значение по умолчанию

    # Проверка, прикреплено ли фото
    if message.photo or message.document:
        # Фото прикреплено
        if message.photo:
            # Получаем file_id из фото
            file_id = message.photo[-1].file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости
        elif message.document:
            # Получаем file_id из документа
            file_id = message.document.file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"documents/{file_id}"  # Измените путь по необходимости

        cursor.execute("INSERT INTO attendance (user_id, check_in, store_id) VALUES (?, ?, ?)", (user_id, current_time, store_id))
        conn.commit()


        bot.send_message(message.chat.id, "Спасибо за фото подиума! Рабочий день начат.", reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        start_work_button = types.KeyboardButton('Начать рабочий день')
        sell_button = types.KeyboardButton('Добавить продажу')
        end_work_button = types.KeyboardButton('Закончить рабочий день')

        markup.add(start_work_button, sell_button, end_work_button)

        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
    else:
        # Фото не прикреплено, уведомляем пользователя и обрабатываем соответственно
        bot.send_message(message.chat.id, "Вы не прикрепили фото. Процесс продолжается.")

# Обработка команды /end_work
@bot.message_handler(func=lambda message: message.text == "Закончить рабочий день")
def handle_end_work(message):
    user_id = message.from_user.id
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Получаем соединение с базой данных
    with get_connection() as conn:
        try:
            # Получаем курсор
            cursor = conn.cursor()

            # Проверяем, завершил ли сотрудник уже рабочий день
            cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))
            existing_attendance = cursor.fetchone()

            if existing_attendance:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                start_work_button = types.KeyboardButton('Начать рабочий день')
                sell_button = types.KeyboardButton('Добавить продажу')
                end_work_button = types.KeyboardButton('Закончить рабочий день')

                markup.add(start_work_button, sell_button, end_work_button)

                bot.send_message(message.chat.id, "Чтобы закончить, пожалуйста, сделай фото селфи и отправь.", reply_markup=markup)
                bot.register_next_step_handler(message, process_selfie_end_photo)
            else:
                bot.send_message(message.chat.id, "Ты еще не начал рабочий день.")

                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                start_work_button = types.KeyboardButton('Начать рабочий день')
                sell_button = types.KeyboardButton('Добавить продажу')
                end_work_button = types.KeyboardButton('Закончить рабочий день')

                markup.add(start_work_button, sell_button, end_work_button)

                bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
        except Exception as e:
            # Логируем ошибку
            logging.error(f"Error in handle_end_work: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса. Попробуйте позже.")
        finally:
            # Закрываем курсор (нет необходимости закрывать соединение, так как использован менеджер контекста)
            cursor.close()

# Обработка селфи
def process_selfie_end_photo(message):

    # Проверка, прикреплено ли фото
    if message.photo or message.document:
        # Фото прикреплено
        if message.photo:
            # Получаем file_id из фото
            file_id = message.photo[-1].file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости
        elif message.document:
            # Получаем file_id из документа
            file_id = message.document.file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"documents/{file_id}"  # Измените путь по необходимости

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        bot.send_message(message.chat.id, "Спасибо за селфи! Теперь сделай фото полок.", reply_markup=markup)
        # Registering the next step handler with the correct arguments
        bot.register_next_step_handler(message, process_shelf_end_photo)
    else:
        # Фото не прикреплено, уведомляем пользователя и обрабатываем соответственно
        bot.send_message(message.chat.id, "Вы не прикрепили фото.")

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        start_work_button = types.KeyboardButton('Начать рабочий день')
        sell_button = types.KeyboardButton('Добавить продажу')
        end_work_button = types.KeyboardButton('Закончить рабочий день')

        markup.add(start_work_button, sell_button, end_work_button)

        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)

# Обработка фото полок
def process_shelf_end_photo(message):
    markup = None  # Или какое-то значение по умолчанию

    # Проверка, прикреплено ли фото
    if message.photo or message.document:
        # Фото прикреплено
        if message.photo:
            # Получаем file_id из фото
            file_id = message.photo[-1].file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости
        elif message.document:
            # Получаем file_id из документа
            file_id = message.document.file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"documents/{file_id}"  # Измените путь по необходимости

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        bot.send_message(message.chat.id, "Спасибо за фото полок! Теперь сделай фото подиума.", reply_markup=markup)
        bot.register_next_step_handler(message, process_podium_end_photo)
    else:
        # Фото не прикреплено, уведомляем пользователя и обрабатываем соответственно
        bot.send_message(message.chat.id, "Вы не прикрепили фото. Процесс продолжается.")

# Обработка фото подиума
def process_podium_end_photo(message):
    with get_connection() as conn:
        cursor = conn.cursor()
        user_id = message.from_user.id
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markup = None  # Или какое-то значение по умолчанию

    # Проверка, прикреплено ли фото
    if message.photo or message.document:
        # Фото прикреплено
        if message.photo:
            # Получаем file_id из фото
            file_id = message.photo[-1].file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости
        elif message.document:
            # Получаем file_id из документа
            file_id = message.document.file_id
            # Составляем путь к файлу, используя file_id
            metadata = f"documents/{file_id}"  # Измените путь по необходимости

        cursor.execute("UPDATE attendance SET check_out = ? WHERE user_id = ? AND check_out IS NULL", (current_time, user_id))
        conn.commit()
        bot.send_message(message.chat.id, "Класс фотки.")
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Спасибо за фото! Рабочий день закончен, всего доброго.", reply_markup=markup)
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        start_work_button = types.KeyboardButton('Начать рабочий день')
        sell_button = types.KeyboardButton('Добавить продажу')
        end_work_button = types.KeyboardButton('Закончить рабочий день')

        markup.add(start_work_button, sell_button, end_work_button)

        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
    else:
        # Фото не прикреплено, уведомляем пользователя и обрабатываем соответственно
        bot.send_message(message.chat.id, "Вы не прикрепили фото. Отмена.")


# Обработка фото полок и подиума
#def process_shelves_photo(message):
#    with get_connection() as conn:
#        cursor = conn.cursor()
#        user_id = message.from_user.id
#        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#    markup = None  # Или какое-то значение по умолчанию
#
#    # Проверка, прикреплено ли фото
#   if message.photo or message.document:
        # Фото прикреплено
#        if message.photo:
#           # Получаем file_id из фото
#            file_id = message.photo[-1].file_id
#            # Составляем путь к файлу, используя file_id
#            metadata = f"photos/{file_id}.jpg"  # Измените путь и расширение файла по необходимости

#            cursor.execute("UPDATE attendance SET check_out = ? WHERE user_id = ? AND check_out IS NULL", (current_time, user_id))
#            conn.commit()
#            bot.send_message(message.chat.id, "Спасибо за фото полок и подиума! Рабочий день завершен.")
#
             # Remove the custom keyboard
#          markup = types.ReplyKeyboardRemove(selective=False)
#         bot.send_message(message.chat.id, "Рабочий день завершен. Спасибо!", reply_markup=markup)
#
           # Отправляем главное меню после завершения рабочего дня
#            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#            start_work_button = types.KeyboardButton('Начать рабочий день')
#            sell_button = types.KeyboardButton('Добавить продажу')
#            end_work_button = types.KeyboardButton('Закончить рабочий день')
#
#            markup.add(start_work_button, sell_button, end_work_button)
#
#            bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
#       else:
#            bot.send_message(message.chat.id, "Рабочий день не завершен. Используйте кнопки меню.")
#
#            # Отправляем главное меню после завершения рабочего дня
#            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#            start_work_button = types.KeyboardButton('Начать рабочий день')
#            sell_button = types.KeyboardButton('Добавить продажу')
#            end_work_button = types.KeyboardButton('Закончить рабочий день')
#
#            markup.add(start_work_button, sell_button, end_work_button)
#
#            bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)

# Обработка команды /sell
@bot.message_handler(func=lambda message: message.text == "Добавить продажу")
def handle_sell(message):
    user_id = message.from_user.id

    # Подключаемся к базе данных с использованием менеджера контекста
    with get_connection() as conn:
        cursor = conn.cursor()

        # Проверяем, начал ли сотрудник рабочий день
        cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))
        existing_attendance = cursor.fetchone()

        if existing_attendance:
            # Получаем список товаров из базы данных
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for product in products:
                markup.add(types.KeyboardButton(product[1]))

            markup.add(types.KeyboardButton('Отмена'))

            bot.send_message(message.chat.id, "Выбери товар из списка:", reply_markup=markup)
            bot.register_next_step_handler(message, process_sale_input)
        else:
            bot.send_message(message.chat.id, "Чтобы зафиксировать продажу, начни рабочий день с команды /start_work")


def process_sale_input(message):
    global product_id  # Объявляем product_id как глобальную переменную

    # Получаем соединение с базой данных с использованием менеджера контекста
    with get_connection() as conn:
        cursor = conn.cursor()

        try:
            # Получаем ID товара
            product_name = message.text
            cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
            product_id = cursor.fetchone()

            if product_id:
                product_id = product_id[0]


                # Предложить фото с системы магазина
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                cancel_button = types.KeyboardButton('Отмена')

                markup.add(cancel_button)

                bot.send_message(message.chat.id, "Продажа товара '{}' зафиксирована. Пожалуйста, сделай фото с системы магазина.".format(product_name), reply_markup=markup)
                bot.register_next_step_handler(message, process_store_system_photo)
            else:
                bot.send_message(message.chat.id, "Ошибка при выборе товара. Попробуйте еще раз или используйте команду /sell.")
        except Exception as e:
            # Используем logging для логирования ошибок
            logging.error(f"Error in process_sale_input: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса. Попробуйте позже.")
        finally:
            # Закрываем курсор (нет необходимости закрывать соединение, так как использован менеджер контекста)
            cursor.close()


def process_store_system_photo(message):
    global product_id  # Объявляем product_id как глобальную переменную

    # Получаем соединение с базой данных с использованием менеджера контекста
    with get_connection() as conn:
        cursor = conn.cursor()
        user_id = message.from_user.id
    # Check if the message contains a photo or a document
    if message.photo or message.document:
        # The employee has attached a photo or a document
        if message.photo:
            # Extract file_id from the photo
            file_id = message.photo[-1].file_id
            # Construct the file path using the file_id
            metadata = f"photos/{file_id}.jpg"  # Change the path and file extension as needed
        elif message.document:
            # Extract file_id from the document
            file_id = message.document.file_id
            # Construct the file path using the file_id
            metadata = f"documents/{file_id}"  # Change the path as needed

        bot.send_message(message.chat.id, "Спасибо за фото с системы магазина!")
        # Зафиксировать продажу
        cursor.execute("INSERT INTO sales (user_id, product_id, sale_time) VALUES (?, ?, ?)",
        (message.from_user.id, product_id, datetime.now()))
        conn.commit()
        # Remove the custom keyboard
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Продажа зафиксирована. Спасибо!", reply_markup=markup)

        # Отправляем главное меню после завершения продажи
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        start_work_button = types.KeyboardButton('Начать рабочий день')
        sell_button = types.KeyboardButton('Добавить продажу')
        end_work_button = types.KeyboardButton('Закончить рабочий день')

        markup.add(start_work_button, sell_button, end_work_button)

        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
    else:
        # No photo attached, inform the user and handle accordingly
        bot.send_message(message.chat.id, "Вы не прикрепили фото. Продажа не завершена.")

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        start_work_button = types.KeyboardButton('Начать рабочий день')
        sell_button = types.KeyboardButton('Добавить продажу')
        end_work_button = types.KeyboardButton('Закончить рабочий день')

        markup.add(start_work_button, sell_button, end_work_button)

        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)

if __name__ == '__main__':
    app.run(debug=True)
