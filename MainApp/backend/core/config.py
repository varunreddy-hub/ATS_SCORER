import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

APP_TITLE = "ATS RESUME ANALYZER API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Analyze resumes against job descriptions using NLP + ML"

ALLOWED_ORIGINS = [
    "https://atsscorer-k9xrzsqzqqkuvtgph4wiqp.streamlit.app"
]



MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx"
}


SPACY_MODEL_PRIMARY = "en_core_web_sm"
SPACY_MODEL_SECONDARY = "en_core_web_sm"


SENTENCE_TRANSFORMER_MODEL = os.getenv(
    "SENTENCE_TRANSFORMER_MODEL",
    "all-MiniLM-L6-v2"
)

SCORE_WEIGHTS = {
    "formatting": 20,
    "keywords": 25,
    "content": 25,
    "skill_validation": 15,
    "ats_compatibility": 15,
}

JD_KEYWORD_WEIGHT = 0.6
JD_SEMANTIC_WEIGHT = 0.4



GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")