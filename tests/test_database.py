import pytest
import sqlite3
from datetime import datetime
from database import (
    init_db, add_expense, get_monthly_expenses,
    get_daily_expenses, get_expenses_by_months,
    get_monthly_totals
)

class TestDatabase:
    """Тесты для модуля database.py"""
    
    def test_init_db_creates_table(self, temp_db):
        """Проверка создания таблицы при инициализации БД"""
        import sqlite3  # Добавлен импорт
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Проверяем существование таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        table = cursor.fetchone()
        
        assert table is not None
        assert table[0] == 'expenses'
        
        conn.close()
    
    def test_add_expense_success(self, temp_db):
        """Проверка успешного добавления расхода"""
        import sqlite3  # Добавлен импорт
        init_db()
        
        user_id = 12345
        amount = 1500.50
        category = '🍔 Еда'
        description = 'Обед'
        
        add_expense(user_id, amount, category, description)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[1] == user_id
        assert result[2] == amount
        assert result[3] == category
        assert result[4] == description
        assert result[5] is not None  # дата должна быть
    
    def test_add_expense_with_empty_description(self, temp_db):
        """Проверка добавления расхода без описания"""
        import sqlite3  
        init_db()
        
        add_expense(12345, 500.00, '🚗 Транспорт', '')
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM expenses")
        description = cursor.fetchone()[0]
        conn.close()
        
        assert description == ''
    
    def test_get_monthly_expenses(self, sample_expenses, temp_db):
        """Проверка получения расходов за месяц с группировкой"""
        user_id = sample_expenses
        now = datetime.now()
        
        expenses = get_monthly_expenses(user_id, now.year, now.month)
        
        # Должны быть расходы только за текущий месяц
        assert isinstance(expenses, list)
        # Проверяем структуру результата (категория, сумма)
        if expenses:
            assert len(expenses[0]) == 2
            assert isinstance(expenses[0][0], str)  # категория
            assert isinstance(expenses[0][1], float)  # сумма
    
    def test_get_monthly_expenses_empty(self, temp_db):
        """Проверка получения расходов для пользователя без данных"""
        init_db()
        
        expenses = get_monthly_expenses(999999, 2024, 1)
        
        assert expenses == []
    
    def test_get_daily_expenses(self, sample_expenses, temp_db):
        """Проверка получения ежедневных расходов"""
        user_id = sample_expenses
        now = datetime.now()
        
        expenses = get_daily_expenses(user_id, now.year, now.month)
        
        assert isinstance(expenses, list)
        if expenses:
            assert len(expenses[0]) == 2
            assert isinstance(expenses[0][0], str)  # дата
            assert isinstance(expenses[0][1], float)  # сумма
    
    def test_get_expenses_by_months(self, sample_expenses, temp_db):
        """Проверка получения расходов за несколько месяцев"""
        user_id = sample_expenses
        
        months, monthly_data, categories = get_expenses_by_months(user_id, months_count=3)
        
        assert isinstance(months, list)
        assert isinstance(monthly_data, dict)
        assert isinstance(categories, list)
        
        # Если есть данные
        if months:
            assert len(months) <= 3
            assert len(monthly_data) == len(months)
    
    def test_get_monthly_totals(self, sample_expenses, temp_db):
        """Проверка получения общих сумм по месяцам"""
        user_id = sample_expenses
        
        months, totals = get_monthly_totals(user_id, months_count=6)
        
        assert isinstance(months, list)
        assert isinstance(totals, list)
        assert len(months) == len(totals)
        
        # Суммы должны быть положительными
        for total in totals:
            assert total >= 0
    
    def test_multiple_users_isolation(self, temp_db):
        """Проверка изоляции данных разных пользователей"""
        init_db()
        
        add_expense(111, 1000, '🍔 Еда', '')
        add_expense(222, 2000, '🚗 Транспорт', '')
        add_expense(111, 500, '🎮 Развлечения', '')
        
        expenses_user1 = get_monthly_expenses(111, datetime.now().year, datetime.now().month)
        expenses_user2 = get_monthly_expenses(222, datetime.now().year, datetime.now().month)
        
        # Сумма расходов пользователя 1
        total_user1 = sum(exp[1] for exp in expenses_user1)
        # Сумма расходов пользователя 2
        total_user2 = sum(exp[1] for exp in expenses_user2)
        
        assert total_user1 == 1500
        assert total_user2 == 2000