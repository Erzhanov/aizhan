import streamlit as st
from Login import check_login, login_page
from AdminPanelLoginSystem import admin_login_page
from Surak import surak_page
from DariDarmek import daridarmek_page
from Psixologia import psixologia_page
from Motivation import motivation_page
from Datasurak import datasurak_page
from Analitika import analitika_page
from SuraktardyBakulay import suraktardy_bakulay_page
from Bagalay import bagalay_page

# -----------------------------
# 🌟 Бет конфигурациясы
# -----------------------------
st.set_page_config(
    page_title="🏥 AI-ZHAN - Медициналық Көмекші",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 🎨 CSS стильдер - Көзге ыңғайлы дизайн (мягкие, успокаивающие цвета: синие, зеленые тона)
# -----------------------------
st.markdown("""
<style>
    /* Негізгі стильдер */
    .main { 
        padding: 1rem; 
        background: linear-gradient(to bottom, #e8f4f8, #d1e8f0); /* Мягкий голубой градиент для фона */
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold;
        transition: all 0.3s ease;
        background-color: #81d4fa; /* Светло-голубой для кнопок */
        color: #2c3e50; /* Темно-синий текст */
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-color: #4fc3f7; /* Немного ярче при hover */
    }
    h1, h2, h3 { 
        color: #00796b; /* Темно-зеленый для заголовков (успокаивающий) */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05); /* Мягкая тень */
    }
    .stSidebar { 
        background: linear-gradient(to bottom, #e0f2f1, #b2dfdb); /* Мягкий зеленоватый градиент для сайдбара */
        border-right: 1px solid #ccc;
        padding: 1rem;
    }
    .stSidebar .stButton>button {
        margin-bottom: 0.5rem;
        background-color: #b2dfdb; /* Светло-зеленый для кнопок в сайдбаре */
        color: #004d40; /* Темно-зеленый текст */
    }
    .stSidebar .stButton>button:hover {
        background-color: #80cbc4; /* Hover эффект */
    }
    /* Карточка стильдері */
    .feature-card {
        background: #f8fcfb; /* Очень светлый зеленоватый фон */
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); /* Мягкая тень */
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    /* Баннер стильдері */
    .banner {
        background: linear-gradient(135deg, #81d4fa, #b3e5fc); /* Мягкий голубой градиент для баннера */
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); /* Мягкая тень */
    }
    /* Қосымша анимациялар (мягкие, не отвлекающие) */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 📜 Қош келдіңіз баннері (нейтральный, без новогодней тематики)
# -----------------------------
def welcome_banner():
    st.markdown("""
        <div class="banner fade-in">
            <h1 style='color:#004d40; margin-bottom: 0.5rem;'>🏥 AI-ZHAN жүйесіне қош келдіңіз!</h1>
            <h3 style='color:#333; margin-top: 0;'>Денсаулыққа қамқорлықпен ✨</h3>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 📜 Интро бөлім - Жақсартылған (более компактная структура)
# -----------------------------
def show_intro():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("🏥 AI-ZHAN")
        st.subheader("Сіздің сенімді медициналық көмекшіңіз")
        st.write("Денсаулық туралы сұрақтарға жылдам жауап алыңыз, дәрі-дәрмектер туралы толық ақпарат алыңыз, психологиялық қолдау мен күнделікті мотивация алыңыз.")
    with col2:
        st.image("https://via.placeholder.com/300x200.png?text=AI-ZHAN", width=300, caption="AI-ZHAN платформасы")

# -----------------------------
# ✨ Мүмкіндіктерді көрсету - Карточка түрінде (улучшенный grid)
# -----------------------------
def show_features():
    st.divider()
    st.header("✨ Біздің мүмкіндіктеріміз")
    features = [
        ("💬 Медициналық сұрақтар", "ИИ-дан денсаулық туралы нақты және сенімді жауаптар алыңыз."),
        ("💊 Дәрі-дәрмек ақпараты", "Дәрілердің толық сипаттамасы, қолдану нұсқаулығы және ескертулер."),
        ("🧠 Психологиялық қолдау", "Эмоциялық қолдау, стресс басқару және психологиялық кеңестер."),
        ("✨ Күнделікті мотивация", "Күн сайын жаңа шабыттандыратын цитаталар мен кеңестер."),
        ("📚 Сұрақтар тарихы", "Өз сұрақтарыңыз бен жауаптарды сақтау және қарау мүмкіндігі."),
        ("💭 Пікір беру", "Платформаны жақсарту үшін өз ойыңызды қалдырыңыз.")
    ]
    cols = st.columns(2)  # Изменено на 2 колонки для лучшей читаемости на мобильных
    for i, (title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="feature-card fade-in">
                    <h3 style="margin-bottom: 0.5rem;">{title}</h3>
                    <p>{desc}</p>
                </div>
            """, unsafe_allow_html=True)

# -----------------------------
# 🔑 Кіру түймелері - Жақсартылған (центрированные)
# -----------------------------
def show_login_buttons():
    st.divider()
    cols = st.columns(2)
    with cols[0]:
        if st.button("👤 Пайдаланушы кіру", type="primary", use_container_width=True):
            st.session_state.login_mode = "user"
            st.rerun()
    with cols[1]:
        if st.button("🔐 Админ кіру", type="secondary", use_container_width=True):
            st.session_state.login_mode = "admin"
            st.rerun()

# -----------------------------
# 📋 Бүйір панель - Жақсартылған (более организованный)
# -----------------------------
def show_sidebar():
    with st.sidebar:
        st.title("🏥 AI-ZHAN")
        if st.session_state.is_admin:
            st.success(f"👨‍💼 Админ: {st.session_state.username}")
        else:
            st.success(f"👤 {st.session_state.username}")
        st.divider()
        st.header("📋 Мәзір")
        menu_items = {
            "💬 Медициналық сұрақтар": "surak",
            "💊 Дәрі-дәрмек": "dari",
            "🧠 Психология": "psixologia",
            "✨ Мотивация": "motivation",
            "📚 Менің тарихым": "datasurak",
            "💭 Пікір беру": "bagalay"
        }
        if st.session_state.is_admin:
            menu_items.update({
                "📊 Аналитика": "analitika",
                "🔍 Сұрақтарды бақылау": "suraktardy"
            })
        if 'current_page' not in st.session_state:
            st.session_state.current_page = list(menu_items.values())[0]
        for label, page in menu_items.items():
            button_type = "primary" if st.session_state.current_page == page else "secondary"
            if st.button(label, use_container_width=True, type=button_type):
                st.session_state.current_page = page
                st.rerun()
        st.divider()
        if st.button("🚪 Шығу", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.divider()
        st.caption("📞 Көмек керек пе?")
        st.caption("eldosy67@gmail.com")
        st.markdown("<p class='fade-in' style='text-align:center; font-size:0.8rem; color:#555;'>© 2025-2026 AI-ZHAN. Барлық құқықтар қорғалған.</p>", unsafe_allow_html=True)

# -----------------------------
# 🔹 Негізгі функция (улучшенная структура: разделение логики входа и контента)
# -----------------------------
def main():
    # Инициализация session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.is_admin = False

    if not st.session_state.logged_in:
        welcome_banner()
        show_intro()
        show_features()
        show_login_buttons()
        if 'login_mode' in st.session_state:
            st.divider()
            if st.session_state.login_mode == "admin":
                admin_login_page()
            else:
                login_page()
        return

    # После входа
    show_sidebar()
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    page = st.session_state.current_page
    pages = {
        "surak": surak_page,
        "dari": daridarmek_page,
        "psixologia": psixologia_page,
        "motivation": motivation_page,
        "datasurak": datasurak_page,
        "analitika": analitika_page,
        "suraktardy": suraktardy_bakulay_page,
        "bagalay": bagalay_page
    }
    if page in pages:
        pages[page]()
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
