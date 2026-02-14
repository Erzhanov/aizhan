import streamlit as st
import hashlib
from config import get_supabase_client

# -----------------------------
# 🔐 Құпия сөзді хэштеу
# -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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
            login_value = st.text_input("👤 Пайдаланушы аты немесе Email")  # ✅ өзгерді
            password = st.text_input("🔒 Құпия сөз", type="password")
            submit = st.form_submit_button("➡️ Кіру")

            if submit:
                if login_value and password:
                    supabase = get_supabase_client()
                    hashed_pw = hash_password(password)

                    try:
                        # ✅ username OR email арқылы іздеу
                        response = (
                            supabase.table("users")
                            .select("*")
                            .or_(f"username.eq.{login_value},email.eq.{login_value}")
                            .eq("password", hashed_pw)
                            .limit(1)
                            .execute()
                        )

                        if response.data:
                            user = response.data[0]

                            st.session_state.logged_in = True
                            st.session_state.username = user["username"]      # ✅ нақты username сақтаймыз
                            st.session_state.user_id = user["id"]
                            st.session_state.is_admin = bool(user.get("is_admin", False))  # егер баған бар болса

                            st.success("🎉 Сәтті кірдіңіз! Қош келдіңіз!")
                            st.rerun()
                        else:
                            st.error("❌ Логин (username/email) немесе құпия сөз қате!")
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
                            # ✅ username немесе email бұрын бар ма тексеру
                            existing = (
                                supabase.table("users")
                                .select("id")
                                .or_(f"username.eq.{new_username},email.eq.{new_email}")
                                .limit(1)
                                .execute()
                            )

                            if existing.data:
                                st.error("⚠️ Бұл username немесе email бұрын тіркелген!")
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
