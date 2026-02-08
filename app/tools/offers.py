import json
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import ToolResult, OfferListResponse

def get_service(token: str = None, client_id: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token, client_id)

def format_whatsapp_offer_list(offers: list, business_id: str) -> str:
    """Format offer list for WhatsApp."""
    if not offers:
        return json.dumps("No active offers found.", ensure_ascii=True)[1:-1]

    message = f"🎉 *Active Offers for Business #{business_id}*\n\n"
    
    for i, offer in enumerate(offers):
        message += f"*{i+1}. {offer.title}*\n"
        if offer.bp_link:
            message += f"🔗 {offer.bp_link}\n"
        message += "\n"
        
    message += "Grab them while they last! 🚀"
    return json.dumps(message, ensure_ascii=True)[1:-1]

async def list_offers(business_id: str, token: str = None, client_id: str = None) -> ToolResult:
    """
    List active offers for a business.
    
    Args:
        business_id: The ID of the business.
        token: Optional auth token.
    """
    service = get_service(token, client_id)
    
    try:
        offers = await service.list_offers(business_id)
    except Exception as e:
        return ToolResult(
            type="list_offers",
            data=[],
            text=f"Error fetching offers: {str(e)}",
            whatsAppText=""
        )

    # Format text response
    if not offers:
        text = f"No active offers found for business {business_id}."
    else:
        text = f"Found {len(offers)} active offers for business {business_id}:\n\n"
        for offer in offers:
            text += f"Title: {offer.title}\n"
            text += f"Details: {offer.details}\n"
            text += f"BP Link: {offer.bp_link}\n"
            text += "---\n"

    whatsAppText = format_whatsapp_offer_list(offers, business_id)

    return ToolResult(
        type="list_offers",
        data=offers,
        text=text,
        whatsAppText=whatsAppText
    )
