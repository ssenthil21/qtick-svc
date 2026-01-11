import asyncio
import httpx
import json

async def test_business_summary():
    url = "http://localhost:8001/agent/chat"
    payload = {
        "prompt": "Get summary for business from 2025/11/01 to 2025/11/30",
        "business_id": 96
    }
    
    print(f"Testing {url} with prompt: {payload['prompt']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print("Response received successfully!")
                print(f"Type: {data.get('type')}")
                
                # Check for whatsAppText
                whatsapp_text = data.get("whatsAppText")
                if whatsapp_text:
                    print("SUCCESS: whatsAppText found in response!")
                else:
                    print("FAILURE: whatsAppText NOT found in response.")
                
                # Check for revenue mapping
                val = data.get("response_value")
                if val:
                    revenue = val.get("total_revenue")
                    leads = val.get("total_leads")
                    print(f"Data - Leads: {leads}, Revenue: {revenue}")
            else:
                print(f"Error: {response.status_code}")
                
    except Exception as e:
        print(f"Expection occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_business_summary())
