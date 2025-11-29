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
        print(f"Response ({duration:.2f}s):")
        print(data["response"])
        return data["response"]
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def main():
    print("Starting Agent Tool Tests...")
    
    test_cases = [
        {
            "name": "Create Lead",
            "prompt": "Create a new lead named 'Sarah Connor' with email 'sarah@skynet.com' and phone '555-0199' for business ID 96."
        },
        {
            "name": "List Leads",
            "prompt": "List all leads for business ID 123."
        },
        {
            "name": "Create Appointment",
            "prompt": "Create a 'Termination Meeting' appointment for customer 'CUST-001' with service name 'Legal Consultation' starting tomorrow at 10:00 AM for 1 hour."
        },
        {
            "name": "List Appointments",
            "prompt": "List all appointments."
        },
        {
            "name": "Create Invoice",
            "prompt": "Create an invoice for business 'BIZ-001' and customer 'sarah@skynet.com' (find the lead ID first) for amount 500.00 with item 'Consultation'."
        },
        {
            "name": "List Invoices",
            "prompt": "List all invoices."
        },
        {
            "name": "Get Business Summary",
            "prompt": "Get the business summary for business ID 'BIZ-001'."
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
