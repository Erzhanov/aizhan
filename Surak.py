import streamlit as st
from openai import OpenAI
from config import OPENAI_API_KEY, get_supabase_client
from datetime import datetime

# -------------------- CONFIG --------------------

st.set_page_config(page_title="Medical Chat", page_icon="💬", layout="centered")

client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------- AI HELPERS --------------------

def is_medical_question(question: str) -> bool:
    """Сұрақтың медициналық екенін тексеру"""
    system_prompt = (
        "Сіз медициналық сұрақтарды анықтаушысыз. "
        "Келесі сұрақ медицинаға қатысты ма екенін анықтаңыз. "
        "Медициналық сұрақтар: симптомдар, аурулар, денсаулық, емдеу, диагноз. "
        "Тек 'ИӘ' немесе 'ЖОҚ' деп жауап беріңіз."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            max_tokens=5,
            temperature=0,
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer == "ИӘ"
    except Exception:
        return True


def detect_emergency(question: str) -> bool:
    """Қауіпті симптомдарды анықтау"""
    danger_keywords = [
        "кеуде", "тыныс", "тұншығу", "есінен тану",
        "қан кет", "жоғары температура", "қатты ауырсыну",
        "инсульт", "жүрек ұстамасы",
    ]
    q = question.lower()
    return any(word in q for word in danger_keywords)


def get_medical_answer(question: str) -> str:
    """Медициналық сұраққа жауап беру"""
    system_prompt = (
        "Сіз медициналық көмекші ботсыз. "
        "Бұл диагноз емес екенін әрқашан ескертіңіз. "
        "Жауапты қысқа, нақты және мейірімді беріңіз. "
        "Қадамдап кеңес беріңіз. "
        "Қауіпті симптом болса – дәрігерге немесе жедел жәрдемге жүгінуді ұсыныңыз. "
        "Жауапты қазақ тілінде беріңіз."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            max_tokens=900,
            temperature=0.6,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Қате орын алды: {str(e)}"


# -------------------- DATABASE --------------------

def save_question_answer(user_id, question, answer, category="medical"):
    try:
        supabase = get_supabase_client()
        supabase.table("questions").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }).execute()
    except Exception as e:
        st.error(f"Сақтау қатесі: {str(e)}")


# -------------------- UI PAGE --------------------

def surak_page():
    st.title("💬 Медициналық чат")
    st.caption("Денсаулыққа қатысты сұрақ қойыңыз. Бұл медициналық диагноз емес ⚠️")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Баптаулар")
        if st.button("🗑️ Чатты тазалау"):
            st.session_state.chat_history = []
        st.markdown("---")
        st.markdown("**Ескерту:** Бұл сервис дәрігерді алмастырмайды.")

    # Disclaimer
    if "accepted_disclaimer" not in st.session_state:
        st.session_state.accepted_disclaimer = False

    if not st.session_state.accepted_disclaimer:
        st.warning("Бұл сервис медициналық диагноз қоймайды. Қауіпті жағдайда жедел жәрдем шақырыңыз 🚑")
        if st.button("✔️ Мен түсіндім"):
            st.session_state.accepted_disclaimer = True
        return

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_question = st.chat_input("Сұрағыңызды жазыңыз...")

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        with st.chat_message("user"):
            st.write(user_question)

        # Emergency alert
        if detect_emergency(user_question):
            with st.chat_message("assistant"):
                st.error("🚑 Қауіпті симптомдар байқалады. Шұғыл түрде дәрігерге немесе жедел жәрдемге жүгініңіз!")

        # Medical validation
        with st.spinner("🔍 Сұрақ тексерілуде..."):
            if not is_medical_question(user_question):
                warning_text = "⚠️ Тек медициналық сұрақтар қойыңыз (симптомдар, аурулар, емдеу)."
                st.session_state.chat_history.append({"role": "assistant", "content": warning_text})
                with st.chat_message("assistant"):
                    st.warning(warning_text)
                return

        # AI answer
        with st.spinner("🧠 AI жауап дайындауда..."):
            answer = get_medical_answer(user_question)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        with st.chat_message("assistant"):
            st.write(answer)
            st.info("⚕️ Бұл ақпарат жалпы сипатта. Міндетті түрде дәрігерге көрініңіз.")

        if "user_id" in st.session_state:
            save_question_answer(st.session_state.user_id, user_question, answer, "medical")

    with st.expander("ℹ️ Маңызды ақпарат"):
        st.markdown(
            """
            - Бұл сервис **диагноз қоймайды**
            - Кеуде ауруы, есінен тану, қан кету – 🚑 **шұғыл жәрдем шақырыңыз**
            - Барлық сұрақтар құпия сақталады 🔐
            """
        )
