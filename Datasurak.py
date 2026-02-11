import streamlit as st
from config import get_supabase_client
import pandas as pd
from datetime import datetime

def get_user_questions(user_id):
    """Пайдаланушының сұрақтарын алу"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("questions").select("*").eq("user_id", user_id).order("timestamp", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Деректерді алу қатесі: {str(e)}")
        return []

def format_timestamp(timestamp_str):
    """Уақытты форматтау"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return timestamp_str

def datasurak_page():
    st.title("📚 Менің сұрақтарым")
    st.write("Сіздің сұрақтар тарихыңыз")
    
    if 'user_id' not in st.session_state:
        st.warning("Тарихты көру үшін жүйеге кіріңіз.")
        return
    
    # Пайдаланушы сұрақтарын алу
    questions = get_user_questions(st.session_state.user_id)
    
    if not questions:
        st.info("Әлі сұрақтар жоқ. Сұрақ қоюды бастаңыз!")
        return
    
    # Статистика
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Барлығы сұрақтар", len(questions))
    with col2:
        medical_count = len([q for q in questions if q.get('category') == 'medical'])
        st.metric("Медициналық", medical_count)
    with col3:
        medication_count = len([q for q in questions if q.get('category') == 'medication'])
        st.metric("Дәрі туралы", medication_count)
    
    st.divider()
    
    # Фильтрация
    categories = ["Барлығы", "Медициналық", "Дәрі-дәрмек", "Психология"]
    selected_category = st.selectbox("Санат бойынша сүзу:", categories)
    
    # Іздеу
    search_query = st.text_input("🔍 Іздеу:", placeholder="Сұрақта не жауапта іздеу...")
    
    # Сұрақтарды фильтрлеу
    filtered_questions = questions
    
    if selected_category != "Барлығы":
        category_map = {
            "Медициналық": "medical",
            "Дәрі-дәрмек": "medication",
            "Психология": "psychology"
        }
        filtered_questions = [q for q in questions if q.get('category') == category_map.get(selected_category)]
    
    if search_query:
        filtered_questions = [
            q for q in filtered_questions 
            if search_query.lower() in q.get('question', '').lower() 
            or search_query.lower() in q.get('answer', '').lower()
        ]
    
    st.write(f"Табылды: **{len(filtered_questions)}** нәтиже")
    
    # Сұрақтарды көрсету
    for i, question in enumerate(filtered_questions):
        with st.expander(f"📝 {question.get('question', 'Сұрақ')[:100]}..."):
            # Метадеректер
            col1, col2 = st.columns([2, 1])
            with col1:
                category_emoji = {
                    'medical': '⚕️',
                    'medication': '💊',
                    'psychology': '🧠',
                }
                emoji = category_emoji.get(question.get('category'), '❓')
                st.write(f"{emoji} **Санат:** {question.get('category', 'белгісіз')}")
            with col2:
                timestamp = format_timestamp(question.get('timestamp', ''))
                st.write(f"🕐 **Уақыт:** {timestamp}")
            
            st.divider()
            
            # Сұрақ
            st.markdown("**Сұрақ:**")
            st.info(question.get('question', ''))
            
            # Жауап
            st.markdown("**Жауап:**")
            st.success(question.get('answer', ''))
    
    # Экспорт опциясы
    st.divider()
    if st.button("📥 CSV форматында жүктеу"):
        if filtered_questions:
            df = pd.DataFrame(filtered_questions)
            csv = df.to_csv(index=False)
            st.download_button(
                label="CSV жүктеу",
                data=csv,
                file_name=f"questions_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Экспорттау үшін деректер жоқ")
    
    # Тазалау опциясы
    with st.sidebar:
        st.header("⚙️ Параметрлер")
        if st.button("🗑️ Тарихты тазалау", type="secondary"):
            if st.checkbox("Растаймын"):
                try:
                    supabase = get_supabase_client()
                    supabase.table("questions").delete().eq("user_id", st.session_state.user_id).execute()
                    st.success("Тарих тазаланды!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Қате: {str(e)}")