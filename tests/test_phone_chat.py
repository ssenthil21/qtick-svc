import httpx
import json
import asyncio
import sys
import io

# Force UTF-8 encoding for stdout and stderr to handle emojis on Windows terminals
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
BASE_URL = "http://localhost:8001/agent/phone/chat"

async def test_phone_chat(phone: str, prompt: str):
    print(f"\n--- Testing Phone Chat for {phone} ---")
    print(f"Prompt: {prompt}")
    
    payload = {
        "phone": phone,
        "prompt": prompt
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(BASE_URL, json=payload, timeout=60)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Response Data:")
                print(f"Type: {data.get('type')}")
                print(f"Text: {data.get('response_text')}")
                if data.get('whatsAppText'):
                    print(f"WhatsApp Text: {data.get('whatsAppText')}")
                if data.get('response_value'):
                    print(f"Value: {json.dumps(data.get('response_value'), indent=2)}")
                return data
            else:
                print("Error Response:")
                print(response.text)
                
    except httpx.ConnectError:
        print(f"Could not connect to {BASE_URL}. Is the server running on port 8001?")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    test_cases = [
        {"name": "Create Lead", "prompt": "Create a new lead named 'Enriched Test User' with email 'enriched@test.com' and phone '98765432'."},
        {"name": "Create Lead with Service", "prompt": "Create a new lead for 'user2' with phone '91944367165454' interested in 'Gents Cut'."},
        {"name": "List Leads", "prompt": "List all leads."},
        {"name": "Create Booking - Single Service", "prompt": "Book an appointment for phone '911234567890', for service Simple Facial on 2025-12-22T09:00:00.000+0000."},
        {"name": "Create Booking - Multi Service", "prompt": "Book an appointment for phone '911234567890', service Facial on 2025-12-23T14:30:00.000+0000."},
        {"name": "Get Business Summary", "prompt": "Get business summary from 2025/11/01 to 2025/11/30."},
        {"name": "Search Services", "prompt": "Search for 'facial' services."},
        {"name": "Franchise Summary", "prompt": "Get franchise summary for branches 96 and 97 for today."},
        {"name": "List Offers", "prompt": "Show me the offers."}
    ]

    PHONE_NUMBER = "6592701525"
    
    while True:
        print("\n=== Phone Chat Test Menu (Target: localhost:8001) ===")
        for i, test in enumerate(test_cases):
            print(f"{i + 1}. {test['name']}")
        print("98. Run All Tests")
        print("99. Custom Prompt")
        print("0. Exit")
        
        try:
            choice = input("\nEnter choice: ")
            if choice == "0":
                print("Exiting...")
                break
            
            if choice == "98":
                for i, test in enumerate(test_cases):
                    print(f"\n[{i+1}/{len(test_cases)}] {test['name']}")
                    await test_phone_chat(PHONE_NUMBER, test["prompt"])
                    await asyncio.sleep(2) # Brief delay
                continue

            if choice == "99":
                custom_prompt = input("Enter custom prompt: ")
                custom_phone = input(f"Enter phone number (default {PHONE_NUMBER}): ")
                if not custom_phone:
                    custom_phone = PHONE_NUMBER
                await test_phone_chat(custom_phone, custom_prompt)
                continue
                
            index = int(choice) - 1
            if 0 <= index < len(test_cases):
                test = test_cases[index]
                await test_phone_chat(PHONE_NUMBER, test["prompt"])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    asyncio.run(main())
