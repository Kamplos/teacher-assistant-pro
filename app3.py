import streamlit as st
from cerebras.cloud.sdk import Cerebras
# Запуск streamlit run app3.py
# --- НАСТРОЙКА API ---
CEREBRAS_API_KEY = st.secrets["CEREBRAS_API_KEY"]
client = Cerebras(api_key=CEREBRAS_API_KEY)

st.set_page_config(page_title="Teacher Assistant Pro", page_icon="🎓", layout="wide")

if "page" not in st.session_state: st.session_state.page = "form"
if "result" not in st.session_state: st.session_state.result = ""
if "topic" not in st.session_state: st.session_state.topic = ""


# --- ЛОГИКА ГЕНЕРАЦИИ ---
def generate_lesson(data):
    # Формируем структуру Техкарты на основе PDF
    tech_card_structure = """
    СТРОГО следуй блочно-модульной структуре ФГОС[cite: 1]:
    БЛОК 1. Вхождение в тему: мотивация, актуализация знаний, целеполагание.
    БЛОК 2. Освоение материала: учебные действия, проверка первичного усвоения[cite: 27, 33].
    БЛОК 3. Применение: задания в новых ситуациях, связь с реальной жизнью, задания в формате ГИА (ОГЭ/ЕГЭ), развитие функциональной грамотности.
    БЛОК 4. Проверка: диагностика и критерии оценивания.
    БЛОК 5. Итоги: рефлексия и дифференцированное домашнее задание.
    """

    reqs = []
    if "Карта" in data['items']:
        reqs.append(tech_card_structure)

    if data['detailed_theory']:
        reqs.append(
            "ПОДРОБНЫЙ ТЕОРЕТИЧЕСКИЙ МАТЕРИАЛ: Напиши лонгрид (минимум 1000 слов). "
            "Это должен быть глубокий экспертный текст с историческим контекстом, научными нюансами, "
            "разбором сложных случаев и интересными фактами. НЕ используй тезисы, пиши связным текстом."
        )
    elif "Краткая теория" in data['items']:
        reqs.append("- Краткий конспект теории (тезисно).")

    if "Презентация" in data['items']:
        reqs.append(
            "ПЛАН ПРЕЗЕНТАЦИИ: Составь структуру на 10-12 слайдов. "
            "Контент должен отличаться от текста теории: здесь фокусируйся на визуальных образах, "
            "схемах, инфографике и кратких выводах для экрана. Укажи описание визуала для каждого слайда."
        )

    if "Тесты" in data['items']:
        if data['test_type'] == "Стандартный тест":
            reqs.append(
                f"- ТЕСТ ({data['test_difficulty']}): {data['test_vars']} вар., {data['q_count']} вопр. с ключами.")
        else:
            reqs.append(f"- ПРАКТИКУМ ({data['test_difficulty']}): Задания на работу с контекстом, анализ и синтез.")

    sys_prompt = (
        "Ты — ведущий методист и заслуженный учитель РФ. Твоя задача — создавать материалы экспертного уровня. "
        "Используй профессиональную педагогическую лексику. "
        "МАТЕМАТИКА: Все формулы пиши ТОЛЬКО в формате $inline$ или $$display$$. "
        "Никогда не используй скобки [ ] или ( ) для LaTeX. Примеры: $a^2 + b^2 = c^2$."
    )

    user_prompt = f"""Сформируй комплекс материалов для {data['grade']} класса. 
Предмет: {data['subject']}. Тема: {data['topic']}.
Задачи:
{chr(10).join(reqs)}
Дополнительные средства: {data['eval_tools']}.
Сложность заданий: {data['test_difficulty']}."""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
            model=data['model'],
            temperature=0.6,  # Немного выше для разнообразия текста
            max_completion_tokens=6000  # Увеличено для длинной теории
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка API: {e}"


# --- ИНТЕРФЕЙС ---
st.sidebar.title("⚙️ Настройки ИИ")
selected_model = st.sidebar.selectbox("Модель:", ["qwen-3-235b-a22b-instruct-2507", "llama3.1-8b", "gpt-oss-120b"])

if st.session_state.page == "form":
    st.title("🎓 Конструктор урока по ФГОС")

    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 1, 2])
        grade = c1.selectbox("Класс", [str(i) for i in range(1, 12)])
        subject = c2.selectbox("Предмет", ["Математика", "Физика", "Химия", "Биология", "История", "Русский язык"])
        topic = c3.text_input("Тема урока", placeholder="Введите тему...")

    st.subheader("📦 Состав материалов")
    col_l, col_r = st.columns(2)
    with col_l:
        detailed_theory = st.toggle("✨ Глубокая и объемная теория (Лекция)", value=True)
        selected_items = st.multiselect(
            "Дополнительно:",
            ["Карта", "Краткая теория", "Тесты", "Презентация"],
            default=["Карта", "Тесты"]
        )

    # Инициализация переменных для тестов (чтобы не было ошибок доступа)
    test_type, test_difficulty, test_vars, q_count, a_count = "Стандартный тест", "Обычный", 1, 5, 4
    if "Тесты" in selected_items:
        with st.expander("📝 Настройка тестирования", expanded=True):
            test_type = st.radio("Формат:", ["Стандартный тест", "Практические задания"], horizontal=True)
            d1, d2, d3 = st.columns(3)
            test_difficulty = d1.select_slider("Сложность:", options=["Легкий", "Обычный", "Продвинутый"])
            test_vars = d2.number_input("Вариантов:", 1, 4, 1)
            q_count = d3.number_input("Вопросов:", 3, 20, 5)

    eval_tools = st.text_input("Доп. оценочные средства", "Самопроверка по эталону")

    if st.button("🚀 Сгенерировать материалы", type="primary", use_container_width=True):
        if not topic:
            st.error("Введите тему урока!")
        else:
            st.session_state.topic = topic
            payload = {
                'grade': grade, 'subject': subject, 'topic': topic,
                'items': selected_items, 'detailed_theory': detailed_theory,
                'test_type': test_type, 'test_difficulty': test_difficulty,
                'test_vars': test_vars, 'q_count': q_count, 'a_count': a_count,
                'eval_tools': eval_tools, 'model': selected_model
            }
            with st.spinner("Создаем глубокий контент... это может занять до 30 секунд"):
                st.session_state.result = generate_lesson(payload)
                st.session_state.page = "result"
                st.rerun()

else:
    # Страница результата
    st.button("← Назад", on_click=lambda: setattr(st.session_state, 'page', 'form'))
    st.title(f"📄 Материалы: {st.session_state.topic}")

    st.markdown(st.session_state.result)

    # Исправлена ошибка NameError: используем st.session_state.topic

    file_name_topic = st.session_state.topic.replace(' ', '_')
    st.download_button(
        label="📥 Скачать (Markdown)",
        data=st.session_state.result,
        file_name=f"lesson_{file_name_topic}.md",
        mime="text/markdown"

    )