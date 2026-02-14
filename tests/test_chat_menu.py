import sys
import os
# Add project root to sys.path (parent of tests directory)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app, CHAT_MENU

client = TestClient(app)

@pytest.mark.asyncio
async def test_chat_menu_command():
    # Mock JavaService to return a business ID so we get past the check
    with patch("app.services.java_service.JavaService.get_my_queues", new_callable=AsyncMock) as mock_get_queues:
        mock_get_queues.return_value = "119"
        
        response = client.post("/agent/phone/chat", json={"phone": "1234567890", "prompt": "menu"})
        
        import json
        
        assert response.status_code == 200
        data = response.json()
        
        # whatsAppText is a JSON-escaped string slice (inner content of a JSON string)
        # To decode it, we wrap it in quotes and load it
        decoded_text = json.loads(f'"{data["whatsAppText"]}"')
        
        assert "Chat Shortcuts" in decoded_text
        assert "1. 📊 Branch Summary" in decoded_text
        # Ensure agent was NOT called
        # We can't easily check agent calls with TestClient this way without patching agent, but the response content proves it intercepted.

@pytest.mark.asyncio
async def test_chat_shortcut_translation():
    # Mock JavaService
    with patch("app.services.java_service.JavaService.get_my_queues", new_callable=AsyncMock) as mock_get_queues:
        mock_get_queues.return_value = "119"
        
        # Mock Agent.process_prompt to check what it receives
        with patch("app.agent.Agent.process_prompt", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "type": "Chat",
                "response_text": "Mock response",
                "whatsAppText": "Mock WA"
            }
            
            # Send "1"
            client.post("/agent/phone/chat", json={"phone": "1234567890", "prompt": "1"})
            
            # Verify agent was called with the translated text
            expected_prompt = CHAT_MENU["1"]
            mock_process.assert_called_once()
            args, _ = mock_process.call_args
            assert args[0] == expected_prompt  # The first argument to process_prompt is prompt

if __name__ == "__main__":
    # Manually run async tests if pytest not available in environment
    import asyncio
    
    async def run_tests():
        print("Running test_chat_menu_command...")
        await test_chat_menu_command()
        print("PASS")
        
        print("Running test_chat_shortcut_translation...")
        await test_chat_shortcut_translation()
        print("PASS")
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_tests())
