import sqlite3
from datetime import datetime

DB_NAME = 'expenses.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(user_id, amount, category, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, category, description, date))
    conn.commit()
    conn.close()

def get_monthly_expenses(user_id, year, month):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id, str(year), f"{month:02d}"))
    data = c.fetchall()
    conn.close()
    return data

def get_daily_expenses(user_id, year, month):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT date, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        GROUP BY date
        ORDER BY date
    ''', (user_id, str(year), f"{month:02d}"))
    data = c.fetchall()
    conn.close()
    return data
#Для графиков по месяцам 
def get_expenses_by_months(user_id, months_count=3):
    """Получить расходы за последние N месяцев по категориям"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Получаем последние months_count месяцев
    c.execute('''
        SELECT DISTINCT strftime('%Y-%m', date) as month
        FROM expenses
        WHERE user_id = ?
        ORDER BY month DESC
        LIMIT ?
    ''', (user_id, months_count))
    
    months = [row[0] for row in c.fetchall()]
    months.reverse()  # От старых к новым
    
    if not months:
        conn.close()
        return [], []
    
    # Получаем расходы по категориям для каждого месяца
    placeholders = ','.join(['?'] * len(months))
    c.execute(f'''
        SELECT strftime('%Y-%m', date) as month, category, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND strftime('%Y-%m', date) IN ({placeholders})
        GROUP BY month, category
        ORDER BY month, total DESC
    ''', [user_id] + months)
    
    data = c.fetchall()
    conn.close()
    
    # Структурируем данные
    categories = set()
    monthly_data = {month: {} for month in months}
    
    for month, category, total in data:
        monthly_data[month][category] = total
        categories.add(category)
    
    return months, monthly_data, list(categories)

def get_monthly_totals(user_id, months_count=6):
    """Получить общие суммы по месяцам для тренда"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month DESC
        LIMIT ?
    ''', (user_id, months_count))
    
    data = c.fetchall()
    data.reverse()  # От старых к новым
    conn.close()
    
    months = [row[0] for row in data]
    totals = [row[1] for row in data]
    
    return months, totals