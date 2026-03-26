"""
Компоненты интерфейса Streamlit для формы создания урока.
Содержит переиспользуемые UI элементы.
"""

import streamlit as st

from app.data.subjects import get_subjects_for_level, get_grade_range, get_level_info


def render_school_level_selector() -> str:
    """
    Отображает селектор уровня школы.
    
    Returns:
        Выбранный уровень школы
    """
    st.subheader("Выберите уровень школы:")
    return st.segmented_control(
        "Уровень:",
        ["Начальная школа (1-4 класс)", "Средняя школа (5-9 класс)", "Старшая школа (10-11 класс)"]
    )


def render_basic_info_form(school_level: str) -> tuple:
    """
    Отображает форму базовой информации об уроке.
    
    Args:
        school_level: Выбранный уровень школы
    
    Returns:
        Кортеж (grade, subject, topic)
    """
    # Получаем данные для уровня
    grade_options = get_grade_range(school_level)
    subject_options = list(get_subjects_for_level(school_level).keys())
    level_info = get_level_info(school_level)
    
    # Показываем инфо об уровне
    st.info(level_info)
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 1, 2])
        grade = c1.selectbox("Класс", grade_options)
        subject = c2.selectbox("Предмет", subject_options)
        topic = c3.text_input("Тема урока", placeholder="Введите тему...")
        
        # Показываем описание предмета
        subject_desc = get_subjects_for_level(school_level).get(subject, "")
        if subject_desc:
            c3.caption(f"💡 {subject_desc}")
    
    return grade, subject, topic


def render_materials_composition() -> tuple:
    """
    Отображает выбор состава материалов.
    
    Returns:
        Кортеж (detailed_theory, selected_items)
    """
    st.subheader("📦 Состав материалов")
    
    detailed_theory = st.toggle("✨ Глубокая и объемная теория (Лекция)", value=True)
    selected_items = st.multiselect(
        "Дополнительно:",
        ["Карта", "Краткая теория", "Тесты", "Презентация"],
        default=["Карта", "Тесты"]
    )
    
    return detailed_theory, selected_items


def render_presentation_settings() -> tuple:
    """
    Отображает настройки презентации.
    
    Returns:
        Кортеж (presentation_slides, presentation_text_volume)
    """
    with st.expander("📊 Настройка презентации", expanded=True):
        p1, p2 = st.columns(2)
        slides = p1.number_input("Количество слайдов:", min_value=3, max_value=50, value=10, step=1)
        text_volume = p2.selectbox("Объем текста:", options=["малый", "средний", "большой"], index=1)
        return slides, text_volume


def render_test_settings() -> tuple:
    """
    Отображает настройки тестирования.
    
    Returns:
        Кортеж (test_type, test_configs)
    """
    with st.expander("📝 Тестирование", expanded=True):
        test_type = st.radio("Формат:", ["Тест", "Практическое тестирование"], horizontal=True)
        num_tests = st.number_input("Количество тестов:", min_value=1, max_value=10, value=1, step=1)
        
        test_configs = []
        for i in range(num_tests):
            st.markdown(f"**Тест #{i+1}**")
            t1, t2, t3, t4 = st.columns(4)
            
            t_difficulty = t1.select_slider(
                f"Сложность {i+1}:",
                options=["Легкий", "Обычный", "Продвинутый"],
                key=f"diff_{i}"
            )
            t_questions = t2.number_input(
                f"Вопросов/заданий {i+1}:",
                min_value=1, max_value=50, value=5, step=1,
                key=f"q_{i}"
            )
            t_variants = t3.number_input(
                f"Вариантов {i+1}:",
                min_value=1, max_value=10, value=1, step=1,
                key=f"v_{i}"
            )
            t_answers = t4.number_input(
                f"Вариантов ответа {i+1}:",
                min_value=2, max_value=10, value=4, step=1,
                key=f"a_{i}"
            )
            
            test_configs.append({
                "difficulty": t_difficulty,
                "questions": t_questions,
                "variants": t_variants,
                "answers": t_answers
            })
            
            if i < num_tests - 1:
                st.divider()
        
        return test_type, test_configs


def render_eval_tools() -> str:
    """
    Отображает поле дополнительных оценочных средств.
    
    Returns:
        Текст дополнительных оценочных средств
    """
    return st.text_input("Доп. оценочные средства", "Самопроверка по эталону")


def render_model_selector() -> str:
    """
    Отображает селектор модели в sidebar.
    
    Returns:
        Выбранная модель
    """
    st.sidebar.title("⚙️ Настройки ИИ")
    return st.sidebar.selectbox(
        "Модель:",
        ["qwen-3-235b-a22b-instruct-2507", "llama3.1-8b", "gpt-oss-120b"]
    )
