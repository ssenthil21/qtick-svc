import httpx
import json

# Configuration
# BASE_URL = "https://qtick-svc-du97k.ondigitalocean.app/website/chat"
BASE_URL = "http://localhost:8010/website/chat"

def test_chat(message: str, history: list = []):
    print(f"\n--- Sending Message: '{message}' ---")
    
    payload = {
        "message": message,
        "history": history
    }
    
    try:
        response = httpx.post(BASE_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("Response Status:", response.status_code)
        print("Response Text:", data.get("response_text"))
        if data.get("action"):
            print("Action Triggered:", data.get("action"))
            
        return data
        
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        print(exc.response.text)
    except Exception as exc:
        print(f"An error occurred: {exc}")

if __name__ == "__main__":
    # Test Case 1: General Question (RAG)
    print("Test Case 1: Asking about features (RAG)")
    history = []
    response1 = test_chat("What is QTick?", history)
    
    if response1:
        # Add to history for next turn
        history.append({"role": "user", "content": "What is QTick?"})
        history.append({"role": "model", "content": response1.get("response_text")})

    # Test Case 2: Specific Feature
    print("\nTest Case 2: Asking about specific feature")
    response2 = test_chat("Tell me about the queuing system", history)
    
    if response2:
        history.append({"role": "user", "content": "Tell me about the queuing system"})
        history.append({"role": "model", "content": response2.get("response_text")})

    # Test Case 3: Lead Capture
    print("\nTest Case 3: Providing contact details (Lead Capture)")
    test_chat("That sounds great. My name is Alice and my number is 9876543210. I'm interested in the loyalty program.", history)
