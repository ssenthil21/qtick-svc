from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import Invoice, ToolResult

def get_service(token: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    return JavaService(token)

async def create_invoice(business_id: str, customer_id: str, amount: float, items: list = [], token: str = None) -> ToolResult:
    """Create a new invoice."""
    service = get_service(token)
    invoice = Invoice(
        business_id=business_id,
        customer_id=customer_id,
        amount=amount,
        items=items
    )

    result = await service.create_invoice(invoice)
    text = f"Invoice created successfully. ID: {result.id}"
    return ToolResult(type="create_invoice", data=result, text=text)

async def list_invoices(token: str = None) -> ToolResult:
    """List all invoices."""
    service = get_service(token)
    data = await service.list_invoices()
    text = f"{len(data)} invoices found."
    return ToolResult(type="list_invoices", data=data, text=text)

async def get_invoice(invoice_id: str, token: str = None) -> ToolResult:
    """Get details of a specific invoice."""
    service = get_service(token)
    data = await service.get_invoice(invoice_id)
    if data:
        text = f"Invoice details found for ID {invoice_id}."
    else:
        text = f"Invoice not found for ID {invoice_id}."
    return ToolResult(type="get_invoice", data=data, text=text)
