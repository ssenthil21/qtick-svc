import requests
import json
import time

#BASE_URL = "http://localhost:8001/agent/chat"
BASE_URL = "https://qtick-svc-du97k.ondigitalocean.app/agent/chat"

def run_prompt(prompt, business_id, description):
    print(f"\n--- Test: {description} ---")
    print(f"Prompt: {prompt}")
    print(f"Business ID: {business_id}")
    
    start_time = time.time()
    try:
        response = requests.post(
            BASE_URL, 
            json={
                "prompt": prompt,
                "business_id": business_id
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        
        duration = time.time() - start_time
        print(data)
        duration = time.time() - start_time
        print(f"Response ({duration:.2f}s):")
        # Handle new structured response
        if "response_text" in data:
            print(f"Type: {data.get('type')}")
            print(f"Text: {data.get('response_text')}")
            print(f"Value: {json.dumps(data.get('response_value'), indent=2)}")
            return data.get("response_text")
        else:
            # Fallback for old structure (shouldn't happen if server updated)
            print(data.get("response"))
            return data.get("response")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")
        return None

def main():
    print("Starting Java API Agent Tool Tests...")
    
    test_cases = [
        {
            "name": "Create Lead (Java API)",
            "prompt": "Create a new lead named 'Enriched Test User' with email 'enriched@test.com' and phone '98765432' for business ID 96.",
            "business_id": 96
        },
        {
            "name": "Create Lead with Service (Java API)",
            "prompt": "Create a new lead for 'user2' with phone '91944367165454' interested in 'Gents Cut' at business 96.",
            "business_id": 96
        },
        {
            "name": "List Leads (Java API)",
            "prompt": "List all leads for business ID 96.",
            "business_id": 96
        },
        {
            "name": "Create Booking - Single Service (Java API)",
            "prompt": "Book an appointment for business ID 96, phone '911234567890', for service Simple Facial on 2025-12-22T09:00:00.000+0000.",
            "business_id": 96
        },
        {
            "name": "Create Booking - Multi Service (Java API)",
            "prompt": "Book an appointment for phone '911234567890', service Facial on 2025-12-23T14:30:00.000+0000.",
            "business_id": 96
        },
        {
            "name": "Get Business Summary (Java API)",
            "prompt": "Get business summary for business ID 96 from 2025/11/01 to 2025/11/30.",
            "business_id": 96
        },
        {
            "name": "Search Services (Java API)",
            "prompt": "Search for 'facial' services for business ID 119.",
            "business_id": 119
        }
    ]
    
    while True:
        print("\nAvailable Test Cases:")
        for i, test in enumerate(test_cases):
            print(f"{i + 1}. {test['name']}")
        print("0. Exit")
        
        try:
            choice = input("\nEnter test case number: ")
            if choice == "0":
                print("Exiting...")
                break
                
            index = int(choice) - 1
            if 0 <= index < len(test_cases):
                test = test_cases[index]
                run_prompt(test["prompt"], test.get("business_id", 96), test["name"])
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
