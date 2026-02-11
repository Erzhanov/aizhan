import streamlit as st
from config import get_supabase_client
import pandas as pd
from datetime import datetime
from AdminPanelLoginSystem import check_admin
import plotly.express as px

def get_all_questions_with_users():
    try:
        supabase = get_supabase_client()
        questions = supabase.table("questions").select("*").order("timestamp", desc=True).execute().data
        users_response = supabase.table("users").select("id, username, email").execute()
        users = {u['id']: u for u in users_response.data}
        for q in questions:
            user_id = q.get('user_id')
            q['username'] = users.get(user_id, {}).get('username', 'Unknown')
            q['user_email'] = users.get(user_id, {}).get('email', 'Unknown')
        return questions
    except Exception as e:
        st.error(f"Қате: {str(e)}")
        return []

def format_timestamp(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt
    except:
        return timestamp_str

def delete_question(question_id):
    try:
        supabase = get_supabase_client()
        supabase.table("questions").delete().eq("id", question_id).execute()
        return True
    except:
        return False

def suraktardy_bakulay_page():
    if not check_admin():
        st.error("⛔ Бұл бет тек админдерге қол жетімді!")
        return

    st.set_page_config(page_title="🔍 Сұрақтарды бақылау", page_icon="📊", layout="wide")
    st.title("🔍 Сұрақтарды бақылау")
    st.write("Барлық пайдаланушы сұрақтарын зерттеу және талдау")

    questions = get_all_questions_with_users()
    if not questions:
        st.info("Әлі сұрақтар жоқ")
        return

    # Деректерді DataFrame-ге ауыстыру
    df = pd.DataFrame(questions)
    df['timestamp_dt'] = df['timestamp'].apply(format_timestamp)
    df['month'] = df['timestamp_dt'].apply(lambda x: x.strftime('%Y-%m') if isinstance(x, datetime) else '')

    # Sidebar фильтрлер
    st.sidebar.header("Фильтрлер")
    categories = ['medical','medication','psychology']
    category_filter = st.sidebar.multiselect("Санат", options=categories, default=categories)
    users = df['username'].unique().tolist()
    user_filter = st.sidebar.multiselect("Пайдаланушы", options=users, default=users)
    months = df['month'].unique().tolist()
    month_filter = st.sidebar.multiselect("Ай", options=months, default=months)
    search_query = st.sidebar.text_input("Іздеу:", placeholder="Сұрақ мәтінінен іздеу...")

    filtered_df = df[
        (df['category'].isin(category_filter)) &
        (df['username'].isin(user_filter)) &
        (df['month'].isin(month_filter))
    ]
    if search_query:
        filtered_df = filtered_df[filtered_df['question'].str.contains(search_query, case=False, na=False)]

    st.write(f"Көрсетілді: **{len(filtered_df)}** нәтиже")

    # Статистика блоктары
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Барлығы", len(filtered_df))
    col2.metric("Медициналық", len(filtered_df[filtered_df['category']=='medical']))
    col3.metric("Дәрі-дәрмек", len(filtered_df[filtered_df['category']=='medication']))
    col4.metric("Психология", len(filtered_df[filtered_df['category']=='psychology']))
    st.divider()

    # Категория бойынша график
    st.subheader("📊 Сұрақтар саны категория бойынша")
    cat_count = filtered_df['category'].value_counts().reset_index()
    cat_count.columns = ['Category','Count']
    fig = px.bar(cat_count, x='Category', y='Count', text='Count', color='Category', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

    # Пайдаланушы белсенділігі
    st.subheader("👤 Ең белсенді пайдаланушылар")
    user_count = filtered_df['username'].value_counts().reset_index()
    user_count.columns = ['User','Count']
    fig2 = px.bar(user_count.head(10), x='User', y='Count', text='Count', color='User', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

    # Айлық динамика
    st.subheader("📈 Айлық тренд")
    month_count = filtered_df.groupby('month').size().reset_index(name='Count')
    fig3 = px.line(month_count, x='month', y='Count', markers=True)
    st.plotly_chart(fig3, use_container_width=True)

    # Сұрақтарды көрсету
    st.subheader("💬 Сұрақтар мен жауаптар")
    for i, row in filtered_df.iterrows():
        with st.expander(f"#{row['id']} - {row['username']} - {row['question'][:80]}..."):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"👤 **Пайдаланушы:** {row['username']}")
                st.write(f"📧 **Email:** {row['user_email']}")
            with col2:
                category_emoji = {'medical':'⚕️ Медициналық','medication':'💊 Дәрі-дәрмек','psychology':'🧠 Психология'}
                st.write(f"**Санат:** {category_emoji.get(row['category'],'❓ Белгісіз')}")
                st.write(f"🆔 **ID:** {row['id']}")
            with col3:
                st.write(f"🕐 **Уақыт:** {row['timestamp_dt'].strftime('%d.%m.%Y %H:%M') if isinstance(row['timestamp_dt'],datetime) else row['timestamp_dt']}")
            
            st.markdown("**📝 Сұрақ:**")
            st.info(row['question'])
            st.markdown("**💬 Жауап:**")
            st.success(row['answer'])

            col1, col2 = st.columns([1,5])
            with col1:
                if st.button("🗑️ Жою", key=f"delete_{row['id']}"):
                    if delete_question(row['id']):
                        st.success("Сұрақ жойылды!")
                        st.rerun()
                    else:
                        st.error("Жою қатесі!")

    # CSV экспорт
    st.divider()
    if st.button("📥 Барлық деректерді жүктеу CSV"):
        st.download_button(
            "CSV жүктеу",
            filtered_df.to_csv(index=False),
            f"all_questions_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

    # Кестелік көрініс
    with st.expander("📊 Кестелік көрініс"):
        if not filtered_df.empty:
            display_cols = ['id','username','user_email','category','question','answer','timestamp']
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
