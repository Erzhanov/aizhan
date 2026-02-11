import streamlit as st
from openai import OpenAI
from config import OPENAI_API_KEY
from datetime import datetime
import random
from html import escape

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------- HELPERS --------------------

def get_daily_motivation():
    system_prompt = (
        "Сіз мотивациялық көмекшісіз.\n"
        "Күн сайын адамдарға жігерлендіретін, рухтандыратын сөздер айтыңыз.\n"
        "Хабарлама 3-5 сөйлемнен тұруы тиіс, позитивті, іс-әрекетке шақыратын, күш-жігер беретін сөздер."
        "Жауапты қазақ тілінде беріңіз."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Маған бүгінге мотивация беріңіз"}
            ],
            temperature=0.9,
            max_tokens=300
        )
        return response.choices[0].message.content
    except:
        return get_fallback_motivation()


def get_fallback_motivation():
    motivations = [
        "🌟 Әр жаңа күн - жаңа мүмкіндік! Бүгін өзіңіздің ең жақсы нұсқаңыз болыңыз!",
        "💪 Сіздің күшіңіз сіздің ойларыңыздан басталады. Өзіңізге сеніңіз!",
        "🎯 Үлкен жетістіктер кішкене қадамдардан басталады. Алға!",
        "🌈 Қиындықтар өтеді, бірақ сіздің күшіңіз мәңгі қалады!",
        "⭐ Сіз өз өміріңіздің авторысыз. Өз тарихыңызды жазыңыз!",
        "🔥 Табыс - бұл жолдағы әр қадам. Тоқтамаңыз!",
        "🌸 Өзіңізді дамытыңыз, өсіңіз, жарқырайсыз!",
        "💎 Сіз бағалысыз. Өз құндылығыңызды еш уақытта ұмытпаңыз!"
    ]
    return random.choice(motivations)


def get_custom_motivation(topic):
    system_prompt = f"""Сіз мотивациялық көмекшісіз. {topic} тақырыбы бойынша шабыттандыратын сөздер беріңіз."
Жауап 3-5 сөйлемнен тұрсын, қазақ тілінде."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{topic} туралы мотивация"}
            ],
            temperature=0.9,
            max_tokens=300
        )
        return response.choices[0].message.content
    except:
        return get_fallback_motivation()


def display_powerful_motivation(text):
    colors = ["#FF4B4B", "#FF8C42", "#FFD93D", "#6BCB77", "#4D96FF", "#A66DD4"]
    color = random.choice(colors)
    safe_text = escape(text).replace("\n", "<br>")
    st.markdown(
        f"""
        <div style="
            max-width: 820px;
            margin: 0 auto;
            padding: 16px 18px;
            border-radius: 12px;
            border-left: 6px solid {color};
            background: #f9fafb;
        ">
            <p style="
                margin: 0;
                text-align: center;
                color: #1f2937;
                font-size: clamp(18px, 2.4vw, 30px);
                line-height: 1.55;
                font-weight: 600;
                word-break: break-word;
            ">
                {safe_text}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------- UI PAGE --------------------

def motivation_page():
    st.set_page_config(page_title="Күшті мотивация", page_icon="✨")
    st.title("✨ Күшті Мотивация")
    st.write("Өзіңізді көтеріңіз, шабыттаныңыз және күш-қуат алыңыз!")

    today = datetime.now().strftime("%d %B, %Y")
    st.subheader(f"📅 {today}")

    # Daily motivation
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🎁 Бүгінгі мотивацияны алу", type="primary", use_container_width=True):
            with st.spinner("Дайындалуда..."):
                motivation = get_daily_motivation()
                display_powerful_motivation(motivation)

    with col2:
        if st.button("🔄 Жаңарту"):
            st.rerun()

    st.divider()

    # Custom topic motivation
    st.subheader("🎯 Арнайы мотивация")
    topics = ["Денсаулық", "Жұмыс", "Оқу", "Спорт", "Өзін-өзі дамыту", "Отбасы", "Достық", "Шығармашылық"]
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_topic = st.selectbox("Тақырыпты таңдаңыз:", topics)
    with col2:
        st.write("")
        st.write("")
        if st.button("Алу", use_container_width=True):
            with st.spinner("Дайындалуда..."):
                custom_mot = get_custom_motivation(selected_topic)
                display_powerful_motivation(custom_mot)

    st.divider()

    # Motivational quotes
    with st.expander("💬 Мотивациялық дәйексөздер"):
        quotes = [
            "\"Табысқа жету жолындағы кедергілер - сіздің күшіңіздің дәлелі.\"",
            "\"Үлкен жетістіктер үлкен қадамдарды қажет етеді.\"",
            "\"Сіз өзіңізді жеңген кезде, әлемді жеңесіз.\"",
            "\"Әр күн - жаңа мүмкіндік. Оны пайдаланыңыз!\"",
            "\"Табыс - бұл жолдағы әр қадамыңыз.\"",
            "\"Өз армандарыңызды шынайы етіңіз!\""
        ]
        for quote in quotes:
            st.write(quote)

    # Sidebar stats and tips
    with st.sidebar:
        st.header("📊 Сіздің көрсеткіштеріңіз")
        st.metric("Мотивация алғансыз", "🔥", "")
        st.write("Күн сайын мотивация алыңыз!")
        st.divider()
        st.header("💡 Кеңестер")
        st.info("Таңертең оянғанда бірінші мотивацияны оқыңыз. Күнді шабытпен бастаңыз!")
        if st.button("🎯 Күннің тақырыбына мотивация алу"):
            topic = random.choice(topics)
            mot = get_custom_motivation(topic)
            display_powerful_motivation(mot)
