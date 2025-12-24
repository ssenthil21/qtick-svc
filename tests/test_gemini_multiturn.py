import asyncio
import os
import logging
from app.agent import Agent
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_multiturn_flow():
    print("\n--- Testing Multi-Turn Gemini Flow ---")
    print("Prompt: 'tomorrow create a simple facial service for Jessica phone number 9443 671 677'")
    
    # Ensure we use mock data so we don't hit real APIs, but the agent still runs through tools
    os.environ["USE_MOCK_DATA"] = "true"
    settings.USE_MOCK_DATA = True
    
    agent = Agent()
    business_id = 96
    prompt = "tomorrow create a simple facial service for Jessica phone number 9443 671 677"
    
    try:
        response = await agent.process_prompt(prompt, business_id)
        print("\nFinal Agent Response:")
        print(f"Type: {response.get('type')}")
        print(f"Text: {response.get('response_text')}")
        
        # Check if the text sounds like an appointment was created
        if "Appointment created successfully" in response.get("response_text"):
            print("\nSUCCESS: Multi-turn flow completed correctly!")
        else:
            print("\nFAILURE: Flow did not complete as expected.")
            
    except Exception as e:
        print(f"\nError during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_multiturn_flow())
