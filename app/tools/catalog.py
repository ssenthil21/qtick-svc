from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import ToolResult

def get_service(token: str = None, client_id: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token, client_id)

async def search_services(business_id: int, text: str, group_id: int = 0, token: str = None, client_id: str = None) -> ToolResult:
    """Search for services in the business catalog."""
    service = get_service(token, client_id)
    data = await service.search_services(business_id, text, group_id)
    text_response = f"Found {len(data)} services matching '{text}' for business ID {business_id}."
    return ToolResult(type="search_services", data=data, text=text_response)
