import logging
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import Lead, LeadCreateRequest, LeadCreateResponse, LeadListResponse, ToolResult

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token)

async def create_lead(
    name: str, 
    business_id: int,
    email: str = None, 
    phone: str = None,
    source: str = "manual",
    notes: str = None,
    location: str = None,
    enquiry_for: str = None,
    details: str = None,
    interest: int = None,
    follow_up_date: str = None,
    enquired_on: str = None,
    enquiry_for_time: str = None,
    attention_staff_id: int = None,
    attention_channel: str = None,
    third_status: str = None,
    service_name: str = None,
    prompt: str = None,
    token: str = None
) -> LeadCreateResponse:
    """Create a new lead."""
    service = get_service(token)
    
    # If enquiry_for is not provided, use service_name, then original chat message (prompt)
    if not enquiry_for:
        if service_name:
            enquiry_for = service_name
        elif prompt:
            enquiry_for = prompt
        
    request = LeadCreateRequest(
        business_id=int(business_id),
        name=name,
        email=email,
        phone=phone,
        source=source,
        notes=notes,
        location=location,
        enquiry_for=enquiry_for,
        details=details,
        interest=interest,
        follow_up_date=follow_up_date,
        enquired_on=enquired_on,
        enquiry_for_time=enquiry_for_time,
        attention_staff_id=attention_staff_id,
        attention_channel=attention_channel,
        third_status=third_status,
        service_name=service_name
    )
    result = await service.create_lead(request)
    logging.info(result)    
    return ToolResult(
        type="create_lead",
        data=result,
        text=f"Lead created successfully. ID: {result.lead_id}, Customer: {result.custName}, Phone: {result.phone}, Enquiry For: {result.enqFor}, Value: {result.value}, Status: {result.status}"
    )

async def list_leads(business_id: int, token: str = None) -> ToolResult:
    """List all leads."""
    service = get_service(token)
    data = await service.list_leads(int(business_id))
    
    # Generate text response
    summary = f"{data.total} leads found for business {business_id}."
    
    # Generate Markdown table
    if data.items:
        table = "| Lead ID | Name | Status | Created At | Phone | Email | Source | Value |\n"
        table += "|---|---|---|---|---|---|---|---|\n"
        for item in data.items:
            table += f"| {item.lead_id} | {item.name} | {item.status} | {item.created_at} | {item.phone} | {item.email} | {item.source} | {item.value} |\n"
        text = f"{summary}\n\n{table}"
    else:
        text = summary

    return ToolResult(type="list_leads", data=data.items, text=summary)
