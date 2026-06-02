import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from config import BOT_TOKEN
from database import (
    init_db, add_expense, get_monthly_expenses, 
    get_daily_expenses, get_expenses_by_months, get_monthly_totals  # новые импорты
)
from charts import (
    create_pie_chart, create_bar_chart, create_trend_chart,
    create_comparison_bar_chart, create_stack_bar_chart,  # новые
    create_monthly_trend_chart, create_heatmap_data
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния для ConversationHandler
AMOUNT, CATEGORY, DESCRIPTION = range(3)

# Категории расходов
CATEGORIES = ['🍔 Еда', '🚗 Транспорт', '🏠 Жильё', '🎮 Развлечения', 
              '🛍️ Шопинг', '💊 Здоровье', '📚 Образование', '💳 Другое']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить расход", callback_data='add_expense')],
        [InlineKeyboardButton("📊 Статистика за месяц", callback_data='stats_month')],
        [InlineKeyboardButton("📈 График расходов", callback_data='charts_menu')],
        [InlineKeyboardButton("📊 Сравнение расходов по месяцам", callback_data='compare_months')], 
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💰 *Бот учёта расходов*\n\n"
        "Я помогу вам отслеживать ваши траты за месяц.\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки (обновлённый)"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_expense':
        context.user_data['awaiting_amount'] = True
        await query.edit_message_text(
            "💵 Введите сумму расхода (например: 500 или 1250.50):"
        )
        return AMOUNT
    
    elif query.data == 'stats_month':
        await show_monthly_stats(query, context)
    
    elif query.data == 'charts_menu':
        await show_charts_menu(query)
    
    elif query.data == 'compare_months':
        await show_compare_months_menu(query)  # Новый обработчик
    
    elif query.data == 'chart_pie':
        await send_pie_chart(query)
    
    elif query.data == 'chart_bar':
        await send_bar_chart(query)
    
    elif query.data == 'chart_trend':
        await send_trend_chart(query)
    
    elif query.data == 'help':
        await show_help(query)
    
    # Новые обработчики для сравнения месяцев
    elif query.data.startswith('compare_'):
        await handle_compare_charts(query, context)
    
    return ConversationHandler.END

async def show_charts_menu(query):
    """Показать меню выбора графиков"""
    keyboard = [
        [InlineKeyboardButton("🥧 Круговая (по категориям)", callback_data='chart_pie')],
        [InlineKeyboardButton("📊 Столбчатая (по дням)", callback_data='chart_bar')],
        [InlineKeyboardButton("📈 Линейный график (динамика)", callback_data='chart_trend')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 *Выберите тип графика:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_monthly_stats(query, context):
    """Показать текстовую статистику за месяц"""
    user_id = query.from_user.id
    now = datetime.now()
    
    expenses = get_monthly_expenses(user_id, now.year, now.month)
    
    if not expenses:
        await query.edit_message_text(
            "📭 За этот месяц расходов пока нет.\n"
            "Добавьте первый расход с помощью кнопки '➕ Добавить расход'"
        )
        return
    
    total = sum(expense[1] for expense in expenses)
    stats_text = f"📊 *Статистика за {now.strftime('%B %Y')}*\n"
    stats_text += f"💰 *Общая сумма:* {total:.2f} руб.\n\n"
    stats_text += "*По категориям:*\n"
    
    for category, amount in expenses:
        percentage = (amount / total) * 100
        stats_text += f"• {category}: {amount:.2f} руб. ({percentage:.1f}%)\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        stats_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def send_pie_chart(query):
    """Отправить круговую диаграмму"""
    user_id = query.from_user.id
    now = datetime.now()
    
    expenses = get_monthly_expenses(user_id, now.year, now.month)
    
    if not expenses:
        await query.edit_message_text("Нет данных для построения графика")
        return
    
    chart_buf = create_pie_chart(expenses)
    
    if chart_buf:
        await query.edit_message_text("📊 Ваш график расходов по категориям:")
        await query.message.reply_photo(photo=chart_buf)
        chart_buf.close()
    
    # Возвращаем в главное меню
    await show_main_menu(query.message)

async def send_bar_chart(query):
    """Отправить столбчатую диаграмму"""
    user_id = query.from_user.id
    now = datetime.now()
    
    daily_expenses = get_daily_expenses(user_id, now.year, now.month)
    
    if not daily_expenses:
        await query.edit_message_text("Нет данных для построения графика")
        return
    
    chart_buf = create_bar_chart(daily_expenses)
    
    if chart_buf:
        await query.edit_message_text("📊 Ежедневные расходы за месяц:")
        await query.message.reply_photo(photo=chart_buf)
        chart_buf.close()
    
    await show_main_menu(query.message)

async def send_trend_chart(query):
    """Отправить график динамики"""
    user_id = query.from_user.id
    now = datetime.now()
    
    daily_expenses = get_daily_expenses(user_id, now.year, now.month)
    
    if not daily_expenses:
        await query.edit_message_text("Нет данных для построения графика")
        return
    
    chart_buf = create_trend_chart(daily_expenses)
    
    if chart_buf:
        await query.edit_message_text("📈 Динамика расходов за месяц:")
        await query.message.reply_photo(photo=chart_buf)
        chart_buf.close()
    
    await show_main_menu(query.message)

async def show_help(query):
    """Показать справку"""
    help_text = (
        "ℹ️ *Как пользоваться ботом:*\n\n"
        "1. Нажмите '➕ Добавить расход'\n"
        "2. Введите сумму (только число)\n"
        "3. Выберите категорию\n"
        "4. При желании добавьте описание\n\n"
        "📊 Для просмотра статистики используйте соответствующие кнопки.\n\n"
        "💡 *Совет:* Добавляйте расходы сразу после покупки, чтобы не забыть!"
    )
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
async def show_compare_months_menu(query):
    """Показать меню выбора графиков для сравнения месяцев"""
    keyboard = [
        [InlineKeyboardButton("📊 Сравнение по категориям (группы)", callback_data='compare_grouped')],
        [InlineKeyboardButton("📈 Сравнение по категориям (стек)", callback_data='compare_stacked')],
        [InlineKeyboardButton("📉 Тренд общих расходов", callback_data='compare_trend')],
        [InlineKeyboardButton("🔥 Тепловая карта", callback_data='compare_heatmap')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 *Сравнение расходов за несколько месяцев*\n\n"
        "Выберите тип графика:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_compare_charts(query, context):
    """Обработка запросов на графики сравнения"""
    user_id = query.from_user.id
    chart_type = query.data.replace('compare_', '')
    
    # Получаем данные за последние 3-6 месяцев
    months, monthly_data, categories = get_expenses_by_months(user_id, months_count=4)
    
    if not months or len(months) < 2:
        await query.edit_message_text(
            "❌ Недостаточно данных для сравнения.\n"
            "Нужны расходы минимум за 2 разных месяца.\n\n"
            "Добавьте расходы за разные месяцы и попробуйте снова."
        )
        return
    
    # Генерируем соответствующий график
    chart_buf = None
    
    if chart_type == 'grouped':
        chart_buf = create_comparison_bar_chart(months, monthly_data, categories)
        title = "📊 Сравнение расходов по категориям"
    elif chart_type == 'stacked':
        chart_buf = create_stack_bar_chart(months, monthly_data, categories)
        title = "📈 Сравнение расходов (с накоплением)"
    elif chart_type == 'trend':
        # Получаем данные для тренда за 6 месяцев
        trend_months, totals = get_monthly_totals(user_id, months_count=6)
        if len(trend_months) < 2:
            await query.edit_message_text(
                "❌ Недостаточно данных для отображения тренда.\n"
                "Нужны расходы минимум за 2 месяца."
            )
            return
        chart_buf = create_monthly_trend_chart(trend_months, totals)
        title = "📉 Тренд общих расходов"
    elif chart_type == 'heatmap':
        chart_buf = create_heatmap_data(months, monthly_data, categories)
        title = "🔥 Тепловая карта расходов"
    
    if chart_buf:
        await query.edit_message_text(title)
        await query.message.reply_photo(photo=chart_buf)
        chart_buf.close()
    else:
        await query.edit_message_text("❌ Ошибка при создании графика")
    
    # Возвращаем в меню сравнения
    await show_compare_months_menu(query)

async def show_main_menu(message):
    """Показать главное меню (обновлённое)"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить расход", callback_data='add_expense')],
        [InlineKeyboardButton("📊 Статистика за месяц", callback_data='stats_month')],
        [InlineKeyboardButton("📈 График расходов", callback_data='charts_menu')],
        [InlineKeyboardButton("📊 Сравнение месяцев", callback_data='compare_months')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "💰 *Главное меню*\n\nВыберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
async def show_main_menu(message):
    """Показать главное меню"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить расход", callback_data='add_expense')],
        [InlineKeyboardButton("📊 Статистика за месяц", callback_data='stats_month')],
        [InlineKeyboardButton("📈 График расходов", callback_data='charts_menu')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "💰 *Главное меню*\n\nВыберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def add_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение суммы расхода"""
    try:
        amount = float(update.message.text.replace(',', '.'))
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной. Попробуйте ещё раз:")
            return AMOUNT
        
        context.user_data['amount'] = amount
        
        # Показываем клавиатуру с категориями
        keyboard = [[InlineKeyboardButton(cat, callback_data=f'cat_{cat}')] for cat in CATEGORIES]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ Сумма: {amount:.2f} руб.\n\nТеперь выберите категорию:",
            reply_markup=reply_markup
        )
        return CATEGORY
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число (например: 500 или 1250.50):")
        return AMOUNT

async def add_expense_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение категории расхода"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace('cat_', '')
    context.user_data['category'] = category
    
    await query.edit_message_text(
        f"✅ Категория: {category}\n\n"
        "Добавьте описание (или отправьте '-' чтобы пропустить):"
    )
    return DESCRIPTION

async def add_expense_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания и сохранение расхода"""
    description = update.message.text
    if description == '-':
        description = ''
    
    user_id = update.message.from_user.id
    amount = context.user_data['amount']
    category = context.user_data['category']
    
    add_expense(user_id, amount, category, description)
    
    await update.message.reply_text(
        f"✅ *Расход сохранён!*\n\n"
        f"💵 Сумма: {amount:.2f} руб.\n"
        f"📂 Категория: {category}\n"
        f"📝 Описание: {description or '—'}\n\n"
        f"Используйте /start для возврата в меню.",
        parse_mode='Markdown'
    )
    
    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена добавления расхода"""
    await update.message.reply_text(
        "❌ Добавление расхода отменено.\n"
        "Используйте /start для возврата в меню."
    )
    context.user_data.clear()
    return ConversationHandler.END

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    await show_main_menu(query.message)
    return ConversationHandler.END

def main():
    """Запуск бота"""
    init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler для добавления расходов
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^add_expense$')],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_amount)],
            CATEGORY: [CallbackQueryHandler(add_expense_category, pattern='^cat_')],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_description)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^(stats_month|charts_menu|help|compare_months)$'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^chart_'))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^compare_'))  # Новый обработчик
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()