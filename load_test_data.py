import sqlite3
from datetime import datetime, timedelta
import random
from database import DB_NAME

# Категории расходов
CATEGORIES = ['🍔 Еда', '🚗 Транспорт', '🏠 Жильё', '🎮 Развлечения', 
              '🛍️ Шопинг', '💊 Здоровье', '📚 Образование', '💳 Другое']

# ID пользователя для тестовых данных (Telegram ID)
TEST_USER_ID = 1239386945  # Замените на свой Telegram ID

def generate_test_data():
    """Генерация тестовых расходов за последние 3 месяца"""
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Очищаем старые тестовые данные для этого пользователя (опционально)
    #c.execute("DELETE FROM expenses WHERE user_id = ?", (TEST_USER_ID,))
    
    # Текущая дата
    today = datetime.now()
    
    # Создаем расходы за последние 3 месяца
    expenses = []
    
    # Базовые расходы по категориям для каждого месяца
    monthly_patterns = [
        {  # 3 месяца назад
            '🍔 Еда': (8000, 12000),
            '🚗 Транспорт': (3000, 5000),
            '🏠 Жильё': (15000, 20000),
            '🎮 Развлечения': (2000, 4000),
            '🛍️ Шопинг': (3000, 6000),
            '💊 Здоровье': (1000, 2000),
            '📚 Образование': (500, 1500),
            '💳 Другое': (500, 1500)
        },
        {  # 2 месяца назад
            '🍔 Еда': (9000, 13000),
            '🚗 Транспорт': (2500, 4500),
            '🏠 Жильё': (15000, 20000),
            '🎮 Развлечения': (2500, 5000),
            '🛍️ Шопинг': (4000, 7000),
            '💊 Здоровье': (800, 1800),
            '📚 Образование': (1000, 2000),
            '💳 Другое': (300, 1000)
        },
        {  # Прошлый месяц
            '🍔 Еда': (8500, 12500),
            '🚗 Транспорт': (3500, 5500),
            '🏠 Жильё': (15500, 20500),
            '🎮 Развлечения': (3000, 6000),
            '🛍️ Шопинг': (3500, 6500),
            '💊 Здоровье': (1200, 2200),
            '📚 Образование': (750, 1750),
            '💳 Другое': (600, 1600)
        }
    ]
    
    # Генерируем расходы для каждого из последних 3 месяцев
    for month_offset in range(3, 0, -1):  # 3, 2, 1 месяц назад
        # Дата первого дня месяца
        month_date = today.replace(day=1) - timedelta(days=month_offset * 30)
        month_date = month_date.replace(day=1)
        
        # Количество дней в месяце
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1)
        days_in_month = (next_month - month_date).days
        
        # Получаем паттерн для этого месяца
        pattern = monthly_patterns[3 - month_offset]
        
        # Для каждой категории генерируем расходы
        for category, (min_total, max_total) in pattern.items():
            # Общая сумма расходов за месяц по категории
            total_month = random.randint(min_total, max_total)
            
            # Количество транзакций в месяц (от 3 до 10)
            num_transactions = random.randint(3, 10)
            
            # Генерируем отдельные транзакции
            remaining = total_month
            for i in range(num_transactions):
                if i == num_transactions - 1:
                    amount = remaining
                else:
                    # Сумма одной транзакции (от 5% до 30% от общей)
                    max_amount = int(total_month * 0.3)
                    min_amount = int(total_month * 0.05)
                    amount = random.randint(min_amount, max_amount)
                    remaining -= amount
                
                # Случайный день месяца (первые 25 дней, чтобы избежать проблем с границами)
                day = random.randint(1, min(25, days_in_month))
                date = month_date.replace(day=day)
                date_str = date.strftime('%Y-%m-%d')
                
                # Случайное описание
                descriptions = [
                    f"Покупка в {category}", 
                    f"Оплата {category.lower()}",
                    f"Расход на {category.lower()}",
                    "",
                    f"Ежедневные траты",
                    f"Необходимая покупка"
                ]
                description = random.choice(descriptions)
                
                expenses.append((TEST_USER_ID, amount, category, description, date_str))
    
    # Добавляем несколько крупных покупок
    large_purchases = [
        (TEST_USER_ID, 15000, '🏠 Жильё', 'Аренда квартиры', (today - timedelta(days=30)).strftime('%Y-%m-%d')),
        (TEST_USER_ID, 8000, '🛍️ Шопинг', 'Новый телефон', (today - timedelta(days=45)).strftime('%Y-%m-%d')),
        (TEST_USER_ID, 5000, '🎮 Развлечения', 'Игровая консоль', (today - timedelta(days=20)).strftime('%Y-%m-%d')),
        (TEST_USER_ID, 3000, '📚 Образование', 'Курсы английского', (today - timedelta(days=10)).strftime('%Y-%m-%d')),
        (TEST_USER_ID, 2000, '💊 Здоровье', 'Стоматолог', (today - timedelta(days=5)).strftime('%Y-%m-%d')),
        (TEST_USER_ID, 12000, '🚗 Транспорт', 'Ремонт авто', (today - timedelta(days=15)).strftime('%Y-%m-%d')),
        (TEST_USER_ID, 7000, '🍔 Еда', 'Ресторан', (today - timedelta(days=8)).strftime('%Y-%m-%d')),
    ]
    
    expenses.extend(large_purchases)
    
    # Добавляем несколько расходов за текущий месяц (для тестов)
    current_month = today.month
    for _ in range(15):
        category = random.choice(CATEGORIES)
        amount = random.randint(300, 5000)
        day = random.randint(1, today.day)
        date = today.replace(day=day)
        if date > today:
            date = today
        date_str = date.strftime('%Y-%m-%d')
        description = f"Текущие расходы на {category.lower()}"
        expenses.append((TEST_USER_ID, amount, category, description, date_str))
    
    # Вставляем все расходы в базу данных
    c.executemany('''
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    ''', expenses)
    
    conn.commit()
    
    # Выводим статистику
    c.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (TEST_USER_ID,))
    count = c.fetchone()[0]
    
    c.execute("SELECT MIN(date), MAX(date) FROM expenses WHERE user_id = ?", (TEST_USER_ID,))
    min_date, max_date = c.fetchone()
    
    c.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month
    ''', (TEST_USER_ID,))
    
    monthly_stats = c.fetchall()
    
    conn.close()
    
    print(f"✅ Загружено {count} тестовых расходов для пользователя {TEST_USER_ID}")
    print(f"📅 Период: с {min_date} по {max_date}")
    print("\n📊 Суммы по месяцам:")
    for month, total in monthly_stats:
        print(f"  {month}: {total:.2f} руб.")
    
    return count

def clear_test_data():
    """Очистить тестовые данные"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE user_id = ?", (TEST_USER_ID,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    print(f"🗑️ Удалено {deleted} тестовых записей")

if __name__ == "__main__":
    print("=" * 50)
    print("Загрузка тестовых данных для бота учёта расходов")
    print("=" * 50)
    print(f"\n⚠️  ВНИМАНИЕ: Используется TEST_USER_ID = {TEST_USER_ID}")
    print("Если хотите использовать свой Telegram ID, измените переменную TEST_USER_ID\n")
    
    choice = input("Выберите действие:\n1 - Загрузить тестовые данные\n2 - Очистить тестовые данные\n3 - Перезагрузить данные\nВаш выбор (1/2/3): ")
    
    if choice == '1':
        count = generate_test_data()
        print(f"\n🎉 Готово! Теперь запустите бота и используйте ID {TEST_USER_ID} для тестирования.")
        print("💡 Совет: Если бот запущен на вашем Telegram аккаунте, измените TEST_USER_ID на ваш реальный ID Telegram.")
    
    elif choice == '2':
        clear_test_data()
    
    elif choice == '3':
        clear_test_data()
        count = generate_test_data()
        print(f"\n🎉 Данные перезагружены! {count} записей добавлено.")
    
    else:
        print("❌ Неверный выбор")