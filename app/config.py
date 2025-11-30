import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower() # openai or gemini
    APP_ENV = os.getenv("APP_ENV", "local").lower()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Gemini Key Selection
    GEMINI_STUDIO_API_KEY = os.getenv("GEMINI_STUDIO_API_KEY")
    GEMINI_PROD_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if APP_ENV == "local" and GEMINI_STUDIO_API_KEY:
        GEMINI_API_KEY = GEMINI_STUDIO_API_KEY
    else:
        GEMINI_API_KEY = GEMINI_PROD_API_KEY
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    JAVA_API_BASE_URL = os.getenv("JAVA_API_BASE_URL", "http://localhost:8080/api")
    QTICK_JAVA_SERVICE_TOKEN = os.getenv("QTICK_JAVA_SERVICE_TOKEN")

settings = Config()
