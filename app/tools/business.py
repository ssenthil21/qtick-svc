import json
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import BusinessSummary, ToolResult

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    
    print(token)
    return JavaService(token)

def format_whatsapp_summary(data: BusinessSummary) -> str:
    """Format business summary for WhatsApp with encoding."""
    # Assuming business name might be available in a real scenario, 
    # but for now using a placeholder or just "Business Summary"
    # The sample had "QTick – Chillbreeze"
    business_name = "QTick" 
    
    message = (
        f"📊 *{business_name} Summary*\n"
        f"_Weekly Business Summary_\n\n"
        f"✅ *Leads Generated:* {data.total_leads}\n"
        f"💰 *Revenue:* ₹{data.total_revenue:,.2f}\n"
        f"📅 *Appointments Booked:* {data.total_appointments}\n"
        f"🧾 *Bills Generated:* {data.bills_count}\n\n"
        f"Thank you for growing with *QTick* 🚀"
    )
    
    # Convert to unicode-escaped string (safe for n8n)
    escaped_message = json.dumps(message, ensure_ascii=True)[1:-1]
    return escaped_message

async def get_summary_for_business(business_id: str, from_date: str = None, to_date: str = None, period: str = None, token: str = None) -> ToolResult:
    """Get a summary for a business."""
    from app.utils.date_utils import get_date_range
    
    # If period is provided, or if from_date looks like a period name
    period_to_check = period or from_date
    if period_to_check and period_to_check.lower() in ["today", "yesterday", "this week", "last week", "this month", "last month"]:
        resolved_from, resolved_to = get_date_range(period_to_check)
        if resolved_from and resolved_to:
            from_date = resolved_from
            to_date = resolved_to

    if not from_date or not to_date:
        # Fallback to today if nothing is provided
        from_date, to_date = get_date_range("today")

    # Final normalization: Ensure YYYY/MM/DD format even if LLM sends dashes
    if from_date:
        from_date = from_date.replace("-", "/")
    if to_date:
        to_date = to_date.replace("-", "/")

    service = get_service(token)
    data = await service.get_summary_for_business(business_id, from_date, to_date)
    text = (
        f"Business Summary for ID {business_id} from {from_date} to {to_date}:\n"
        f"✅ Total Leads: {data.total_leads}\n"
        f"📅 Total Appointments: {data.total_appointments}\n"
        f"🧾 Total Bills: {data.bills_count}\n"
        f"💰 Total Revenue: ₹{data.total_revenue:,.2f}"
    )
    
    whatsAppText = format_whatsapp_summary(data)
    
    return ToolResult(
        type="get_summary_for_business", 
        data=data, 
        text=text,
        whatsAppText=whatsAppText
    )
