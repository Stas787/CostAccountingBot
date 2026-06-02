import pytest
import sqlite3
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

# Временная директория для тестов
@pytest.fixture
def temp_db():
    """Создаёт временную БД для тестов"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Патчим DB_NAME для тестов
    with patch('database.DB_NAME', db_path):
        yield db_path
    
    # Очистка после тестов
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def db_connection(temp_db):
    """Возвращает соединение с тестовой БД"""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    
    # Создаём таблицу
    from database import init_db
    init_db()
    
    yield conn
    conn.close()

@pytest.fixture
def sample_expenses(temp_db): 
    """Заполняет БД тестовыми расходами"""
    import sqlite3
    from database import init_db
    
    # Инициализируем БД
    init_db()
    
    user_id = 123456789
    base_date = datetime(2024, 1, 15)
    
    expenses_data = [
        (user_id, 1500.50, '🍔 Еда', 'Обед в кафе', base_date),
        (user_id, 3500.00, '🚗 Транспорт', 'Бензин', base_date - timedelta(days=30)),
        (user_id, 8500.00, '🏠 Жильё', 'Коммунальные', base_date - timedelta(days=30)),
        (user_id, 2500.00, '🍔 Еда', 'Продукты', base_date - timedelta(days=30)),
        (user_id, 4200.00, '🛍️ Шопинг', 'Одежда', base_date - timedelta(days=60)),
        (user_id, 1800.00, '🎮 Развлечения', 'Кино', base_date),
        (user_id, 950.00, '🍔 Еда', 'Кофе', base_date),
        (user_id, 2800.00, '💊 Здоровье', 'Аптека', base_date - timedelta(days=15)),
    ]
    
    # Подключаемся напрямую к БД
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    for user, amount, category, desc, date in expenses_data:
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user, amount, category, desc, date.strftime('%Y-%m-%d')))
    
    conn.commit()
    conn.close()
    
    return user_id

@pytest.fixture
def mock_update():
    """Создаёт мок объекта Update"""
    update = Mock()
    update.message = Mock()
    update.message.reply_text = AsyncMock()
    update.message.from_user = Mock()
    update.message.from_user.id = 123456789
    update.callback_query = Mock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.message = Mock()
    update.callback_query.message.reply_text = AsyncMock()  # Добавлено
    update.callback_query.from_user = Mock()
    update.callback_query.from_user.id = 123456789
    return update

@pytest.fixture
def mock_context():
    """Создаёт мок объекта Context"""
    context = Mock()
    context.user_data = {}
    context.bot = Mock()
    context.bot.send_photo = AsyncMock()
    return context