from app.tools.leads import create_lead
from app.models import ToolResult

async def capture_lead(name: str, phone: str = None, email: str = None, interest: str = None, token: str = None) -> ToolResult:
    """
    Capture a lead from the website chat.
    """
    # Use a specific business ID for website leads (e.g., 0 or a config value)
    # For now, we'll use 0 or 1 as a placeholder, or maybe the user wants to pass it.
    # Let's assume a default "QTick Website" business ID, say 1.
    WEBSITE_BUSINESS_ID = 1 
    
    # Map interest string to an integer if possible, or just put it in notes
    # The create_lead tool expects 'interest' as int, but let's put the text in 'details'
    
    details = f"Interest: {interest}" if interest else "Website Enquiry"
    
    result = await create_lead(
        name=name,
        business_id=WEBSITE_BUSINESS_ID,
        phone=phone,
        email=email,
        source="Website Chat",
        details=details,
        token=token
    )
    
    return ToolResult(
        type="capture_lead",
        data=result.data,
        text=f"Thanks {name}, we have received your details. Our team will contact you shortly."
    )
