import pytest
import asyncio
from app.tools.leads import create_lead, list_leads
from app.models import ToolResult, LeadCreateResponse, LeadSummary, LeadCreateRequest
from app.config import settings
import json

# Force mock mode for testing
settings.USE_MOCK_DATA = True

@pytest.mark.asyncio
async def test_create_lead_lead_value(mocker):
    # We need to ensure we use the same service or mock the service return
    from app.services.mock_service import MockService
    mock_service = MockService()
    mocker.patch("app.tools.leads.get_service", return_value=mock_service)

    # Test lead creation
    result: ToolResult = await create_lead(
        name="Test Lead",
        business_id=123,
        prompt="Interested in product",
        token="mock-token"
    )
    
    assert result.type == "create_lead"
    # Check if the text response contains the value
    assert "Value: 0.0" in result.text
    # In MockService, it's hardcoded to 0.0 for now, but we check if the field exists
    assert result.data.leadValue == 0.0
    
    # Check WhatsApp formatting (handle escaped JSON characters)
    assert "*Potential Value:*" in result.whatsAppText
    assert "0.00" in result.whatsAppText

@pytest.mark.asyncio
async def test_list_leads_enhanced_presentation(mocker):
    from app.services.mock_service import MockService
    mock_service = MockService()
    mocker.patch("app.tools.leads.get_service", return_value=mock_service)

    # Create multiple leads with different values in MockService
    # Note: MockService create_lead currently hardcodes value to 0.0
    # Let's mock create_lead or manually append to mock_service.leads if it were accessible
    # Better: Patch MockService.list_leads to return specific data
    from app.models import LeadListResponse, LeadSummary
    mock_data = LeadListResponse(
        total=3,
        items=[
            LeadSummary(lead_id="1", name="Low Value", status="new", created_at="now", leadValue=100.0),
            LeadSummary(lead_id="2", name="High Value", status="new", created_at="now", leadValue=1000.0),
            LeadSummary(lead_id="3", name="Mid Value", status="new", created_at="now", leadValue=500.0),
        ]
    )
    mocker.patch.object(mock_service, 'list_leads', return_value=mock_data)
    
    result: ToolResult = await list_leads(business_id=123, token="mock-token")
    
    assert result.type == "list_leads"
    # Check total value calculation (100 + 1000 + 500 = 1600)
    assert "Total Potential Value: ₹1,600.00" in result.text
    
    # Check WhatsApp formatting for total value (handle escaping)
    assert "Total Potential Value:" in result.whatsAppText
    assert "1,600.00" in result.whatsAppText
    
    # Check sorting in WhatsApp text (Top 5 list)
    assert "1. *High Value*" in result.whatsAppText
    assert "2. *Mid Value*" in result.whatsAppText
    assert "3. *Low Value*" in result.whatsAppText
    assert "1,000.00" in result.whatsAppText
    assert "500.00" in result.whatsAppText
    assert "100.00" in result.whatsAppText

if __name__ == "__main__":
    asyncio.run(test_create_lead_lead_value())
    asyncio.run(test_list_leads_lead_value())
