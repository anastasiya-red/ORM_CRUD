import sqlite3

connection = sqlite3.connect('module_14_5.db')
cursor = connection.cursor()

def products_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
    )
    ''')
    connection.commit()

def user_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL
    )
    ''')
    connection.commit()

def get_all_products():
    cursor.execute('SELECT * FROM Products')
    data = cursor.fetchall()
    return data

def add_products():
    for i in range (1,5):
        cursor.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
                       (f'Продукт{i}', f'Описание{i}', f'{100*i}'))
    connection.commit()

def add_user(username, email, age):
    cursor.execute("INSERT INTO Users (username, email, age, balance) VALUES(?, ?, ?, ?)",
        (f'{username}', f'{email}', f'{age}', 1000))
    connection.commit()

def is_included(username):
    check_user = cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    if check_user.fetchone() is None:
        return False
    else: return True


if __name__ == '__main__':
  products_db()
  add_products()
  user_db()
  connection.close()