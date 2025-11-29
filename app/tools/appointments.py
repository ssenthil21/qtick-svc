from datetime import datetime
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import Appointment, ToolResult

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token)

async def create_appointment(customer_id: str, service_name: str, start_time: str, end_time: str, description: str = None, token: str = None) -> ToolResult:
    """Create a new appointment. Times should be ISO 8601 strings."""
    service = get_service(token)
    # Parse strings to datetime
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    
    appt = Appointment(
        customer_id=customer_id,
        service_name=service_name,
        start_time=start,
        end_time=end,
        description=description
    )

    result = await service.create_appointment(appt)
    text = f"Appointment created successfully. ID: {result.id}"
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
