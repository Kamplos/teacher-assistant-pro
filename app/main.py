"""
Teacher Assistant Pro - Конструктор уроков по ФГОС.
Основной файл приложения Streamlit.

Запуск: streamlit run app/main.py
"""

import streamlit as st

from app.config import PAGE_CONFIG, AVAILABLE_MODELS
from app.utils.generator import LessonGenerator


def init_session_state():
    """Инициализирует переменные состояния сессии."""
    if "page" not in st.session_state:
        st.session_state.page = "form"
    if "result" not in st.session_state:
        st.session_state.result = ""
    if "topic" not in st.session_state:
        st.session_state.topic = ""


def main():
    """Основная функция приложения."""
    # Настройка страницы
    st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        page_icon=PAGE_CONFIG["page_icon"],
        layout=PAGE_CONFIG["layout"]
    )
    
    # Инициализация состояния
    init_session_state()
    
    # Инициализация генератора
    try:
        api_key = st.secrets["CEREBRAS_API_KEY"]
        generator = LessonGenerator(api_key)
    except KeyError:
        st.error("❌ Не найден API ключ CEREBRAS_API_KEY в secrets.")
        st.info("Добавьте ключ в файл .streamlit/secrets.toml или настройте secrets в облаке.")
        return
    
    # Выбор модели в sidebar
    st.sidebar.title("⚙️ Настройки ИИ")
    selected_model = st.sidebar.selectbox("Модель:", AVAILABLE_MODELS)
    
    # Отображение нужной страницы
    if st.session_state.page == "form":
        from app.components.result_components import render_form_page
        render_form_page(generator, selected_model)
    else:
        from app.components.result_components import render_result_page
        render_result_page(st.session_state.result, st.session_state.topic)


if __name__ == "__main__":
    main()
