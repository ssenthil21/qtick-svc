import os
from pathlib import Path
from dotenv import load_dotenv


# Resolve the absolute path to the .env file (root of the project)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

print(f"--- Environment Loading ---")
print(f"Project Root: {BASE_DIR}")
print(f"Looking for .env at: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")

# In dev, let .env provide defaults, but allow environment variables to override.
# override=False (default) preserves existing env vars in the current shell.
loaded = load_dotenv(dotenv_path=env_path, override=False)
print(f"load_dotenv result: {loaded}")

def mask_key(k):
    if not k: return "None"
    if len(k) < 8: return "****"
    return f"{k[:4]}...{k[-4:]}"

class Config:
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    APP_ENV = os.getenv("APP_ENV", "local").lower()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Gemini Key Selection
    # Many users have both GEMINI_STUDIO_API_KEY and GEMINI_API_KEY
    GEMINI_STUDIO_API_KEY = os.getenv("GEMINI_STUDIO_API_KEY")
    GEMINI_PROD_API_KEY = os.getenv("GEMINI_API_KEY")

    if APP_ENV == "local" and GEMINI_STUDIO_API_KEY:
        GEMINI_API_KEY = GEMINI_STUDIO_API_KEY
        key_source = "GEMINI_STUDIO_API_KEY (Local Mode)"
    else:
        GEMINI_API_KEY = GEMINI_PROD_API_KEY
        key_source = "GEMINI_API_KEY (Prod Mode)"

    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    
    JAVA_API_BASE_URL = os.getenv("JAVA_API_BASE_URL", "http://localhost:8080/api")
    QTICK_JAVA_SERVICE_TOKEN = os.getenv("QTICK_JAVA_SERVICE_TOKEN")
    QTICK_BIZ_PROFILE_SECRET = os.getenv("QTICK_BIZ_PROFILE_SECRET")

    # Mapping files based on profile
    if APP_ENV == "prod":
        FRANCHISE_FILE = "data/franchise_mappings_prod.json"
    elif APP_ENV == "qa":
        FRANCHISE_FILE = "data/franchise_mappings_qa.json"
    else:
        FRANCHISE_FILE = "data/franchise_mappings.json"

    # Debug logging
    print(f"--- Configuration Debug ---")
    print(f"APP_ENV: {APP_ENV}")
    print(f"FRANCHISE_FILE: {FRANCHISE_FILE}")
    print(f"LLM_PROVIDER: {LLM_PROVIDER}")
    print(f"GEMINI_MODEL: {GEMINI_MODEL}")
    print(f"Selected GEMINI_API_KEY source: {key_source}")
    print(f"Active GEMINI_API_KEY: {mask_key(GEMINI_API_KEY)}")
    print(f"JAVA_API_BASE_URL: {JAVA_API_BASE_URL}")
    print(f"QTICK_JAVA_SERVICE_TOKEN: {mask_key(QTICK_JAVA_SERVICE_TOKEN)}")
    print(f"---------------------------")

settings = Config()
