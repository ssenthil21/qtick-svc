
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from app.models import LeadCreateRequest, LeadCreateResponse, ToolResult
from app.tools import leads

class TestLeadsEnqFor(unittest.IsolatedAsyncioTestCase):
    async def test_create_lead_enq_for_default(self):
        # Mock get_service
        with patch('app.tools.leads.get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            
            # Setup mock response
            mock_service.create_lead = MagicMock()
            mock_service.create_lead.return_value = asyncio.Future()
            mock_service.create_lead.return_value.set_result(
                LeadCreateResponse(lead_id="ENQ123", status="NEW", created_at="2025-12-20", next_action="Followup")
            )
            
            # Test Case 1: enquiry_for IS provided
            await leads.create_lead(
                name="user1", 
                business_id=96, 
                enquiry_for="Specific Service",
                prompt="I want a service"
            )
            args, kwargs = mock_service.create_lead.call_args
            request = args[0]
            print(f"Test 1 - enqFor: {request.enquiry_for}")
            self.assertEqual(request.enquiry_for, "Specific Service")
            
            # Test Case 2: enquiry_for IS NOT provided
            await leads.create_lead(
                name="user2", 
                business_id=96, 
                prompt="I am interested in a style cut"
            )
            args, kwargs = mock_service.create_lead.call_args
            request = args[0]
            print(f"Test 2 - enqFor from prompt: {request.enquiry_for}")
            self.assertEqual(request.enquiry_for, "I am interested in a style cut")
            
            # Test Case 3: service_name IS provided, enquiry_for IS NOT
            await leads.create_lead(
                name="user3", 
                business_id=96, 
                service_name="Style Cut",
                prompt="I want a style cut"
            )
            args, kwargs = mock_service.create_lead.call_args
            request = args[0]
            print(f"Test 3 - enqFor from service_name: {request.enquiry_for}")
            self.assertEqual(request.enquiry_for, "Style Cut")

if __name__ == "__main__":
    unittest.main()
