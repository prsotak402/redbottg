import sqlite3

conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

# Таблица для хранения данных о сотрудниках
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    full_name TEXT,
    fio TEXT
);
''')

# Таблица для фиксации времени прихода и ухода
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    check_in TIMESTAMP,
    check_out TIMESTAMP
);
''')

# Таблица для товаров
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
''')

# Таблица для фиксации продаж
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    sale_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES employees(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
''')

conn.commit()
conn.close()
