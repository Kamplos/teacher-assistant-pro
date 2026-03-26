"""
Модуль генерации учебных материалов с использованием Cerebras API.
Содержит логику формирования промтов и запросов к ИИ.
"""

from typing import Dict, Any
from cerebras.cloud.sdk import Cerebras

from app.utils.prompts import get_subject_prompt


# Системный промт по умолчанию
SYSTEM_PROMPT_TEMPLATE = (
    "Ты — ведущий методист и заслуженный учитель РФ. Твоя задача — создавать материалы экспертного уровня. "
    "Используй профессиональную педагогическую лексику. "
    "МАТЕМАТИКА: Все формулы пиши ТОЛЬКО в формате $inline$ или $$display$$. "
    "Никогда не используй скобки [ ] или ( ) для LaTeX. Примеры: $a^2 + b^2 = c^2$.\n\n"
    "СПЕЦИФИКА ПРЕДМЕТА: {subject_prompt}"
)

# Структура техкарты по ФГОС
TECH_CARD_STRUCTURE = """
СТРОГО следуй блочно-модульной структуре ФГОС[cite: 1]:
БЛОК 1. Вхождение в тему: мотивация, актуализация знаний, целеполагание.
БЛОК 2. Освоение материала: учебные действия, проверка первичного усвоения[cite: 27, 33].
БЛОК 3. Применение: задания в новых ситуациях, связь с реальной жизнью, задания в формате ГИА (ОГЭ/ЕГЭ), развитие функциональной грамотности.
БЛОК 4. Проверка: диагностика и критерии оценивания.
БЛОК 5. Итоги: рефлексия и дифференцированное домашнее задание.
"""

# Описания объема текста для презентации
TEXT_VOLUME_DESCRIPTIONS = {
    "малый": "минимум текста, только ключевые тезисы и заголовки",
    "средний": "сбалансированное сочетание текста и визуальных элементов",
    "большой": "подробные пояснения на каждом слайде"
}


class LessonGenerator:
    """Генератор учебных материалов."""
    
    def __init__(self, api_key: str):
        """
        Инициализация генератора.
        
        Args:
            api_key: API ключ для Cerebras
        """
        self.client = Cerebras(api_key=api_key)
    
    def _build_requirements(self, data: Dict[str, Any]) -> list:
        """
        Формирует список требований к генерируемым материалам.
        
        Args:
            data: Данные формы
        
        Returns:
            Список строк с требованиями
        """
        reqs = []
        
        # Техкарта
        if "Карта" in data['items']:
            reqs.append(TECH_CARD_STRUCTURE)
        
        # Теория
        if data.get('detailed_theory'):
            reqs.append(
                "ПОДРОБНЫЙ ТЕОРЕТИЧЕСКИЙ МАТЕРИАЛ: Напиши лонгрид (минимум 1000 слов). "
                "Это должен быть глубокий экспертный текст с историческим контекстом, научными нюансами, "
                "разбором сложных случаев и интересными фактами. НЕ используй тезисы, пиши связным текстом."
            )
        elif "Краткая теория" in data['items']:
            reqs.append("- Краткий конспект теории (тезисно).")
        
        # Презентация
        if "Презентация" in data['items']:
            slides = data.get('presentation_slides', 10)
            text_volume = data.get('presentation_text_volume', 'средний')
            volume_desc = TEXT_VOLUME_DESCRIPTIONS.get(text_volume, TEXT_VOLUME_DESCRIPTIONS['средний'])
            
            reqs.append(
                f"ПЛАН ПРЕЗЕНТАЦИИ: Составь структуру на {slides} слайдов. "
                f"Объем текста: {volume_desc}. "
                "Контент должен отличаться от текста теории: фокусируйся на визуальных образах, "
                "схемах, инфографике и кратких выводах для экрана. Укажи описание визуала для каждого слайда."
            )
        
        # Тесты
        if "Тесты" in data['items']:
            test_configs = data.get('test_configs', [])
            
            if data.get('test_type') == "Тест":
                test_reqs = []
                for i, config in enumerate(test_configs):
                    test_reqs.append(
                        f"Тест #{i+1}: {config['questions']} вопросов, {config['variants']} вариант(а), "
                        f"{config['answers']} варианта ответа, сложность: {config['difficulty']}"
                    )
                reqs.append(f"- ТЕСТЫ:\n" + "\n".join(test_reqs) + " с ключами.")
            else:
                prac_reqs = []
                for i, config in enumerate(test_configs):
                    prac_reqs.append(
                        f"Практическое задание #{i+1}: {config['questions']} заданий на работу с контекстом, "
                        f"анализ и синтез, сложность: {config['difficulty']}"
                    )
                reqs.append(f"- ПРАКТИЧЕСКОЕ ТЕСТИРОВАНИЕ:\n" + "\n".join(prac_reqs))
        
        return reqs
    
    def _build_prompts(self, data: Dict[str, Any], requirements: list) -> tuple:
        """
        Строит системный и пользовательский промты.
        
        Args:
            data: Данные формы
            requirements: Список требований
        
        Returns:
            Кортеж (system_prompt, user_prompt)
        """
        # Получаем специфичный промт для предмета
        subject_prompt = get_subject_prompt(data['subject'], data['grade'])
        
        # Системный промт
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(subject_prompt=subject_prompt)
        
        # Пользовательский промт
        user_prompt = f"""Сформируй комплекс материалов для {data['grade']} класса.
Предмет: {data['subject']}. Тема: {data['topic']}.
Задачи:
{chr(10).join(requirements)}
Дополнительные средства: {data['eval_tools']}.
Сложность заданий: {data['test_difficulty']}."""
        
        return system_prompt, user_prompt
    
    def generate(self, data: Dict[str, Any]) -> str:
        """
        Генерирует учебные материалы.
        
        Args:
            data: Данные формы с настройками
        
        Returns:
            Сгенерированный контент или сообщение об ошибке
        """
        try:
            # Формируем требования
            requirements = self._build_requirements(data)
            
            # Строим промты
            system_prompt, user_prompt = self._build_prompts(data, requirements)
            
            # Запрос к API
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=data['model'],
                temperature=0.6,
                max_completion_tokens=6000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Ошибка API: {e}"
