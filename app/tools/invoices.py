from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import Invoice, ToolResult

def get_service(token: str = None, client_id: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token, client_id)

async def create_invoice(business_id: str, customer_id: str, amount: float, items: list = [], token: str = None, client_id: str = None) -> ToolResult:
    """Create a new invoice."""
    service = get_service(token, client_id)
    invoice = Invoice(
        business_id=business_id,
        customer_id=customer_id,
        amount=amount,
        items=items
    )

    result = await service.create_invoice(invoice)
    text = f"Invoice created successfully. ID: {result.id}"
    return ToolResult(type="create_invoice", data=result, text=text)

async def list_invoices(token: str = None, client_id: str = None) -> ToolResult:
    """List all invoices."""
    service = get_service(token, client_id)
    data = await service.list_invoices()
    text = f"{len(data)} invoices found."
    
    # WhatsApp Format
    wa_lines = [f"🧾 *Invoices for Biz #{settings.DEFAULT_BUSINESS_ID}*"] # list_invoices doesn't take business_id arg currently, using default or context if available
    # Wait, the tool definition says it takes business_id? No, implementation above doesn't have it.
    # Checking implementation: async def list_invoices(token: str = None, client_id: str = None)
    # It seems list_invoices fetches for all businesses accessible to token? 
    # Let's check JavaService.list_invoices
    
    wa_lines = [f"🧾 *Invoices Summary*"]
    if not data:
        wa_lines.append("No invoices found.")
    else:
        # Show top 5 recent
        for inv in data[:5]:
             wa_lines.append(f"#{inv.id} - ₹{inv.amount}")
             
    wa_message = "\n".join(wa_lines)
    escaped_wa = json.dumps(wa_message, ensure_ascii=True)[1:-1]
    
    return ToolResult(type="list_invoices", data=data, text=text, whatsAppText=escaped_wa)

async def get_invoice(invoice_id: str, token: str = None, client_id: str = None) -> ToolResult:
    """Get details of a specific invoice."""
    service = get_service(token, client_id)
    data = await service.get_invoice(invoice_id)
    if data:
        text = f"Invoice details found for ID {invoice_id}."
    else:
        text = f"Invoice not found for ID {invoice_id}."
    return ToolResult(type="get_invoice", data=data, text=text)
