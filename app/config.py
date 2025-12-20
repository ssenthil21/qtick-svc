import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve the absolute path to the .env file (root of the project)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

print(f"--- Environment Loading ---")
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

# In dev, let .env override anything else
loaded = load_dotenv(dotenv_path=env_path, override=True)
print(f"load_dotenv result: {loaded}")
print(f"---------------------------")

class Config:
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # openai or gemini
    APP_ENV = os.getenv("APP_ENV", "local").lower()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Gemini Key Selection
    GEMINI_STUDIO_API_KEY = os.getenv("GEMINI_STUDIO_API_KEY")
    GEMINI_PROD_API_KEY = os.getenv("GEMINI_API_KEY")

    if APP_ENV == "local" and GEMINI_STUDIO_API_KEY:
        GEMINI_API_KEY = GEMINI_STUDIO_API_KEY
    else:
        GEMINI_API_KEY = GEMINI_PROD_API_KEY

    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    
    # Debug logging (safe)
    print(f"--- Configuration Debug ---")
    print(f"APP_ENV: {APP_ENV}")
    print(f"LLM_PROVIDER: {LLM_PROVIDER}")
    print(f"GEMINI_MODEL: {GEMINI_MODEL}")
    
    def mask_key(k):
        if not k: return "None"
        if len(k) < 8: return "****"
        return f"{k[:4]}...{k[-4:]}"

    print(f"GEMINI_STUDIO_API_KEY (loaded): {mask_key(GEMINI_STUDIO_API_KEY)}")
    print(f"GEMINI_API_KEY (from GEMINI_API_KEY env): {mask_key(os.getenv('GEMINI_API_KEY'))}")
    print(f"Active GEMINI_API_KEY (selected): {mask_key(GEMINI_API_KEY)}")
    print(f"---------------------------")

    JAVA_API_BASE_URL = os.getenv("JAVA_API_BASE_URL", "http://localhost:8080/api")
    QTICK_JAVA_SERVICE_TOKEN = os.getenv("QTICK_JAVA_SERVICE_TOKEN")

settings = Config()
