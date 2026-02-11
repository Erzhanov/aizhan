import streamlit as st
from openai import OpenAI
from config import OPENAI_API_KEY, get_supabase_client
from datetime import datetime

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------- HELPERS --------------------

def get_psychological_support(message: str) -> str:
    """Психологиялық қолдау алу"""
    system_prompt = (
        "Сіз мейірімді және кәсіби емес психолог көмекшісісіз. "
        "Адамдардың эмоциялық жағдайын тыңдап, жылы қолдау сөздерін айтыңыз.\n"
        "Міндеттер: эмпатия көрсету, қолдау, позитивті көзқарас қалыптастыру.\n"
        "Қиын жағдайда кәсіби маманға хабарласу керектігін ескертіңіз.\n"
        "Сіз сондай-ақ қысқа тыныштандыру жаттығуларын немесе медитация нұсқауларын ұсына аласыз."
        "Жауапты қазақ тілінде беріңіз, жылы және мейірімді етіп."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.8,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Қате орын алды: {str(e)}"


def save_psychological_session(user_id, message, response):
    try:
        supabase = get_supabase_client()
        supabase.table("questions").insert({
            "user_id": user_id,
            "question": message,
            "answer": response,
            "category": "psychology",
            "timestamp": datetime.now().isoformat(),
        }).execute()
    except Exception as e:
        st.error(f"Сақтау қатесі: {str(e)}")

# -------------------- UI PAGE --------------------

def psixologia_page():
    st.set_page_config(page_title="Психологиялық қолдау", page_icon="🧠")
    st.title("🧠 Психологиялық қолдау")
    st.caption("Сізді тыңдайтын және жылы сөздермен қолдайтын чат")

    # Sidebar ресурстары
    with st.sidebar:
        st.header("🆘 Көмек ресурстары")
        st.write("Қиын жағдайда: ")
        st.write("📞 Психологиялық көмек: 150")
        st.write("📞 Сенім телефоны: +7 708 999 7777")
        st.info("💡 Кеңес: Күнделікті медитация, демалыс және тыныс алу жаттығуларын жасаңыз")

    # Disclaimer
    if 'accepted_psychology_disclaimer' not in st.session_state:
        st.session_state.accepted_psychology_disclaimer = False

    if not st.session_state.accepted_psychology_disclaimer:
        st.warning("Бұл чат кәсіби психолог емес. Қиын жағдайда маманға хабарласыңыз.")
        if st.button("✔️ Түсіндім"):
            st.session_state.accepted_psychology_disclaimer = True
        return

    # Chat history
    if 'psychology_history' not in st.session_state:
        st.session_state.psychology_history = []

    # Chat input
    user_message = st.chat_input("Өзіңізді қалай сезініп тұрсыз?")

    if user_message:
        st.session_state.psychology_history.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.write(user_message)

        with st.spinner("💚 Тыңдап жатырмын..."):
            response = get_psychological_support(user_message)

        st.session_state.psychology_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.success(response)
            st.info("⚕️ Бұл психологиялық қолдау. Қиын жағдайда маманға хабарласыңыз.")

        # Save
        if 'user_id' in st.session_state:
            save_psychological_session(st.session_state.user_id, user_message, response)

    # Show last messages
    if st.session_state.psychology_history:
        st.divider()
        st.subheader("💬 Біздің әңгімеміз")
        for chat in reversed(st.session_state.psychology_history[-10:]):  # last 10 messages
            role_icon = "👤" if chat["role"] == "user" else "💚"
            with st.container():
                col1, col2 = st.columns([1, 12])
                with col1:
                    st.write(role_icon)
                with col2:
                    st.info(chat["content"] if chat["role"] == "user" else chat["content"])
                st.divider()

    # Daily exercises
    with st.expander("💡 Күнделікті психологиялық қолдау"):
        st.write("1. 😴 Жеткілікті ұйықтау (7-9 сағат)")
        st.write("2. 🏃‍♂️ Күн сайын жеңіл жаттығулар жасау")
        st.write("3. 🧘‍♀️ Тыныс алу және медитация жаттығулары")
        st.write("4. 👥 Жақындармен уақыт өткізу")
        st.write("5. 📝 Күнделік жүргізу")
        st.write("6. 🎨 Шығармашылықпен айналысу")
        st.write("7. 🚫 Стрессті азайту әдістерін пайдалану")
        st.write("8. 😊 Өзіңізге мейірімді болу")
        st.write("9. 📚 Позитивті кітаптар оқу немесе мотивациялық контент қарау")
        st.write("10. 🎵 Сүйікті музыка тыңдау, демалу")

    # Quick support buttons
    st.divider()
    st.subheader("⚡ Жылдам қолдау")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Тыныс алу жаттығуы 1 мин"):
            st.info("💨 1 минут тыныс алу жаттығуын бастаңыз: терең дем алып, баяу шығарыңыз")
    with col2:
        if st.button("Жеңіл медитация 3 мин"):
            st.info("🧘 3 минуттық қысқа медитацияны орындаңыз, ойыңызды тыныштандырыңыз")
    with col3:
        if st.button("Позитив ойлар"):
            st.info("😊 1 минут бойы өзіңізді қуантатын позитив ойларды еске алыңыз")