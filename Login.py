import streamlit as st
import hashlib
from config import get_supabase_client

# -----------------------------
# 🔐 Құпия сөзді хэштеу
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# 🎄 Жаңа жылдық баннер
# -----------------------------

# -----------------------------
# 🚪 Кіру беті
# -----------------------------
def login_page():

    st.write(" ")
    st.subheader("🔐 Жүйеге кіру немесе тіркелу")

    tab_login, tab_register = st.tabs(["🎁 Кіру", "🎉 Тіркелу"])

    # -------------------------
    # 🎁 КІРУ
    # -------------------------
    with tab_login:
        with st.form("login_form"):
            st.markdown("#### 🔑 Кіру мәліметтері")
            username = st.text_input("👤 Пайдаланушы аты")
            password = st.text_input("🔒 Құпия сөз", type="password")
            submit = st.form_submit_button("➡️ Кіру")

            if submit:
                if username and password:
                    supabase = get_supabase_client()
                    hashed_pw = hash_password(password)

                    try:
                        response = (
                            supabase.table("users")
                            .select("*")
                            .eq("username", username)
                            .eq("password", hashed_pw)
                            .execute()
                        )

                        if response.data:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.user_id = response.data[0]["id"]
                            st.session_state.is_admin = False

                            st.success("🎉 Сәтті кірдіңіз! Қош келдіңіз!")
                            st.rerun()
                        else:
                            st.error("❌ Пайдаланушы аты немесе құпия сөз қате!")
                    except Exception as e:
                        st.error(f"⚠️ Қате орын алды: {str(e)}")
                else:
                    st.warning("⚠️ Барлық өрістерді толтырыңыз!")

    # -------------------------
    # 🎉 ТІРКЕЛУ
    # -------------------------
    with tab_register:
        with st.form("register_form"):
            st.markdown("#### 📝 Жаңа аккаунт құру")
            new_username = st.text_input("👤 Пайдаланушы аты")
            new_email = st.text_input("📨 Email")
            new_password = st.text_input("🔒 Құпия сөз", type="password")
            confirm_password = st.text_input("🔁 Құпия сөзді растау", type="password")
            submit_register = st.form_submit_button("🎉 Тіркелу")

            if submit_register:
                if new_username and new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Құпия сөздер сәйкес келмейді!")
                    else:
                        supabase = get_supabase_client()
                        hashed_pw = hash_password(new_password)

                        try:
                            existing = (
                                supabase.table("users")
                                .select("*")
                                .eq("username", new_username)
                                .execute()
                            )

                            if existing.data:
                                st.error("⚠️ Бұл пайдаланушы аты бұрын алынған!")
                            else:
                                supabase.table("users").insert({
                                    "username": new_username,
                                    "email": new_email,
                                    "password": hashed_pw
                                }).execute()

                                st.success("🎄 Тіркелу сәтті өтті! Енді жүйеге кіре аласыз 🎅")
                        except Exception as e:
                            st.error(f"⚠️ Қате орын алды: {str(e)}")
                else:
                    st.warning("⚠️ Барлық өрістерді толтырыңыз!")

# -----------------------------
# ✔️ Кіру статусын тексеру
# -----------------------------
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        return False

    return True
