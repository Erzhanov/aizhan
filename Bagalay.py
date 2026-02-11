import streamlit as st
from config import FEEDBACK_FORM_URL, get_supabase_client
from datetime import datetime

def save_feedback(user_id, username, rating, feedback_text, suggestions):
    """Пікірді дерекқорға сақтау"""
    try:
        supabase = get_supabase_client()
        supabase.table("feedback").insert({
            "user_id": user_id,
            "username": username,
            "rating": rating,
            "feedback_text": feedback_text,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"Сақтау қатесі: {str(e)}")
        return False

def bagalay_page():
    st.set_page_config(page_title="💭 Пікір беру", page_icon="💬")
    st.title("💭 Пікір беру")
    st.write("Платформаны жақсарту үшін пікіріңізді қалдырыңыз")

    # Екі нұсқа: жылдам пікір немесе Google Form
    tab1, tab2 = st.tabs(["⚡ Жылдам пікір", "📋 Толық сауалнама"])

    with tab1:
        st.subheader("⚡ Жылдам пікір беру")
        with st.form("quick_feedback_form"):
            # Бағалау
            st.write("**Жүйені қалай бағалайсыз?**")
            rating = st.slider("", 1, 5, 3, help="1 - өте нашар, 5 - өте жақсы")
            emoji_map = {
                1: "😞 Өте нашар",
                2: "😕 Нашар",
                3: "😐 Орташа",
                4: "😊 Жақсы",
                5: "😍 Өте жақсы"
            }
            st.write(f"### {emoji_map[rating]}")

            # Пікір
            feedback_text = st.text_area(
                "**Пікіріңіз:**",
                placeholder="Платформа туралы ойларыңызды жазыңыз...",
                height=150
            )

            # Ұсыныстар
            suggestions = st.text_area(
                "**Не қосқыңыз келеді немесе не жетіспейді?**",
                placeholder="Жаңа функциялар, жақсартулар туралы жазыңыз...",
                height=100
            )

            # Жіберу
            submitted = st.form_submit_button("📤 Жіберу", type="primary", use_container_width=True)
            if submitted:
                if feedback_text or suggestions:
                    username = st.session_state.get('username', 'Anonymous')
                    user_id = st.session_state.get('user_id', None)
                    if save_feedback(user_id, username, rating, feedback_text, suggestions):
                        st.success("✅ Пікіріңіз үшін рахмет! Біз оны міндетті түрде қарастырамыз.")
                        st.balloons()
                    else:
                        st.error("Қате орын алды. Қайта көріңіз.")
                else:
                    st.warning("Кемінде бір өрісті толтырыңыз!")

    with tab2:
        st.subheader("📋 Толық сауалнама (Google Forms)")
        st.write("Толығырақ пікір қалдырғыңыз келсе, Google Forms арқылы сауалнаманы толтырыңыз.")
        st.markdown(f"""
        <div style="text-align:center; padding:20px;">
            <a href="{FEEDBACK_FORM_URL}" target="_blank">
                <button style="
                    background-color:#4CAF50;
                    border:none;
                    color:white;
                    padding:15px 32px;
                    text-align:center;
                    font-size:16px;
                    border-radius:12px;
                    cursor:pointer;
                ">
                    📝 Google Forms сауалнамасын ашу
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 Сауалнама шамамен 3-5 минут алады")

    # Жиі қойылатын сұрақтар
    st.divider()
    with st.expander("❓ Жиі қойылатын сұрақтар"):
        st.markdown("""
        **Пікірлер қаралады ма?** - Иә, барлық пікірлер біздің команда тарапынан қаралады және назарға алынады.
        **Пікір беру анонимді ме?** - Жылдам пікірде аты-жөніңіз көрсетіледі, бірақ Google Forms анонимді болуы мүмкін.
        **Жауап аламын ба?** - Маңызды мәселелер бойынша біз байланысуға тырысамыз.
        **Қаншалықты жиі пікір бере аламын?** - Қалаған уақытта, шектеусіз.
        """)

    # Админ панель статистикасы
    if st.session_state.get('is_admin', False):
        st.divider()
        st.subheader("📊 Пікірлер статистикасы (Админ)")
        try:
            supabase = get_supabase_client()
            response = supabase.table("feedback").select("*").execute()
            feedbacks = response.data
            if feedbacks:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Барлығы пікірлер", len(feedbacks))
                with col2:
                    avg_rating = sum([f.get('rating',0) for f in feedbacks])/len(feedbacks)
                    st.metric("Орташа бағалау", f"{avg_rating:.1f}/5")
                with col3:
                    recent = len([f for f in feedbacks if f.get('timestamp','').startswith(datetime.now().strftime('%Y-%m'))])
                    st.metric("Осы айда", recent)
        except:
            pass

    # Sidebar: байланыс және ақпарат
    with st.sidebar:
        st.header("📞 Байланыс")
        st.write("Сұрақтарыңыз бар ма?")
        st.write("📧 Email: eldosy67@gmail.com")
        st.write("📱 Телефон: +7 705 781 29-35")
        st.divider()
        st.info("💚 Пікіріңіз үшін рахмет! Сіздің ойларыңыз бізге маңызды.")
