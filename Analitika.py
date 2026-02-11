import streamlit as st
from config import get_supabase_client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, timezone
from AdminPanelLoginSystem import check_admin
import numpy as np

# Бет конфигурациясы
st.set_page_config(
    page_title="Аналитика Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def get_total_users():
    """Барлық пайдаланушыларды алу"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("users").select("*").execute()
        return len(response.data), response.data
    except Exception as e:
        st.error(f"Қате: {e}")
        return 0, []

def get_total_questions():
    """Барлық сұрақтарды алу"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("questions").select("*").execute()
        return len(response.data), response.data
    except Exception as e:
        st.error(f"Қате: {e}")
        return 0, []

def get_questions_by_category():
    """Санаттар бойынша сұрақтар"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("questions").select("category").execute()
        categories = {}
        for item in response.data:
            cat = item.get('category', 'Белгісіз')
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    except Exception:
        return {}

def get_daily_statistics(start_date, end_date):
    """Күнделікті статистика, күндер аралығы бойынша"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("questions").select("timestamp").gte('timestamp', start_date.isoformat()).lte('timestamp', end_date.isoformat()).execute()
        
        # Күндер бойынша топтау
        daily_counts = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_counts[date_str] = 0
            current_date += timedelta(days=1)
        
        for item in response.data:
            try:
                dt = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d')
                if date_str in daily_counts:
                    daily_counts[date_str] += 1
            except Exception:
                continue
        
        return daily_counts
    except Exception:
        return {}

def get_user_growth(start_date, end_date):
    """Пайдаланушылардың өсу статистикасы"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("users").select("created_at").gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat()).execute()
        
        daily_growth = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_growth[date_str] = 0
            current_date += timedelta(days=1)
        
        for item in response.data:
            try:
                dt = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d')
                if date_str in daily_growth:
                    daily_growth[date_str] += 1
            except Exception:
                continue
        
        # Кумулятивті өсу
        cumulative = {}
        total = 0
        for date_str in sorted(daily_growth.keys()):
            total += daily_growth[date_str]
            cumulative[date_str] = total
        
        return daily_growth, cumulative
    except Exception:
        return {}, {}

def get_top_users(limit=10):
    """Ең белсенді пайдаланушылар"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("questions").select("user_id, username").execute()
        user_counts = {}
        for item in response.data:
            user = item.get('username') or item.get('user_id', 'Белгісіз')
            user_counts[user] = user_counts.get(user, 0) + 1
        
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return sorted_users
    except Exception:
        return []

def get_active_users(days=7):
    """Соңғы күндердегі белсенді пайдаланушылар"""
    try:
        start_date = datetime.now(tz=timezone.utc) - timedelta(days=days)
        supabase = get_supabase_client()
        response = supabase.table("questions").select("user_id, username, timestamp").gte('timestamp', start_date.isoformat()).execute()
        
        unique_users = set()
        for item in response.data:
            user = item.get('username') or item.get('user_id')
            if user:
                unique_users.add(user)
        
        return len(unique_users)
    except Exception:
        return 0

def get_hourly_distribution():
    """Сағат бойынша үлестірім"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("questions").select("timestamp").execute()
        
        hourly_counts = {i: 0 for i in range(24)}
        
        for item in response.data:
            try:
                dt = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                hour = dt.hour
                hourly_counts[hour] += 1
            except Exception:
                continue
        
        return hourly_counts
    except Exception:
        return {}

def create_gauge_chart(value, max_value, title):
    """Gauge chart жасау"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': max_value * 0.8},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value * 0.5], 'color': '#e8f5e9'},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': '#fff3e0'},
                {'range': [max_value * 0.8, max_value], 'color': '#ffebee'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def analitika_page():
    # Админ тексеру
    if not check_admin():
        st.error("⛔ Бұл бет тек админдерге қол жетімді!")
        st.info("Жүйеге админ ретінде кіріңіз")
        return
    
    # Тақырып
    st.markdown('<h1 class="main-header">📊 Жүйе аналитикасы - Толықтандырылған Dashboard</h1>', unsafe_allow_html=True)
    
    # Сайдбар фильтрлер
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/analytics.png", width=150)
        st.header("⚙️ Баптаулар мен фильтрлер")
        
        st.subheader("📅 Күндер аралығы")
        default_end = date.today()
        default_start = default_end - timedelta(days=30)
        start_date = st.date_input("Бастау күні", default_start)
        end_date = st.date_input("Аяқтау күні", default_end)
        
        if start_date > end_date:
            st.error("❌ Бастау күні аяқтау күнінен бұрын болуы керек!")
            return
        
        st.divider()
        
        st.subheader("📈 Қосымша опциялар")
        show_trends = st.checkbox("Трендтерді көрсету", value=True)
        show_predictions = st.checkbox("Болжамдарды көрсету", value=False)
        
        st.divider()
        
        st.subheader("📊 Статистика кезеңі")
        period_days = st.slider("Соңғы күндер", 7, 90, 30)
        
        st.divider()
        
        if st.button("🔄 Деректерді жаңарту", use_container_width=True):
            st.rerun()
    
    # Деректерді жүктеу
    with st.spinner('Деректер жүктелуде...'):
        total_users, users_data = get_total_users()
        total_questions, questions_data = get_total_questions()
        categories = get_questions_by_category()
        active_users_7d = get_active_users(7)
        active_users_30d = get_active_users(30)
    
    # Табтар
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Жалпы шолу",
        "🗂️ Санаттар",
        "📅 Динамика",
        "👥 Пайдаланушылар",
        "⏰ Белсенділік",
        "📥 Экспорт"
    ])
    
    # ========== ТАБ 1: ЖАЛПЫ ШОЛУ ==========
    with tab1:
        st.header("📈 Негізгі көрсеткіштер")
        
        # Негізгі метрикалар
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            new_users_7d = len([u for u in users_data if (datetime.now(tz=timezone.utc) - datetime.fromisoformat(u.get('created_at', datetime.now(tz=timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 7])
            st.metric(
                "👥 Барлық пайдаланушылар",
                f"{total_users:,}",
                delta=f"+{new_users_7d} (7 күн)",
                delta_color="normal"
            )
        
        with col2:
            today_questions = len([q for q in questions_data if q.get('timestamp', '').startswith(datetime.now(tz=timezone.utc).strftime('%Y-%m-%d'))])
            st.metric(
                "❓ Барлық сұрақтар",
                f"{total_questions:,}",
                delta=f"+{today_questions} (Бүгін)",
                delta_color="normal"
            )
        
        with col3:
            avg_per_user = round(total_questions / total_users, 1) if total_users > 0 else 0
            st.metric(
                "📊 Орташа сұрақ/адам",
                f"{avg_per_user}",
                delta="Жақсы" if avg_per_user > 5 else "Орташа",
                delta_color="normal"
            )
        
        with col4:
            unique_dates = set([q.get('timestamp', '')[:10] for q in questions_data if q.get('timestamp')])
            avg_daily_questions = round(total_questions / max(len(unique_dates), 1), 1)
            percent_change = round((today_questions / avg_daily_questions - 1) * 100, 1) if avg_daily_questions > 0 else 0
            st.metric(
                "📅 Бүгінгі сұрақтар",
                f"{today_questions}",
                delta=f"{percent_change}%",
                delta_color="normal"
            )
        
        with col5:
            engagement_pct = round(active_users_7d / total_users * 100, 1) if total_users > 0 else 0
            st.metric(
                "🟢 7 күндегі белсенді",
                f"{active_users_7d}",
                delta=f"{engagement_pct}% жалпыдан",
                delta_color="normal"
            )
        
        st.divider()
        
        # Қосымша статистика
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("🎯 Белсенділік көрсеткіштері")
            engagement_rate = round((active_users_7d / total_users * 100), 1) if total_users > 0 else 0
            st.metric("7 күндік белсенділік", f"{engagement_rate}%")
            st.progress(engagement_rate / 100)
            
            retention_rate = round((active_users_30d / total_users * 100), 1) if total_users > 0 else 0
            st.metric("30 күндік қайтарым", f"{retention_rate}%")
            st.progress(retention_rate / 100)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("📊 Сұрақтар статистикасы")
            if questions_data:
                last_7_days = [q for q in questions_data if (datetime.now(tz=timezone.utc) - datetime.fromisoformat(q.get('timestamp', datetime.now(tz=timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 7]
                st.metric("Соңғы 7 күн", len(last_7_days))
                
                last_30_days = [q for q in questions_data if (datetime.now(tz=timezone.utc) - datetime.fromisoformat(q.get('timestamp', datetime.now(tz=timezone.utc).isoformat()).replace('Z', '+00:00'))).days <= 30]
                st.metric("Соңғы 30 күн", len(last_30_days))
                
                avg_daily = round(len(last_30_days) / 30, 1)
                st.metric("Орташа күніне", avg_daily)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("🏆 Рекордтар")
            if questions_data:
                dates_count = {}
                for q in questions_data:
                    date_str = q.get('timestamp', '')[:10]
                    dates_count[date_str] = dates_count.get(date_str, 0) + 1
                
                if dates_count:
                    max_day = max(dates_count.items(), key=lambda x: x[1])
                    st.metric("Ең белсенді күн", max_day[0])
                    st.metric("Сұрақтар саны", max_day[1])
                    
                    st.metric("Санаттар саны", len(categories))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Gauge charts
        st.subheader("🎯 Өнімділік индикаторлары")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_gauge1 = create_gauge_chart(active_users_7d, total_users, "Белсенді пайдаланушылар")
            st.plotly_chart(fig_gauge1, use_container_width=True)
        
        with col2:
            fig_gauge2 = create_gauge_chart(today_questions, 500, "Бүгінгі сұрақтар")
            st.plotly_chart(fig_gauge2, use_container_width=True)
        
        with col3:
            fig_gauge3 = create_gauge_chart(len(categories), 20, "Санаттар саны")
            st.plotly_chart(fig_gauge3, use_container_width=True)
    
    # ========== ТАБ 2: САНАТТАР ==========
    with tab2:
        st.header("🗂️ Сұрақтар санаттары бойынша талдау")
        
        if categories:
            col1, col2 = st.columns(2)
            
            with col1:
                # Donut chart
                fig_pie = px.pie(
                    values=list(categories.values()),
                    names=list(categories.keys()),
                    title="<b>Санаттар бойынша үлесі</b>",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Саны: %{value}<br>Үлесі: %{percent}<extra></extra>'
                )
                fig_pie.update_layout(
                    showlegend=True,
                    height=500,
                    font=dict(size=12)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                fig_bar = px.bar(
                    x=[cat[1] for cat in sorted_cats],
                    y=[cat[0] for cat in sorted_cats],
                    orientation='h',
                    title="<b>Санаттар бойынша сұрақтар саны</b>",
                    labels={'x': 'Сұрақтар саны', 'y': 'Санат'},
                    color=[cat[1] for cat in sorted_cats],
                    color_continuous_scale='Viridis',
                    text=[cat[1] for cat in sorted_cats]
                )
                fig_bar.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Саны: %{x}<extra></extra>'
                )
                fig_bar.update_layout(height=500)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            
            # Санаттар бойынша детальды кесте
            st.subheader("📋 Санаттар детальды статистикасы")
            
            min_timestamp = min([q.get('timestamp', datetime.now(tz=timezone.utc).isoformat()) for q in questions_data], default=datetime.now(tz=timezone.utc).isoformat())
            min_dt = datetime.fromisoformat(min_timestamp.replace('Z', '+00:00'))
            days_since_min = max((datetime.now(tz=timezone.utc) - min_dt).days, 1)
            
            cat_df = pd.DataFrame([
                {
                    'Санат': cat,
                    'Сұрақтар саны': count,
                    'Үлесі (%)': round(count / total_questions * 100, 2),
                    'Орташа күніне': round(count / days_since_min, 2)
                }
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)
            ])
            
            st.dataframe(
                cat_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Санат": st.column_config.TextColumn("Санат", width="medium"),
                    "Сұрақтар саны": st.column_config.NumberColumn("Саны", format="%d"),
                    "Үлесі (%)": st.column_config.ProgressColumn("Үлесі", format="%.2f%%", min_value=0, max_value=100),
                    "Орташа күніне": st.column_config.NumberColumn("Күніне", format="%.2f")
                }
            )
            
        else:
            st.info("📭 Санаттар бойынша деректер жоқ")
    
    # ========== ТАБ 3: ДИНАМИКА ==========
    with tab3:
        st.header("📅 Күнделікті және өсу динамикасы")
        
        daily_stats = get_daily_statistics(start_date, end_date)
        
        if daily_stats:
            dates = sorted(daily_stats.keys())
            counts = [daily_stats[d] for d in dates]
            
            # Line chart with area
            fig_line = go.Figure()
            
            fig_line.add_trace(go.Scatter(
                x=dates,
                y=counts,
                mode='lines+markers',
                name='Сұрақтар',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, symbol='circle'),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)',
                hovertemplate='<b>Күні:</b> %{x}<br><b>Сұрақтар:</b> %{y}<extra></extra>'
            ))
            
            if show_trends and len(counts) > 1:
                # Тренд желісі
                z = np.polyfit(range(len(counts)), counts, 1)
                p = np.poly1d(z)
                fig_line.add_trace(go.Scatter(
                    x=dates,
                    y=p(range(len(counts))),
                    mode='lines',
                    name='Тренд',
                    line=dict(color='red', width=2, dash='dash'),
                    hovertemplate='<b>Тренд:</b> %{y:.1f}<extra></extra>'
                ))
            
            fig_line.update_layout(
                title="<b>Күнделікті сұрақтар динамикасы</b>",
                xaxis_title="Күні",
                yaxis_title="Сұрақтар саны",
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Статистикалық көрсеткіштер
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_daily = round(sum(counts) / len(counts), 1) if len(counts) > 0 else 0
                st.metric("📊 Орташа күніне", avg_daily)
            
            with col2:
                max_daily = max(counts) if counts else 0
                max_date = dates[counts.index(max_daily)] if counts else ""
                st.metric("📈 Максимум", max_daily, delta=max_date)
            
            with col3:
                min_daily = min(counts) if counts else 0
                min_date = dates[counts.index(min_daily)] if counts else ""
                st.metric("📉 Минимум", min_daily, delta=min_date)
            
            with col4:
                total_period = sum(counts)
                st.metric("📦 Жалпы кезеңде", total_period)
            
            st.divider()
            
            # Пайдаланушылардың өсуі
            st.subheader("👥 Пайдаланушылардың өсу динамикасы")
            
            daily_growth, cumulative_growth = get_user_growth(start_date, end_date)
            growth_dates = sorted(daily_growth.keys())
            growth_counts = [daily_growth[d] for d in growth_dates]
            cumulative_counts = [cumulative_growth[d] for d in growth_dates]
            
            fig_growth = go.Figure()
            
            fig_growth.add_trace(go.Bar(
                x=growth_dates,
                y=growth_counts,
                name='Жаңа пайдаланушылар',
                marker_color='#2ca02c',
                hovertemplate='<b>Күні:</b> %{x}<br><b>Жаңа:</b> %{y}<extra></extra>'
            ))
            
            fig_growth.add_trace(go.Scatter(
                x=growth_dates,
                y=cumulative_counts,
                mode='lines+markers',
                name='Кумулятивті',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=6),
                yaxis='y2',
                hovertemplate='<b>Күні:</b> %{x}<br><b>Барлығы:</b> %{y}<extra></extra>'
            ))
            
            fig_growth.update_layout(
                title="<b>Пайдаланушылардың өсу динамикасы</b>",
                xaxis_title="Күні",
                yaxis_title="Жаңа пайдаланушылар",
                yaxis2=dict(
                    title="Кумулятивті саны",
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)
            
            # Өсу статистикасы
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_growth = round(sum(growth_counts) / len(growth_counts), 1) if growth_counts else 0
                st.metric("📊 Орташа күніне", avg_growth)
            
            with col2:
                total_new = sum(growth_counts)
                st.metric("✅ Жаңа жалпы", total_new)
            
            with col3:
                if len(cumulative_counts) > 0 and cumulative_counts[0] > 0:
                    growth_rate = round((cumulative_counts[-1] / cumulative_counts[0] - 1) * 100, 1)
                    st.metric("📈 Өсу қарқыны", f"{growth_rate}%")
                else:
                    st.metric("📈 Өсу қарқыны", "N/A")
            
            with col4:
                if len(growth_counts) >= 7:
                    last_week = sum(growth_counts[-7:])
                    st.metric("📅 Соңғы 7 күн", last_week)
                else:
                    st.metric("📅 Соңғы 7 күн", sum(growth_counts))
        
        else:
            st.info("📭 Таңдалған кезеңде деректер жоқ")
    
    # ========== ТАБ 4: ПАЙДАЛАНУШЫЛАР ==========
    with tab4:
        st.header("👥 Пайдаланушылар аналитикасы")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top пайдаланушылар
            st.subheader("🏆 Ең белсенді пайдаланушылар")
            top_users = get_top_users(15)
            
            if top_users:
                users_list, counts_list = zip(*top_users)
                
                fig_top = px.bar(
                    x=counts_list,
                    y=users_list,
                    orientation='h',
                    title="<b>Топ-15 пайдаланушылар (сұрақтар саны бойынша)</b>",
                    labels={'x': 'Сұрақтар саны', 'y': 'Пайдаланушы'},
                    color=counts_list,
                    color_continuous_scale='RdYlGn',
                    text=counts_list
                )
                fig_top.update_traces(
                    texttemplate='%{text}',
                    textposition='outside'
                )
                fig_top.update_layout(
                    height=600,
                    yaxis={'autorange': 'reversed'}
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("📭 Пайдаланушылар деректері жоқ")
        
        with col2:
            # Соңғы тіркелгендер
            st.subheader("🕒 Соңғы тіркелген пайдаланушылар")
            if users_data:
                users_df = pd.DataFrame(users_data)
                if 'created_at' in users_df.columns:
                    users_df['created_at'] = pd.to_datetime(users_df['created_at'])
                    users_df = users_df.sort_values('created_at', ascending=False)
                
                display_columns = []
                if 'username' in users_df.columns:
                    display_columns.append('username')
                if 'email' in users_df.columns:
                    display_columns.append('email')
                if 'created_at' in users_df.columns:
                    display_columns.append('created_at')
                
                if display_columns:
                    st.dataframe(
                        users_df[display_columns].head(20),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'created_at': st.column_config.DatetimeColumn(
                                "Тіркелу күні",
                                format="YYYY-MM-DD HH:mm"
                            )
                        }
                    )
                else:
                    st.info("📭 Көрсетуге деректер жоқ")
            else:
                st.info("📭 Пайдаланушылар деректері жоқ")
    
    # ========== ТАБ 5: БЕЛСЕНДІЛІК ==========
    with tab5:
        st.header("⏰ Уақыт бойынша белсенділік талдауы")
        
        hourly = get_hourly_distribution()
        
        if hourly:
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart
                fig_hourly = px.bar(
                    x=list(hourly.keys()),
                    y=list(hourly.values()),
                    title="<b>Сағат бойынша сұрақтар үлестірімі</b>",
                    labels={'x': 'Сағат (24 сағат форматы)', 'y': 'Сұрақтар саны'},
                    color=list(hourly.values()),
                    color_continuous_scale='Plasma',
                    text=list(hourly.values())
                )
                fig_hourly.update_traces(
                    texttemplate='%{text}',
                    textposition='outside'
                )
                fig_hourly.update_layout(
                    height=500,
                    xaxis=dict(tickmode='linear', dtick=1)
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
            
            with col2:
                # Polar chart
                fig_polar = px.line_polar(
                    r=list(hourly.values()),
                    theta=[f"{h}:00" for h in hourly.keys()],
                    line_close=True,
                    title="<b>Сағаттық цикл</b>",
                    color_discrete_sequence=['#636efa']
                )
                fig_polar.update_traces(fill='toself')
                fig_polar.update_layout(height=500)
                st.plotly_chart(fig_polar, use_container_width=True)
            
            st.divider()
            
            # Peak және low сағаттар
            st.subheader("📊 Белсенділік көрсеткіштері")
            col1, col2, col3 = st.columns(3)
            
            peak_hour = max(hourly, key=hourly.get)
            with col1:
                st.metric("🏆 Ең белсенді сағат", f"{peak_hour}:00 - {peak_hour+1}:00", delta=hourly[peak_hour])
            
            low_hour = min(hourly, key=hourly.get)
            with col2:
                st.metric("😴 Ең төмен сағат", f"{low_hour}:00 - {low_hour+1}:00", delta=hourly[low_hour])
            
            avg_hourly = round(sum(hourly.values()) / 24, 1)
            with col3:
                st.metric("📊 Орташа сағаттық", avg_hourly)
            
        else:
            st.info("📭 Уақыт деректері жоқ")
    
    # ========== ТАБ 6: ЭКСПОРТ ==========
    with tab6:
        st.header("📥 Деректерді экспорттау және жүктеу")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👥 Пайдаланушылар")
            if st.button("CSV экспорт", key="export_users", use_container_width=True):
                if users_data:
                    df = pd.DataFrame(users_data)
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 Жүктеу",
                        csv,
                        f"users_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("Деректер жоқ")
        
        with col2:
            st.subheader("❓ Сұрақтар")
            if st.button("CSV экспорт", key="export_questions", use_container_width=True):
                if questions_data:
                    df = pd.DataFrame(questions_data)
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 Жүктеу",
                        csv,
                        f"questions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("Деректер жоқ")
        
        with col3:
            st.subheader("🗂️ Санаттар")
            if st.button("CSV экспорт", key="export_categories", use_container_width=True):
                if categories:
                    df = pd.DataFrame(list(categories.items()), columns=['Санат', 'Саны'])
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 Жүктеу",
                        csv,
                        f"categories_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("Деректер жоқ")
        
        st.divider()
        
        st.info("ℹ️ Экспортталған файлдар UTF-8 кодтауда, Excel-де ашу үшін 'Data' > 'From Text/CSV' қолданыңыз.")

if __name__ == "__main__":
    analitika_page()