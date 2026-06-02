import pytest
from unittest.mock import AsyncMock, patch
from telegram import InlineKeyboardMarkup
from bot import (
    start, button_handler, show_main_menu,
    AMOUNT, CATEGORY, DESCRIPTION
)

class TestBotHandlers:
    """Тесты для основной логики бота"""
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_context):
        """Проверка команды /start"""
        await start(mock_update, mock_context)
        
        # Проверяем, что было отправлено сообщение
        mock_update.message.reply_text.assert_called_once()
        
        # Проверяем наличие кнопок в ответе
        call_args = mock_update.message.reply_text.call_args
        assert call_args[1]['parse_mode'] == 'Markdown'
        assert 'reply_markup' in call_args[1]
        assert isinstance(call_args[1]['reply_markup'], InlineKeyboardMarkup)
    
    @pytest.mark.asyncio
    async def test_add_expense_button(self, mock_update, mock_context):
        """Проверка нажатия кнопки добавления расхода"""
        mock_update.callback_query.data = 'add_expense'
        mock_update.callback_query.message.text = "Test"
        
        result = await button_handler(mock_update, mock_context)
        
        # Проверяем, что запрашивается сумма
        mock_update.callback_query.edit_message_text.assert_called()
        assert result == AMOUNT
    
    @pytest.mark.asyncio
    async def test_stats_month_button_empty(self, mock_update, mock_context, temp_db):
        """Проверка статистики для пользователя без данных"""
        from database import init_db
        init_db()
        
        mock_update.callback_query.data = 'stats_month'
        mock_update.callback_query.from_user.id = 999999
        
        await button_handler(mock_update, mock_context)
        
        # Должно быть сообщение о отсутствии расходов
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "нет" in call_args[0][0].lower() or "Нет" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_help_button(self, mock_update, mock_context):
        """Проверка кнопки помощи"""
        mock_update.callback_query.data = 'help'
        
        await button_handler(mock_update, mock_context)
        
        mock_update.callback_query.edit_message_text.assert_called()
        call_args = mock_update.callback_query.edit_message_text.call_args
        text = call_args[0][0].lower()
        # Проверяем наличие слов "пользоваться", "ботом" или "добавляйте"
        assert any(word in text for word in ['пользоваться', 'ботом', 'добавляйте', 'совет'])
    
    @pytest.mark.asyncio
    async def test_charts_menu_button(self, mock_update, mock_context):
        """Проверка кнопки меню графиков"""
        mock_update.callback_query.data = 'charts_menu'
        
        await button_handler(mock_update, mock_context)
        
        mock_update.callback_query.edit_message_text.assert_called()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "выберите тип графика" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_compare_months_button(self, mock_update, mock_context):
        """Проверка кнопки сравнения месяцев"""
        mock_update.callback_query.data = 'compare_months'
        
        await button_handler(mock_update, mock_context)
        
        mock_update.callback_query.edit_message_text.assert_called()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "сравнение расходов" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_back_to_menu(self, mock_update, mock_context):
        """Проверка возврата в главное меню"""
        from bot import back_to_menu
        
        # Создаем правильный мок для message
        mock_message = AsyncMock()
        mock_message.reply_text = AsyncMock()
        mock_update.callback_query.message = mock_message
        mock_update.callback_query.data = 'back_to_menu'
        
        await back_to_menu(mock_update, mock_context)
        
        # Проверяем, что вызван reply_text
        mock_update.callback_query.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_show_main_menu(self, mock_update):
        """Проверка отображения главного меню"""
        mock_message = AsyncMock()
        mock_message.reply_text = AsyncMock()
        
        await show_main_menu(mock_message)
        
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "главное меню" in call_args[0][0].lower()
        assert 'reply_markup' in call_args[1]

class TestExpenseAdding:
    """Тесты для процесса добавления расходов"""
    
    @pytest.mark.asyncio
    async def test_add_expense_amount_valid(self, mock_update, mock_context):
        """Проверка ввода корректной суммы расхода"""
        from bot import add_expense_amount
        
        mock_update.message.text = "1500.50"
        mock_context.user_data = {}
        
        result = await add_expense_amount(mock_update, mock_context)
        
        assert mock_context.user_data['amount'] == 1500.50
        assert result == CATEGORY
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_add_expense_amount_invalid(self, mock_update, mock_context):
        """Проверка ввода некорректной суммы"""
        from bot import add_expense_amount
        
        mock_update.message.text = "не число"
        mock_context.user_data = {}
        
        result = await add_expense_amount(mock_update, mock_context)
        
        assert result == AMOUNT
        mock_update.message.reply_text.assert_called_with(
            "❌ Пожалуйста, введите число (например: 500 или 1250.50):"
        )
    
    @pytest.mark.asyncio
    async def test_add_expense_amount_negative(self, mock_update, mock_context):
        """Проверка ввода отрицательной суммы"""
        from bot import add_expense_amount
        
        mock_update.message.text = "-500"
        mock_context.user_data = {}
        
        result = await add_expense_amount(mock_update, mock_context)
        
        assert result == AMOUNT
        mock_update.message.reply_text.assert_called_with(
            "❌ Сумма должна быть положительной. Попробуйте ещё раз:"
        )
    
    @pytest.mark.asyncio
    async def test_add_expense_amount_zero(self, mock_update, mock_context):
        """Проверка ввода нулевой суммы"""
        from bot import add_expense_amount
        
        mock_update.message.text = "0"
        mock_context.user_data = {}
        
        result = await add_expense_amount(mock_update, mock_context)
        
        assert result == AMOUNT
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_cancel_command(self, mock_update, mock_context):
        """Проверка отмены добавления расхода"""
        from bot import cancel
        
        await cancel(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        assert "отменено" in call_args[0][0]

class TestDatabaseIntegration:
    """Интеграционные тесты с БД"""
    
    @pytest.mark.asyncio
    async def test_full_expense_flow(self, temp_db):
        """Полный цикл добавления и получения расхода"""
        from database import init_db, add_expense, get_monthly_expenses
        from datetime import datetime
        
        init_db()
        
        user_id = 123456
        add_expense(user_id, 1500.50, '🍔 Еда', 'Обед')
        
        now = datetime.now()
        expenses = get_monthly_expenses(user_id, now.year, now.month)
        
        assert len(expenses) > 0
        assert expenses[0][0] == '🍔 Еда'
        assert expenses[0][1] == 1500.50
    
    def test_multiple_expenses_aggregation(self, sample_expenses, temp_db):
        """Проверка агрегации нескольких расходов"""
        from database import get_monthly_expenses
        from datetime import datetime
        
        user_id = sample_expenses
        now = datetime.now()
        
        expenses = get_monthly_expenses(user_id, now.year, now.month)
        
        # Проверяем, что суммы сгруппированы по категориям
        categories = [exp[0] for exp in expenses]
        assert len(categories) == len(set(categories))  # Нет дубликатов категорий