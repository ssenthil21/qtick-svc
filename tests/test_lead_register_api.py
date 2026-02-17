import requests
import json
import sys

# Testing against local running instance
BASE_URL = "http://localhost:8001/lead/register"

def test_lead_register_success():
    print(f"\n--- Testing Lead Registration API at {BASE_URL} ---")
    
    payload = {
        "business_id": 119,  # Using a known valid business ID from other tests (e.g. 96 or 119)
        "owner_name": "119 User",
        "mobile_number": "919876543210",
        "salon_name": "119 Salon",
        "city": "Chennai",
        "plan": "Premium Plan",
        "x_client_id": "6592701525",
        "campId": 779,
        "campName": "QTICK-ABCEXPO"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Lead registered.")
            print(f"Lead ID: {data.get('lead_id')}")
        else:
            print("[FAILED] Request failed!")
            
    except Exception as e:
        print(f"[ERROR] Error connecting to server: {e}")
        print("Make sure the server is running on port 8001.")

if __name__ == "__main__":
    test_lead_register_success()
