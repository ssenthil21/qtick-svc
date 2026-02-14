import sys
import os
import asyncio
import json
from unittest.mock import AsyncMock, patch

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

# External URL
API_URL = "http://localhost:8001/agent/phone/chat"

def safe_print(text, end="\n", flush=False):
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Fallback for Windows consoles with limited character sets
        if sys.stdout.encoding:
            encoded = text.encode(sys.stdout.encoding, errors='replace')
            print(encoded.decode(sys.stdout.encoding), end=end, flush=flush)
        else:
            print(text.encode('ascii', errors='replace').decode('ascii'), end=end, flush=flush)

async def interactive_chat():
    import argparse
    parser = argparse.ArgumentParser(description="QTick Interactive Chat")
    parser.add_argument("--phone", type=str, default="6592701525", help="Phone number to simulate")
    args = parser.parse_args()

    PHONE_NUMBER = args.phone
    
    safe_print("----------------------------------------------------------------")
    safe_print("QTick Interactive Console (Phone Chat Mode)")
    safe_print("----------------------------------------------------------------")
    safe_print(f"Simulating Phone: {PHONE_NUMBER}")
    safe_print("Type '1', 'menu', 'exit', or any natural language query.")
    safe_print("----------------------------------------------------------------")

    # Mock the JavaService to return a dummy ID if lookup fails, 
    # but we want to allow it to TRY real lookup if possible? 
    # Actually, the user environment seems to have real keys. 
    # Let's NOT mock get_my_queues strongly if we want real data, 
    # BUT the previous tests required mocking. 
    # Let's stick to mocking a success for now to ensure we get to the Agent.
    
    # We won't mock internal services since we are calling an external URL
    # with patch("app.services.java_service.JavaService.get_my_queues", new_callable=AsyncMock) as mock_get_queues:
        # mock_get_queues.return_value = "119"
        
    async with httpx.AsyncClient() as client:
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit"]:
                    safe_print("Exiting...")
                    break
                
                # Make the request
                safe_print("Thinking...", end="", flush=True)
                try:
                    response = await client.post(API_URL, json={"phone": PHONE_NUMBER, "prompt": user_input}, timeout=60.0)
                except Exception as e:
                    safe_print(f"\nRequest Failed: {e}")
                    continue
                safe_print("\r", end="") # Clear "Thinking..."
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Decode JSON-escaped WhatsApp text
                    try:
                        wa_text = json.loads(f'"{data["whatsAppText"]}"')
                    except:
                        wa_text = data["whatsAppText"]
                        
                    safe_print(f"Bot:\n{wa_text}")
                    
                    # If there's a response value (like data), maybe print summary
                    # if data.get("response_value"):
                    #     print(f"[Debug Data]: {str(data['response_value'])[:100]}...")
                else:
                    safe_print(f"Error {response.status_code}: {response.text}")

            except KeyboardInterrupt:
                safe_print("\nExiting...")
                break
            except Exception as e:
                safe_print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_chat())
