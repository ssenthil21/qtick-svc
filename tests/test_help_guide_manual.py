import requests
import json
import sys
import io

# Force UTF-8 for Windows terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8001/agent/phone/chat"

def test_greeting():
    print("\n--- Testing Greeting: 'Hi' ---")
    payload = {
        "prompt": "Hi",
        "phone": "6592701525"
    }
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Type: {data.get('type')}")
    print(f"Text: {data.get('response_text')}")
    print(f"WhatsApp Text: {data.get('whatsAppText')}")

def test_guide_me():
    print("\n--- Testing Help Request: 'guide me' ---")
    payload = {
        "prompt": "guide me",
        "phone": "6592701525"
    }
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Type: {data.get('type')}")
    print(f"Text: {data.get('response_text')}")

if __name__ == "__main__":
    try:
        test_greeting()
        test_guide_me()
    except Exception as e:
        print(f"Error: {e}")
