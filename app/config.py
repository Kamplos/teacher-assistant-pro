"""
Конфигурация приложения.
Содержит константы и настройки.
"""

# Доступные модели ИИ
AVAILABLE_MODELS = [
    "qwen-3-235b-a22b-instruct-2507",
    "llama3.1-8b",
    "gpt-oss-120b"
]

# Настройки страницы Streamlit
PAGE_CONFIG = {
    "page_title": "Teacher Assistant Pro",
    "page_icon": "🎓",
    "layout": "wide"
}

# Уровни школы
SCHOOL_LEVELS = [
    "Начальная школа (1-4 класс)",
    "Средняя школа (5-9 класс)",
    "Старшая школа (10-11 класс)"
]

# Опции материалов
MATERIAL_OPTIONS = ["Карта", "Краткая теория", "Тесты", "Презентация"]
DEFAULT_MATERIALS = ["Карта", "Тесты"]

# Настройки генерации
GENERATION_CONFIG = {
    "temperature": 0.6,
    "max_completion_tokens": 6000
}
