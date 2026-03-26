"""
Компоненты интерфейса Streamlit для отображения результатов.
"""

import streamlit as st


def render_result_page(result: str, topic: str) -> None:
    """
    Отображает страницу с результатами генерации.
    
    Args:
        result: Сгенерированный контент
        topic: Тема урока
    """
    st.button("← Назад", on_click=lambda: setattr(st.session_state, 'page', 'form'))
    st.title(f"📄 Материалы: {topic}")
    
    st.markdown(result)
    
    # Кнопка скачивания
    file_name = topic.replace(' ', '_')
    st.download_button(
        label="📥 Скачать (Markdown)",
        data=result,
        file_name=f"lesson_{file_name}.md",
        mime="text/markdown"
    )


def render_form_page(generator, selected_model: str) -> None:
    """
    Отображает главную форму создания урока.
    
    Args:
        generator: Экземпляр LessonGenerator
        selected_model: Выбранная модель ИИ
    """
    from app.components.form_components import (
        render_school_level_selector,
        render_basic_info_form,
        render_materials_composition,
        render_presentation_settings,
        render_test_settings,
        render_eval_tools
    )
    
    st.title("🎓 Конструктор урока по ФГОС")
    
    # Селектор уровня школы
    school_level = render_school_level_selector()
    
    # Форма базовой информации
    grade, subject, topic = render_basic_info_form(school_level)
    
    # Состав материалов
    detailed_theory, selected_items = render_materials_composition()
    
    # Инициализация переменных по умолчанию
    presentation_slides = 10
    presentation_text_volume = "средний"
    test_type = "Тест"
    test_configs = []
    
    # Настройки презентации
    if "Презентация" in selected_items:
        presentation_slides, presentation_text_volume = render_presentation_settings()
    
    # Настройки тестирования
    if "Тесты" in selected_items:
        test_type, test_configs = render_test_settings()
    
    # Дополнительные оценочные средства
    eval_tools = render_eval_tools()
    
    # Кнопка генерации
    if st.button("🚀 Сгенерировать материалы", type="primary", use_container_width=True):
        if not topic:
            st.error("Введите тему урока!")
        else:
            st.session_state.topic = topic
            
            # Формируем payload
            payload = {
                'grade': grade,
                'subject': subject,
                'topic': topic,
                'items': selected_items,
                'detailed_theory': detailed_theory,
                'test_type': test_type,
                'test_difficulty': "Обычный",
                'test_vars': 1,
                'q_count': 5,
                'a_count': 4,
                'eval_tools': eval_tools,
                'model': selected_model,
                'presentation_slides': presentation_slides,
                'presentation_text_volume': presentation_text_volume,
                'test_configs': test_configs if "Тесты" in selected_items else []
            }
            
            with st.spinner("Создаем глубокий контент... это может занять до 30 секунд"):
                st.session_state.result = generator.generate(payload)
                st.session_state.page = "result"
                st.rerun()
