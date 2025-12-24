from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import BusinessSummary, ToolResult

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token)

async def get_summary_for_business(business_id: str, from_date: str, to_date: str, token: str = None) -> ToolResult:
    """Get a summary for a business."""
    service = get_service(token)
    data = await service.get_summary_for_business(business_id, from_date, to_date)
    text = (
        f"Business Summary for ID {business_id} from {from_date} to {to_date}:\n"
        f"- Total Leads: {data.total_leads}\n"
        f"- Total Appointments: {data.total_appointments}\n"
        f"- Total Revenue: {data.total_revenue}"
    )
    return ToolResult(type="get_summary_for_business", data=data, text=text)
