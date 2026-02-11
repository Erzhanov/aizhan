import os
from supabase import create_client, Client
from dotenv import load_dotenv

# .env файлын жүктеу
load_dotenv()

# Supabase конфигурациясы
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# OpenAI API конфигурациясы
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Hugging Face конфигурациясы
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Админ тіркелгі мәліметтері
ADMIN_USERNAME = "1"
ADMIN_PASSWORD = "1"

# Supabase клиенті
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ SUPABASE_URL немесе SUPABASE_KEY .env ішінен жүктелмеді!")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Google Form сілтемесі
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd57kyirolWpwdFfHjNgsCm2DYLe_eDFITi3yo8PpbVFRoOCg/viewform?usp=publish-editor"
