import matplotlib.pyplot as plt
import io
from datetime import datetime

# Настройка русских шрифтов (для Windows/Mac/Linux)
plt.rcParams['font.family'] = 'DejaVu Sans'
# Если нужен русский, установите: 'Arial' или 'Microsoft YaHei'

def create_pie_chart(expenses_data):
    """Круговая диаграмма расходов по категориям"""
    if not expenses_data:
        return None
    
    categories = [item[0] for item in expenses_data]
    amounts = [item[1] for item in expenses_data]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        amounts, 
        labels=categories, 
        autopct='%1.1f%%',
        startangle=90
    )
    ax.set_title('Расходы по категориям за месяц', fontsize=14)
    
    # Сохраняем в байтовый буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def create_bar_chart(daily_expenses):
    """Столбчатая диаграмма ежедневных расходов"""
    if not daily_expenses:
        return None
    
    days = [item[0].split('-')[2] for item in daily_expenses]  # Дни месяца
    amounts = [item[1] for item in daily_expenses]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(days, amounts, color='skyblue', edgecolor='black')
    ax.set_xlabel('День месяца', fontsize=12)
    ax.set_ylabel('Сумма (руб)', fontsize=12)
    ax.set_title('Ежедневные расходы за месяц', fontsize=14)
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def create_trend_chart(daily_expenses):
    """Линейный график динамики расходов"""
    if not daily_expenses:
        return None
    
    days = list(range(1, len(daily_expenses) + 1))
    amounts = [item[1] for item in daily_expenses]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, amounts, marker='o', linestyle='-', linewidth=2, markersize=6)
    ax.set_xlabel('День месяца', fontsize=12)
    ax.set_ylabel('Сумма (руб)', fontsize=12)
    ax.set_title('Динамика расходов за месяц', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf
def create_comparison_bar_chart(months, monthly_data, categories):
    """
    Сгруппированная столбчатая диаграмма сравнения месяцев по категориям
    """
    if not months or not categories:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(months))
    width = 0.8 / len(categories)  # Ширина столбцов
    
    # Строим столбцы для каждой категории
    colors = plt.cm.tab20(range(len(categories)))
    
    for i, category in enumerate(categories):
        values = [monthly_data[month].get(category, 0) for month in months]
        offset = (i - len(categories)/2) * width + width/2
        ax.bar([xi + offset for xi in x], values, width, 
               label=category, color=colors[i])
    
    ax.set_xlabel('Месяц', fontsize=12)
    ax.set_ylabel('Сумма (руб)', fontsize=12)
    ax.set_title('Сравнение расходов по категориям за несколько месяцев', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf

def create_stack_bar_chart(months, monthly_data, categories):
    """
    Столбчатая диаграмма (stacked bar chart)
    """
    if not months or not categories:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Подготавливаем данные
    bottoms = [0] * len(months)
    colors = plt.cm.Set3(range(len(categories)))
    
    for i, category in enumerate(categories):
        values = [monthly_data[month].get(category, 0) for month in months]
        ax.bar(months, values, bottom=bottoms, label=category, color=colors[i])
        bottoms = [bottoms[j] + values[j] for j in range(len(months))]
    
    ax.set_xlabel('Месяц', fontsize=12)
    ax.set_ylabel('Сумма (руб)', fontsize=12)
    ax.set_title('Динамика расходов по категориям ', fontsize=14)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf

def create_monthly_trend_chart(months, totals):
    """
    Линейный график тренда общих расходов по месяцам
    """
    if not months or not totals:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(months, totals, marker='o', linewidth=2, markersize=8, 
            color='#FF6B6B', markerfacecolor='white', markeredgewidth=2)
    
    # Добавляем значения на график
    for i, (month, total) in enumerate(zip(months, totals)):
        ax.annotate(f'{total:.0f}₽', (month, total), 
                   textcoords="offset points", xytext=(0, 10), 
                   ha='center', fontsize=9)
    
    ax.set_xlabel('Месяц', fontsize=12)
    ax.set_ylabel('Общая сумма расходов (руб)', fontsize=12)
    ax.set_title('Тренд общих расходов за последние месяцы', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf

def create_heatmap_data(months, monthly_data, categories):
    """
    Тепловая карта расходов (матрица месяц-категория)
    """
    if not months or not categories:
        return None
    
    import numpy as np
    
    # Создаем матрицу данных
    data = []
    for month in months:
        row = [monthly_data[month].get(category, 0) for category in categories]
        data.append(row)
    
    data = np.array(data)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Рисуем тепловую карту
    im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
    
    # Настройка осей
    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(len(months)))
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_yticklabels(months)
    
    # Добавляем значения в ячейки
    for i in range(len(months)):
        for j in range(len(categories)):
            text = ax.text(j, i, f'{data[i, j]:.0f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('Тепловая карта расходов (месяц × категория)', fontsize=14)
    
    # Добавляем цветовую шкалу
    plt.colorbar(im, ax=ax, label='Сумма расходов (руб)')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf