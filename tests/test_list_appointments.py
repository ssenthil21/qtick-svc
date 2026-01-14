import pytest
from app.tools.appointments import list_appointments
from app.models import ToolResult, AppointmentSummary
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_list_appointments_integration(mocker):
    # Mock JavaService
    mock_svc = AsyncMock()
    
    # Mock data return
    mock_data = [
        AppointmentSummary(
            booking_id="12345",
            customer_name="John Doe",
            service_name="Hair Cut",
            start_time="2026-01-14T10:00:00.000+0000",
            status="BO",
            phone="1234567890"
        ),
         AppointmentSummary(
            booking_id="67890",
            customer_name="Jane Smith",
            service_name="Facial",
            start_time="2026-01-14T14:30:00.000+0000",
            status="PE",
            phone="0987654321"
        )
    ]
    mock_svc.list_appointments.return_value = mock_data
    
    with patch("app.tools.appointments.get_service", return_value=mock_svc):
        # 1. Test "today"
        result = await list_appointments(business_id=123, period="today")
        
        # Verify service called with correct args (we can't easily check date string values without mocking datetime, but we check flow)
        assert mock_svc.list_appointments.called
        assert len(result.data) == 2
        
        # Verify Text Format
        assert "John Doe" in result.text
        assert "Hair Cut" in result.text
        assert "10:00 AM" in result.text
        
        # Verify WhatsApp Format (decode the escaped string first)
        import json
        decoded_wa = json.loads(f'"{result.whatsAppText}"')
        assert "📅 *Appointments (2)*" in decoded_wa
        assert "👤 John Doe" in decoded_wa
        assert "💇 Hair Cut" in decoded_wa
        assert "🕒" in decoded_wa

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_list_appointments_integration(None))
        print("Test Passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Test Failed: {e}")
