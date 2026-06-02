import pytest
from PIL import Image
import io
from charts import (
    create_pie_chart, create_bar_chart, create_trend_chart,
    create_comparison_bar_chart, create_stack_bar_chart,
    create_monthly_trend_chart, create_heatmap_data
)

class TestCharts:
    """Тесты для модуля charts.py"""
    
    def test_create_pie_chart_success(self):
        """Проверка создания круговой диаграммы с данными"""
        expenses_data = [
            ('🍔 Еда', 15000),
            ('🚗 Транспорт', 8000),
            ('🏠 Жильё', 25000),
            ('🎮 Развлечения', 5000),
        ]
        
        result = create_pie_chart(expenses_data)
        
        assert result is not None
        assert isinstance(result, io.BytesIO)
        
        # Проверяем, что это валидное изображение
        result.seek(0)
        img = Image.open(result)
        assert img.format == 'PNG'
        assert img.size[0] > 0 and img.size[1] > 0
    
    def test_create_pie_chart_empty_data(self):
        """Проверка создания диаграммы с пустыми данными"""
        result = create_pie_chart([])
        assert result is None
    
    def test_create_pie_chart_single_category(self):
        """Проверка диаграммы с одной категорией"""
        expenses_data = [('🍔 Еда', 15000)]
        
        result = create_pie_chart(expenses_data)
        
        assert result is not None
        result.seek(0)
        img = Image.open(result)
        assert img.format == 'PNG'
    
    def test_create_bar_chart_success(self):
        """Проверка создания столбчатой диаграммы"""
        daily_expenses = [
            ('2024-01-01', 1500),
            ('2024-01-02', 2300),
            ('2024-01-03', 1800),
            ('2024-01-04', 3200),
        ]
        
        result = create_bar_chart(daily_expenses)
        
        assert result is not None
        assert isinstance(result, io.BytesIO)
        
        result.seek(0)
        img = Image.open(result)
        assert img.format == 'PNG'
    
    def test_create_bar_chart_empty(self):
        """Проверка столбчатой диаграммы с пустыми данными"""
        result = create_bar_chart([])
        assert result is None
    
    def test_create_trend_chart_success(self):
        """Проверка создания линейного графика"""
        daily_expenses = [
            ('2024-01-01', 1500),
            ('2024-01-02', 2300),
            ('2024-01-03', 1800),
        ]
        
        result = create_trend_chart(daily_expenses)
        
        assert result is not None
        assert isinstance(result, io.BytesIO)
    
    def test_create_comparison_bar_chart(self):
        """Проверка создания сравнительной диаграммы по месяцам"""
        months = ['2024-01', '2024-02', '2024-03']
        monthly_data = {
            '2024-01': {'🍔 Еда': 15000, '🚗 Транспорт': 8000},
            '2024-02': {'🍔 Еда': 17000, '🚗 Транспорт': 7500},
            '2024-03': {'🍔 Еда': 16000, '🚗 Транспорт': 9000},
        }
        categories = ['🍔 Еда', '🚗 Транспорт']
        
        result = create_comparison_bar_chart(months, monthly_data, categories)
        
        assert result is not None
        result.seek(0)
        img = Image.open(result)
        assert img.format == 'PNG'
    
    def test_create_stack_bar_chart(self):
        """Проверка создания stacked bar chart"""
        months = ['2024-01', '2024-02']
        monthly_data = {
            '2024-01': {'🍔 Еда': 15000, '🚗 Транспорт': 8000},
            '2024-02': {'🍔 Еда': 17000, '🚗 Транспорт': 7500},
        }
        categories = ['🍔 Еда', '🚗 Транспорт']
        
        result = create_stack_bar_chart(months, monthly_data, categories)
        
        assert result is not None
        assert isinstance(result, io.BytesIO)
    
    def test_create_monthly_trend_chart(self):
        """Проверка создания графика тренда"""
        months = ['2024-01', '2024-02', '2024-03']
        totals = [28000, 29500, 31000]
        
        result = create_monthly_trend_chart(months, totals)
        
        assert result is not None
        result.seek(0)
        img = Image.open(result)
        assert img.format == 'PNG'
    
    def test_create_monthly_trend_chart_empty(self):
        """Проверка графика тренда с пустыми данными"""
        result = create_monthly_trend_chart([], [])
        assert result is None
    
    def test_create_heatmap_data(self):
        """Проверка создания тепловой карты"""
        months = ['2024-01', '2024-02']
        monthly_data = {
            '2024-01': {'🍔 Еда': 15000, '🚗 Транспорт': 8000},
            '2024-02': {'🍔 Еда': 17000, '🚗 Транспорт': 7500},
        }
        categories = ['🍔 Еда', '🚗 Транспорт']
        
        result = create_heatmap_data(months, monthly_data, categories)
        
        assert result is not None
        result.seek(0)
        img = Image.open(result)
        assert img.format == 'PNG'
    
    def test_all_charts_return_bytesio(self):
        """Проверка что все графики возвращают BytesIO с корректными данными"""
        # Тестовые данные
        pie_data = [('🍔 Еда', 1000)]
        bar_data = [('2024-01-01', 1000)]
        months = ['2024-01']
        monthly_data = {'2024-01': {'🍔 Еда': 1000}}
        categories = ['🍔 Еда']
        
        charts = [
            ('pie', create_pie_chart(pie_data)),
            ('bar', create_bar_chart(bar_data)),
            ('trend', create_trend_chart(bar_data)),
            ('comparison', create_comparison_bar_chart(months, monthly_data, categories)),
            ('stack', create_stack_bar_chart(months, monthly_data, categories)),
            ('monthly_trend', create_monthly_trend_chart(months, [1000])),
            ('heatmap', create_heatmap_data(months, monthly_data, categories)),
        ]
        
        for name, chart in charts:
            if chart is not None:
                assert isinstance(chart, io.BytesIO), f"Chart {name} should return BytesIO"
                chart_data = chart.getvalue()
                assert len(chart_data) > 0, f"Chart {name} should have data"