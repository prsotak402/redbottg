import sqlite3

conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

# Список товаров
products_list = [
      "Массажное керсло Yamaguchi Xu",
    "Массажное кресло Yamaguchi Xi (иксай) (черное)",
    "Массажное кресло Yamaguchi Xi (иксай) (бежевое)",
    "Массажное кресло Yamaguchi X (икс)",
    "Массажное кресло Yamaguchi Xr (иксар)",
    "Массажное кресло Yamaguchi Eclipse (черное)",
    "Массажное кресло Yamaguchi Eclipse (бежевое)",
    "Массажное кресло Yamaguchi Mercury (черное)",
    "Массажное кресло Yamaguchi Mercury (бежевое)",
    "Массажное кресло Yamaguchi YA-6000 Axiom (бело-рыжее)",
    "Массажное кресло Yamaguchi YA-6000 Axiom (бело-бежевое)",
    "Массажное кресло Yamaguchi YA-6000 Axiom (бело-черное)",
    "Массажное кресло Yamaguchi YA-6000 Axiom (цвет шампанского)",
    "Массажное кресло Yamaguchi YA-6000 Axiom (черно-рыжее)",
    "Массажное кресло Yamaguchi YA-6000 Axiom (черно-черное)",
    "Массажное кресло Yamaguchi Ewok",
    "Массажное кресло Yamaguchi Pulsar",
    "Гребной тренажер для тела Yamaguchi Ya-Rower Sport",
    "Насадки для фена-стайлера Yamaguchi Hair Styler Heads",
    "Массажер для головы и тела Yamaguchi Magic Head",
    "Массажный ободок для головы и шеи Yamaguchi Headband",
    "Массажер для ног Yamaguchi Yume (черный)",
    "Массажер для ног Yamaguchi Capsula (бежевый)",
    "Кресло-качалка Yamaguchi Liberty (бежевый)",
    "Напольная груша Yamaguchi Kinetic",
    "Звуковая электрическая зубная щетка Yamaguchi Smile Expert TRAVEL (белая)",
    "Ирригатор для полости рта Yamaguchi Oral Care",
    "Фен-стайлер для волос Yamaguchi Hair Styler",
    "Светодиодная силиконовая маска для лица Yamaguchi LED Light Therapy Mask",
    "Массажер для рук, живота и тела Yamaguchi HeartLine",
    "Массажер для ног Yamaguchi Capsula (серый)",
    "Массажер для колена Yamaguchi Joint Care",
    "Массажер для шеи Yamaguchi EMS Neck Massager",
    "Перкуссионный массажер для тела Yamaguchi Massage Gun MAX PRO",
    "Прибор для вакуумной чистки и пилинга кожи лица Yamaguchi Face Remover",
    "Беговая дорожка Yamaguchi MAX",
    "Беговая дорожка Yamaguchi Runway PRO-X",
    "Воздухоочиститель Yamaguchi Oxygen (белый)",
    "Беговая дорожка YAMAGUCHI Runway-X",
    "Велотренажер Yamaguchi Crossway",
    "Кресло-качалка Yamaguchi Liberty (серый)",
    "Прибор для очищения кожи и массажа лица Yamaguchi Silicone Cleansing Brush",
    "Виброплатформа Yamaguchi Vibroplate",
    "Массажер для головы Yamaguchi Galaxy PRO",
    "Массажер для шеи Yamaguchi Axiom Neck (белый/терракотовый)",
    "Перкуссионный массажер для тела Yamaguchi Massage Gun PRO",
    "Перкуссионный массажер для тела Yamaguchi Therapy Massage Gun",
    "Миостимулятор для ягодиц Yamaguchi Hips Trainer MIO (черный)",
    "Прибор для подтяжки кожи лица и декольте Yamaguchi EMS Face Lifting",
    "Прибор по антивозрастному уходу за кожей лица Yamaguchi Anti-Age Skin Care",
    "Прибор для RF лифтинга и омоложения кожи лица 6 в 1 Yamaguchi RF Lifting",
    "Миостимулятор для пресса Yamaguchi ABS Trainer MIO (черный)",
    "Миостимулятор для шеи Yamaguchi NECK Trainer MIO (черный)",
    "Перкуссионный массажер для тела Yamaguchi Massage Gun Mini 2",
    "Массажер для головы Yamaguchi Galaxy PRO Chrome",
    "Массажер для глаз Yamaguchi Axiom Eye AF (белый/терракотовый)",
]

# Вставляем товары в таблицу
for product_name in products_list:
    cursor.execute("INSERT INTO products (name) VALUES (?)", (product_name,))

# Коммитим изменения и закрываем соединение
conn.commit()
conn.close()