from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import ToolResult

def get_service(token: str = None, client_id: str = None, biz_hash: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token, client_id, biz_hash)

async def search_services(business_id: int, text: str, token: str = None, client_id: str = None, biz_hash: str = None) -> ToolResult:
    """Search for services in the business catalog."""
    service = get_service(token, client_id, biz_hash)
    data = await service.search_services(business_id, text)
    
    if not data:
        text_response = f"No services found matching '{text}'."
    else:
        text_response = f"Found {len(data)} services matching '{text}':\n"
        for s in data:
            text_response += f"- ID: {s.id}, Name: {s.name}, Price: ₹{s.price}\n"
            
    return ToolResult(type="search_services", data=data, text=text_response)
