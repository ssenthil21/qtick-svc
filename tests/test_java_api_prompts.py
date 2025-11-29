import requests
import json
import time

BASE_URL = "http://localhost:8000/agent/chat"

def run_prompt(prompt, description):
    print(f"\n--- Test: {description} ---")
    print(f"Prompt: {prompt}")
    
    start_time = time.time()
    try:
        response = requests.post(
            BASE_URL, 
            json={"prompt": prompt},
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
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def main():
    print("Starting Java API Agent Tool Tests...")
    
    test_cases = [
        {
            "name": "Create Lead (Java API)",
            "prompt": "Create a new lead named 'Java Test User' with email 'java@test.com' and phone '98765432' for business ID 96."
        },
        {
            "name": "List Leads (Java API)",
            "prompt": "List all leads for business ID 96."
        },
        {
            "name": "Create Appointment (Java API)",
            "prompt": "Create a 'Consultation' appointment for customer 'CUST-001' with service name 'General Service' starting tomorrow at 10:00 AM for 1 hour."
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
                run_prompt(test["prompt"], test["name"])
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
