import pytest
from app.tools.appointments import create_appointment
from app.models import ToolResult, BookingResponse
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_create_appointment_wa(mocker):
    # Mock JavaService
    mock_svc = AsyncMock()
    
    # Mock data return
    mock_response = BookingResponse(
        bookingId=9999,
        date="2026-02-14",
        time="10:30 AM",
        custName="Alice Wonderland",
        bizInfo={"name": "Queen's Salon"},
        services=["Hair Cut", "Coloring"]
    )
    mock_svc.create_appointment.return_value = mock_response
    
    with patch("app.tools.appointments.get_service", return_value=mock_svc):
        # Call tool
        result = await create_appointment(
            business_id=123, 
            phone="1234567890", 
            service_ids=[1, 2], 
            date_time="tomorrow"
        )
        
        # Verify WhatsApp Format (decode the escaped string first)
        import json
        decoded_wa = json.loads(f'"{result.whatsAppText}"')
        
        import sys
        
        # Configure stdout for utf-8
        if sys.stdout.encoding != 'utf-8':
            import codecs
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        
        print(f"Decoded WhatsApp Text:\n{decoded_wa}")
        
        assert "✅ *Appointment Confirmed*" in decoded_wa
        assert "🆔 ID: 9999" in decoded_wa
        assert "🏢 Queen's Salon" in decoded_wa
        assert "👤 Alice Wonderland" in decoded_wa
        assert "📅 2026-02-14 10:30 AM" in decoded_wa
        assert "💇 Hair Cut, Coloring" in decoded_wa

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_create_appointment_wa(None))
        print("Test Passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Test Failed: {e}")
