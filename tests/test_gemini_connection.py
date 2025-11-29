import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file or environment variables.")
    print("Please add GEMINI_API_KEY=your_key_here to your .env file.")
    exit(1)

print(f"Using API Key: {api_key[:4]}...{api_key[-4:]}")

# Configure Gemini
genai.configure(api_key=api_key)

# Use the model from env or default to gemini-1.5-flash as requested
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
print(f"Using Model: {model_name}")

try:
    model = genai.GenerativeModel(model_name)
    print("\nSending request: 'Hello world'...")
    response = model.generate_content("Hello world")
    print("\nResponse received:")
    print(response.text)
    print("\nSUCCESS: API Key is valid and working.")
except Exception as e:
    print(f"\nERROR: Failed to connect to Gemini API.")
    print(f"Details: {e}")
