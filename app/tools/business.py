from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import BusinessSummary, ToolResult

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token)

async def get_summary_for_business(business_id: str, token: str = None) -> ToolResult:
    """Get a summary for a business."""
    service = get_service(token)
    data = await service.get_summary_for_business(business_id)
    text = f"Business summary retrieved for ID {business_id}."
    return ToolResult(type="get_summary_for_business", data=data, text=text)
