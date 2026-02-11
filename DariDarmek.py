import streamlit as st
from openai import OpenAI
from config import OPENAI_API_KEY, get_supabase_client
from datetime import datetime

# -------------------- CONFIG --------------------

st.set_page_config(
    page_title="Дәрі-дәрмек чаты",
    page_icon="💊",
    layout="centered"
)

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------- HELPERS --------------------

def is_medication_question(question: str) -> bool:
    """Дәрі-дәрмекке қатысты ма екенін тексеру"""
    keywords = [
        "дәрі", "таблетка", "препарат", "капсула", "дәрмек",
        "доза", "қабылдау", "жанама әсер",
        "medicine", "drug", "pill", "medication"
    ]
    q = question.lower()
    return any(word in q for word in keywords)


def get_medication_info(question: str) -> str:
    """Дәрі туралы қауіпсіз ақпарат"""
    system_prompt = (
        "Сіз дәрі-дәрмек туралы ақпарат беретін көмекшісіз.\n"
        "ТЕК жалпы ақпарат беріңіз, диагноз қоймаңыз.\n\n"
        "Құрылым:\n"
        "1. 💊 Дәрінің атауы\n"
        "2. 📌 Қолданылуы\n"
        "3. 🕒 Қабылдау тәртібі (жалпы)\n"
        "4. ⚠️ Қарсы көрсетілімдер\n"
        "5. 🤒 Жанама әсерлер\n\n"
        "Әрқашан: «Дәрігермен кеңесіңіз» деп ескертіңіз.\n"
        "Жауапты қазақ тілінде беріңіз."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=0.5,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Қате орын алды: {str(e)}"


def save_medication_query(user_id, question, answer):
    """Supabase-ке сақтау"""
    try:
        supabase = get_supabase_client()
        supabase.table("questions").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "category": "medication",
            "timestamp": datetime.now().isoformat(),
        }).execute()
    except Exception as e:
        st.error(f"Сақтау қатесі: {str(e)}")

# -------------------- UI PAGE --------------------

def daridarmek_page():
    st.title("💊 Дәрі-дәрмек чаты")
    st.caption("Бұл сервис дәрігерді алмастырмайды ⚠️")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Ақпарат")
        st.markdown(
            """
            Бұл бет:
            - Дәрі туралы **жалпы ақпарат** береді
            - ❌ Рецепт жазбайды
            - ❌ Доза тағайындамайды
            """
        )
        if st.button("🗑️ Чатты тазалау"):
            st.session_state.med_chat = []

    # Disclaimer
    if "accepted_med_disclaimer" not in st.session_state:
        st.session_state.accepted_med_disclaimer = False

    if not st.session_state.accepted_med_disclaimer:
        st.warning(
            "Бұл ақпарат тек танысу мақсатында беріледі.\n\n"
            "❗ Дәріні тек дәрігер кеңесімен қабылдаңыз."
        )
        if st.button("✔️ Түсіндім"):
            st.session_state.accepted_med_disclaimer = True
        return

    # Chat history
    if "med_chat" not in st.session_state:
        st.session_state.med_chat = []

    for msg in st.session_state.med_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_question = st.chat_input("Мысалы: Парацетамол не үшін қолданылады?")

    if user_question:
        # User message
        st.session_state.med_chat.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.write(user_question)

        # Validation
        if not is_medication_question(user_question):
            warning = "⚠️ Тек дәрі-дәрмек туралы сұрақ қойыңыз."
            st.session_state.med_chat.append({
                "role": "assistant",
                "content": warning
            })
            with st.chat_message("assistant"):
                st.warning(warning)
            return

        # AI response
        with st.spinner("💊 Ақпарат дайындалуда..."):
            answer = get_medication_info(user_question)

        st.session_state.med_chat.append({
            "role": "assistant",
            "content": answer
        })

        with st.chat_message("assistant"):
            st.write(answer)
            st.info("⚕️ Бұл диагноз емес. Дәрігермен кеңесіңіз.")

        # Save
        if "user_id" in st.session_state:
            save_medication_query(
                st.session_state.user_id,
                user_question,
                answer
            )

    # FAQ
    with st.expander("❓ Жиі қойылатын сұрақтар"):
        st.markdown(
            """
            **Қандай сұрақтар қоюға болады?**
            - Дәрінің не үшін қолданылатыны
            - Жалпы қабылдау тәртібі
            - Жанама әсерлері

            **Қандай сұрақтарға жауап берілмейді?**
            - Қанша мг ішу керек
            - Қандай дәрі жақсы
            - Диагноз қою
            """
        )
