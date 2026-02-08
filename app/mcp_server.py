from mcp.server.fastmcp import FastMCP
from app.tools.leads import create_lead, list_leads
from app.tools.appointments import create_appointment, list_appointments, get_appointment
from app.tools.invoices import create_invoice, list_invoices, get_invoice
from app.tools.business import get_summary_for_business, get_franchise_summary
from app.tools.offers import list_offers

# Initialize FastMCP server
mcp = FastMCP("QTick Service")

# Register tools
mcp.add_tool(create_lead)
mcp.add_tool(list_leads)
mcp.add_tool(create_appointment)
mcp.add_tool(list_appointments)
mcp.add_tool(get_appointment)
mcp.add_tool(create_invoice)
mcp.add_tool(list_invoices)
mcp.add_tool(get_invoice)
mcp.add_tool(get_summary_for_business)
mcp.add_tool(get_franchise_summary)
mcp.add_tool(list_offers)
