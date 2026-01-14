import json
from app.models import ToolResult

def format_whatsapp_help() -> str:
    """Format the help guide for WhatsApp."""
    message = (
        "👋 *Welcome to QTick Assistant!*\n\n"
        "I'm here to help you manage your business efficiently. Here's what I can do for you:\n\n"
        "📊 *Business Summary*\n"
        "• Get overview of leads, revenue, and appointments.\n"
        "• _Try: 'Show summary for today' or 'How was last week?'_\n\n"
        "👥 *Lead Management*\n"
        "• Create new leads and list existing ones.\n"
        "• _Try: 'Create lead for John' or 'List all leads'_\n\n"
        "📅 *Appointments*\n"
        "• Book new appointments and view your schedule.\n"
        "• _Try: 'Book Facial for tomorrow 10am' or 'List appointments'_\n\n"
        "📋 *Catalog & Invoices*\n"
        "• Search services and manage invoices.\n"
        "• _Try: 'Search for Haircut' or 'List my invoices'_\n\n"
        "Just tell me what you need, and I'll take care of it! 🚀"
    )
    # Convert to unicode-escaped string (safe for n8n)
    return json.dumps(message, ensure_ascii=True)[1:-1]

async def get_help_guide() -> ToolResult:
    """Provides a guide on how to use the QTick Assistant."""
    text = (
        "Welcome to QTick Assistant! I can help you with the following:\n\n"
        "1. Business Summary: Get stats on leads, revenue, and appointments (e.g., 'today', 'this week').\n"
        "2. Lead Management: Create (name, phone, enquiry) and list leads.\n"
        "3. Appointments: Book services for customers and list upcoming schedules.\n"
        "4. Catalog: Search for services in your business catalog.\n"
        "5. Invoices: List and manage business invoices.\n\n"
        "How can I help you today?"
    )
    
    whatsAppText = format_whatsapp_help()
    
    return ToolResult(
        type="get_help_guide",
        data={"guide": "Getting Started"},
        text=text,
        whatsAppText=whatsAppText
    )
