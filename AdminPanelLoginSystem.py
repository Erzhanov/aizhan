import streamlit as st
from config import ADMIN_USERNAME, ADMIN_PASSWORD

def admin_login_page():
    st.title("🔐 Админ панеліне кіру")
    
    with st.form("admin_login_form"):
        admin_user = st.text_input("Админ логині")
        admin_pass = st.text_input("Админ құпия сөзі", type="password")
        submit = st.form_submit_button("Кіру")
        
        if submit:
            if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.username = "Admin"
                st.success("Админ ретінде кірдіңіз!")
                st.rerun()
            else:
                st.error("Логин немесе құпия сөз қате!")

def check_admin():
    return st.session_state.get('is_admin', False)
