import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch

# Ensure app is in path
sys.path.append(os.getcwd())
# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

import pytest
from httpx import Response
from app.services.java_service import JavaService
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient

# Mock data
MOCK_PHONE = "6592701525"
MOCK_BIZ_ID = 119
MOCK_RESPONSE_DATA = [
    {
        "bizId": MOCK_BIZ_ID, 
        "operId": 26013001, 
        "name": "SRJ Beauty Salon"
    }
]

@pytest.mark.asyncio
async def test_get_my_queues_service_call():
    print("\n--- Testing JavaService.get_my_queues ---")
    
    with patch("app.services.java_service.httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Response(200, json=MOCK_RESPONSE_DATA)
        
        service = JavaService()
        biz_id = await service.get_my_queues(MOCK_PHONE)
        
        print(f"Call Result: {biz_id}")
        assert biz_id == MOCK_BIZ_ID
        
        # Verify Headers
        call_args = mock_get.call_args
        headers = call_args.kwargs.get("headers", {})
        print(f"Headers sent: {headers}")
        
        assert headers.get("X-ClientId") == MOCK_PHONE
        if settings.QTICK_BIZ_PROFILE_SECRET:
            assert headers.get("Authorization") == settings.QTICK_BIZ_PROFILE_SECRET
            print("Authorization header verified.")
        else:
            print("WARNING: QTICK_BIZ_PROFILE_SECRET not set in environment!")

def test_phone_chat_endpoint():
    print("\n--- Testing /agent/phone/chat Endpoint ---")
    
    with patch("app.services.java_service.JavaService.get_my_queues", new_callable=AsyncMock) as mock_lookup:
        mock_lookup.return_value = MOCK_BIZ_ID
        
        # Mock the agent process to avoid real LLM calls
        with patch("app.agent.Agent.process_prompt", new_callable=AsyncMock) as mock_agent:
            mock_agent.return_value = {
                "type": "Chat",
                "response_text": "Hello from Mock Agent",
                "whatsAppText": "Hello"
            }
            
            client = TestClient(app)
            
            # Payload without Authorization header
            payload = {
                "phone": MOCK_PHONE,
                "prompt": "Hi"
            }
            
            response = client.post("/agent/phone/chat", json=payload)
            print(f"Endpoint Response Status: {response.status_code}")
            print(f"Endpoint Response Body: {response.json()}")
            
            assert response.status_code == 200
            assert response.json()["response_text"] == "Hello from Mock Agent"
            
            # Verify lookup was called
            mock_lookup.assert_called_once_with(MOCK_PHONE)
            print("Business Lookup verified.")

if __name__ == "__main__":
    # We run pytest via code to inspect output easily
    sys.exit(pytest.main(["-s", __file__]))
