BEGIN;

-- =========================================================
-- 1) USERS
-- =========================================================
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Бар база үшін қауіпсіз толықтырулар
ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- =========================================================
-- 2) QUESTIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS public.questions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    username TEXT, -- Analitika.py үшін керек
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('medical', 'medication', 'psychology', 'other')),
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_answered BOOLEAN NOT NULL DEFAULT TRUE,
    answer_quality INTEGER CHECK (answer_quality BETWEEN 1 AND 5)
);

ALTER TABLE public.questions
    ADD COLUMN IF NOT EXISTS username TEXT,
    ADD COLUMN IF NOT EXISTS is_answered BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS answer_quality INTEGER;

-- category/answer_quality check-тері жоқ болса қосамыз
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'questions_category_check'
    ) THEN
        ALTER TABLE public.questions
        ADD CONSTRAINT questions_category_check
        CHECK (category IN ('medical', 'medication', 'psychology', 'other'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'questions_answer_quality_check'
    ) THEN
        ALTER TABLE public.questions
        ADD CONSTRAINT questions_answer_quality_check
        CHECK (answer_quality BETWEEN 1 AND 5 OR answer_quality IS NULL);
    END IF;
END $$;

-- user_id берілсе username автоматты толтыру (Analitika үшін пайдалы)
CREATE OR REPLACE FUNCTION public.fill_question_username()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.username IS NULL AND NEW.user_id IS NOT NULL THEN
        SELECT u.username INTO NEW.username
        FROM public.users u
        WHERE u.id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_fill_question_username ON public.questions;
CREATE TRIGGER trg_fill_question_username
BEFORE INSERT OR UPDATE OF user_id, username
ON public.questions
FOR EACH ROW
EXECUTE FUNCTION public.fill_question_username();

-- =========================================================
-- 3) FEEDBACK
-- =========================================================
CREATE TABLE IF NOT EXISTS public.feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    username TEXT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    suggestions TEXT,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER TABLE public.feedback
    ADD COLUMN IF NOT EXISTS is_reviewed BOOLEAN NOT NULL DEFAULT FALSE;

-- =========================================================
-- 4) INDEXES
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_questions_user_id ON public.questions(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_username ON public.questions(username);
CREATE INDEX IF NOT EXISTS idx_questions_category ON public.questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_timestamp ON public.questions("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_questions_user_time ON public.questions(user_id, "timestamp" DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON public.feedback("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON public.feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON public.feedback(user_id);

-- =========================================================
-- 5) RLS (осы жоба логикасына сай: өшіреміз)
-- =========================================================
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_select_own ON public.users;
DROP POLICY IF EXISTS questions_select_own ON public.questions;
DROP POLICY IF EXISTS questions_insert_own ON public.questions;
DROP POLICY IF EXISTS feedback_select_all ON public.feedback;
DROP POLICY IF EXISTS feedback_insert_own ON public.feedback;

-- =========================================================
-- 6) Аналитика view
-- =========================================================
CREATE OR REPLACE VIEW public.statistics_overview AS
SELECT
    (SELECT COUNT(*) FROM public.users) AS total_users,
    (SELECT COUNT(*) FROM public.questions) AS total_questions,
    (SELECT COUNT(*) FROM public.feedback) AS total_feedback,
    (SELECT ROUND(AVG(rating)::numeric, 2) FROM public.feedback) AS avg_rating,
    (SELECT COUNT(*) FROM public.questions WHERE DATE("timestamp") = CURRENT_DATE) AS questions_today,
    (SELECT COUNT(*) FROM public.users WHERE DATE(created_at) = CURRENT_DATE) AS new_users_today;

COMMIT;
