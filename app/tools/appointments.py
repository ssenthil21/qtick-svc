from datetime import datetime
from typing import List
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import Appointment, ToolResult, BookingRequest, AppointmentSummary
from app.utils.date_utils import parse_date_flexible, get_date_range
import json

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
    
    # WhatsApp Format
    services_str = ", ".join(result.services)
    wa_message = (
        f"✅ *Appointment Confirmed*\n"
        f"🆔 ID: {result.bookingId}\n"
        f"🏢 {result.bizInfo.get('name')}\n"
        f"👤 {result.custName}\n"
        f"📅 {result.date} {result.time}\n"
        f"💇 {services_str}\n"
    )
    escaped_wa = json.dumps(wa_message, ensure_ascii=True)[1:-1]
    
    return ToolResult(type="create_appointment", data=result, text=text, whatsAppText=escaped_wa)

async def list_appointments(business_id: int, from_date: str = None, to_date: str = None, period: str = None, token: str = None) -> ToolResult:
    """List appointments with date filtering."""
    
    # Handle date logic
    period_to_check = period or from_date
    if period_to_check and period_to_check.lower() in ["today", "yesterday", "this week", "last week", "this month", "last month"]:
        resolved_from, resolved_to = get_date_range(period_to_check)
        if resolved_from and resolved_to:
            from_date = resolved_from
            to_date = resolved_to
            
    if not from_date or not to_date:
        from_date, to_date = get_date_range("today")

    # Normalize dates
    if from_date: from_date = from_date.replace("-", "/")
    if to_date: to_date = to_date.replace("-", "/")

    # Ensure format YYYY/MM/DD HH:mm:ss for API
    if len(from_date.split(' ')) == 1: from_date += " 00:00:00"
    if len(to_date.split(' ')) == 1: to_date += " 23:59:59"

    service = get_service(token)
    data = await service.list_appointments(business_id, from_date, to_date)
    
    # Text Format
    text_lines = [f"Found {len(data)} appointments from {from_date} to {to_date}:"]
    for appt in data:
        start_dt = str(appt.start_time) # Convert to string if needed
        # Try to parse and pretty print time
        try:
           dt_obj = datetime.strptime(appt.start_time, "%Y-%m-%dT%H:%M:%S.000+0000")
           time_str = dt_obj.strftime("%I:%M %p")
           date_str = dt_obj.strftime("%b %d")
        except:
           time_str = appt.start_time
           date_str = ""

        text_lines.append(f"- {date_str} {time_str} | {appt.customer_name} | {appt.service_name} | {appt.status}")
    
    text = "\n".join(text_lines)

    # WhatsApp Format
    wa_lines = [f"📅 *Appointments ({len(data)})*"]
    for appt in data:
        try:
           dt_obj = datetime.strptime(appt.start_time, "%Y-%m-%dT%H:%M:%S.000+0000")
           time_str = dt_obj.strftime("%I:%M %p")
           date_str = dt_obj.strftime("%d %b")
        except:
           time_str = appt.start_time
           date_str = ""
           
        wa_lines.append(
            f"🕒 *{date_str} {time_str}*\n"
            f"👤 {appt.customer_name}\n"
            f"💇 {appt.service_name}\n"
            f"ℹ️ Status: {appt.status}\n"
        )
    
    wa_message = "\n".join(wa_lines)
    escaped_wa = json.dumps(wa_message, ensure_ascii=True)[1:-1]

    return ToolResult(type="list_appointments", data=data, text=text, whatsAppText=escaped_wa)

async def get_appointment(appointment_id: str, token: str = None) -> ToolResult:
    """Get details of a specific appointment."""
    service = get_service(token)
    data = await service.get_appointment(appointment_id)
    if data:
        text = f"Appointment details found for ID {appointment_id}."
    else:
        text = f"Appointment not found for ID {appointment_id}."
    return ToolResult(type="get_appointment", data=data, text=text)
