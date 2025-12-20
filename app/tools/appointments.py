from datetime import datetime
from typing import List
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import Appointment, ToolResult, BookingRequest
from app.utils.date_utils import parse_date_flexible

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token)

async def create_appointment(business_id: int, phone: str, service_ids: List[int], date_time: str, token: str = None) -> ToolResult:
    """Create a new appointment. Supports natural language dates."""
    date_time = parse_date_flexible(date_time)
    service = get_service(token)
    
    request = BookingRequest(
        bizId=int(business_id),
        phone=phone,
        serviceIds=[int(sid) for sid in service_ids],
        dateTime=date_time
    )

    result = await service.create_appointment(request)
    text = f"Appointment created successfully. ID: {result.bookingId}. Status: Pending. Business: {result.bizInfo.get('name')}."
    return ToolResult(type="create_appointment", data=result, text=text)

async def list_appointments(token: str = None) -> ToolResult:
    """List all appointments."""
    service = get_service(token)
    data = await service.list_appointments()
    text = f"{len(data)} appointments found."
    return ToolResult(type="list_appointments", data=data, text=text)

async def get_appointment(appointment_id: str, token: str = None) -> ToolResult:
    """Get details of a specific appointment."""
    service = get_service(token)
    data = await service.get_appointment(appointment_id)
    if data:
        text = f"Appointment details found for ID {appointment_id}."
    else:
        text = f"Appointment not found for ID {appointment_id}."
    return ToolResult(type="get_appointment", data=data, text=text)
