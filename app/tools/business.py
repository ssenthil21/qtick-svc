import json
from datetime import datetime
from app.config import settings
from app.services.mock_service import MockService
from app.services.java_service import JavaService
from app.models import BusinessSummary, ToolResult

def get_service(token: str = None, client_id: str = None):
    if settings.USE_MOCK_DATA:
        return MockService(token)
    
    return JavaService(token, client_id)

def format_short_number(num: float) -> str:
    """Format number to short form (e.g., 1.5L, 12.5K)."""
    if num >= 100000:
        return f"{num/100000:.1f}L".replace(".0L", "L")
    if num >= 1000:
        return f"{num/1000:.1f}K".replace(".0K", "K")
    return str(int(num))

def format_whatsapp_summary(data: BusinessSummary, from_date: str, to_date: str, business_id: str = "") -> str:
    """Format business summary for WhatsApp with encoding."""
    business_name = f"QTick (Biz #{business_id})" if business_id else "QTick"
    
    try:
        start_dt = datetime.strptime(from_date, "%Y/%m/%d")
        end_dt = datetime.strptime(to_date, "%Y/%m/%d")
        start_str = start_dt.strftime("%b %d, %Y")
        end_str = end_dt.strftime("%b %d, %Y")
    except Exception:
        start_str = from_date
        end_str = to_date

    message = (
        f"📊 *{business_name} Summary*\n"
        f"_{start_str} - {end_str} Business Summary_\n\n"
        f"✅ *Enquiries:* {data.total_leads}\n"
        f"💰 *Revenue:* ₹{format_short_number(data.total_revenue)}\n"
        f"📅 *Bookings:* {data.total_appointments}\n"
        f"🧾 *Bills:* {data.bills_count}\n\n"
        f"Thank you for growing with *QTick* 🚀"
    )
    
    escaped_message = json.dumps(message, ensure_ascii=True)[1:-1]
    return escaped_message

def format_whatsapp_franchise_summary(consolidated: BusinessSummary, details: list[BusinessSummary], from_date: str, to_date: str) -> str:
    """Format franchise summary for WhatsApp with a text-based table."""
    
    # Format dates
    try:
        start_dt = datetime.strptime(from_date, "%Y/%m/%d")
        end_dt = datetime.strptime(to_date, "%Y/%m/%d")
        start_str = start_dt.strftime("%b %d")
        end_str = end_dt.strftime("%b %d")
    except Exception:
        start_str = from_date
        end_str = to_date

    # ID | Enq | Rev | Bkg
    # Aligning exactly for monospaced backticks
    # Headers use 2-byte emojis, columns are padded
    header = f"  🆔 |  ✅ |  💰  |  📅 "
    table_lines = [header]
    
    for s in details:
        # Business ID (last 3 chars to handle 119, 219 etc)
        bid = str(s.business_id)[-3:].rjust(3)
        enq = str(s.total_leads).rjust(2)
        rev = format_short_number(s.total_revenue).rjust(4)
        bkg = str(s.total_appointments).rjust(2)
        
        line = f" {bid} |  {enq} | {rev} |  {bkg} "
        table_lines.append(line)

    table_str = "\n".join(table_lines)

    message = (
        f"📊 *Franchise Report*\n"
        f"_{start_str} - {end_str}_\n\n"
        f"{table_str}\n\n"
        f"🔥 *Total Performance:*\n"
        f"✅ *Enquiries:* {consolidated.total_leads}\n"
        f"💰 *Revenue:* ₹{format_short_number(consolidated.total_revenue)}\n"
        f"📅 *Bookings:* {consolidated.total_appointments}\n"
    )
    
    escaped_message = json.dumps(message, ensure_ascii=True)[1:-1]
    return escaped_message

async def get_summary_for_business(business_id: str, from_date: str = None, to_date: str = None, period: str = None, token: str = None, client_id: str = None) -> ToolResult:
    """Get a summary for a business."""
    from app.utils.date_utils import get_date_range
    
    # Date handling logic
    period_to_check = period or from_date
    if period_to_check and isinstance(period_to_check, str) and period_to_check.lower() in ["today", "yesterday", "this week", "last week", "this month", "last month"]:
        resolved_from, resolved_to = get_date_range(period_to_check)
        if resolved_from and resolved_to:
            from_date = resolved_from
            to_date = resolved_to

    if not from_date or not to_date:
        # Fallback to today if nothing is provided
        from_date, to_date = get_date_range("today")

    # Final normalization: Ensure YYYY/MM/DD format even if LLM sends dashes
    if from_date:
        from_date = from_date.replace("-", "/")
    if to_date:
        to_date = to_date.replace("-", "/")

    service = get_service(token, client_id)
    data = await service.get_summary_for_business(business_id, from_date, to_date)
    text = (
        f"Business Summary for ID {business_id} from {from_date} to {to_date}:\n"
        f"✅ Total Leads: {data.total_leads}\n"
        f"📅 Total Appointments: {data.total_appointments}\n"
        f"🧾 Total Bills: {data.bills_count}\n"
        f"💰 Total Revenue: ₹{data.total_revenue:,.2f}"
    )
    
    whatsAppText = format_whatsapp_summary(data, from_date, to_date, business_id)
    
    return ToolResult(
        type="get_summary_for_business", 
        data=data, 
        text=text,
        whatsAppText=whatsAppText
    )

async def get_franchise_summary(business_ids: str, from_date: str = None, to_date: str = None, period: str = None, token: str = None, client_id: str = None) -> ToolResult:
    """
    Get a consolidated summary for multiple businesses (franchise report).
    
    Args:
        business_ids: Comma-separated list of business IDs (e.g. "1,2,3")
        from_date: Start date (YYYY/MM/DD or YYYY-MM-DD)
        to_date: End date (YYYY/MM/DD or YYYY-MM-DD)
        period: shortcut like "today", "yesterday", "this week"
        token: Optional auth token
    """
    from app.utils.date_utils import get_date_range
    
    # Date handling logic
    period_to_check = period or from_date
    if period_to_check and isinstance(period_to_check, str) and period_to_check.lower() in ["today", "yesterday", "this week", "last week", "this month", "last month"]:
        resolved_from, resolved_to = get_date_range(period_to_check)
        if resolved_from and resolved_to:
            from_date = resolved_from
            to_date = resolved_to

    if not from_date or not to_date:
        from_date, to_date = get_date_range("today")

    # Normalize dates
    if from_date:
        from_date = from_date.replace("-", "/")
    if to_date:
        to_date = to_date.replace("-", "/")

    service = get_service(token, client_id)
    
    # Auto-mapping for franchises if no IDs are provided
    if not business_ids and client_id:
        from app.utils.mappings import get_franchise_ids_by_phone
        mapped_ids = get_franchise_ids_by_phone(client_id)
        if mapped_ids:
            business_ids = ",".join(map(str, mapped_ids))
            print(f"Auto-mapped franchise IDs for {client_id}: {business_ids}")

    if not business_ids:
        return ToolResult(
            type="get_franchise_summary",
            data=None,
            text="Please specify which business IDs you want to include in the franchise report, or ensure your phone number is registered as a franchise owner.",
            whatsAppText=""
        )

    ids = [bid.strip() for bid in business_ids.split(",") if bid.strip()]
    
    total_leads = 0
    total_appointments = 0
    bills_count = 0
    total_revenue = 0.0
    
    # We could collect individual summaries if needed, but for now we aggregate
    details = []
    
    for business_id in ids:
        try:
           data = await service.get_summary_for_business(business_id, from_date, to_date)
           if data:
               details.append(data)
               total_leads += data.total_leads
               total_appointments += data.total_appointments
               bills_count += data.bills_count
               total_revenue += data.total_revenue
        except Exception as e:
            # We continue even if one branch fails
            print(f"Error fetching summary for business {business_id}: {e}")
            pass

    # Create a consolidated BusinessSummary object
    consolidated_data = BusinessSummary(
        business_id="FRANCHISE_GROUP",
        total_leads=total_leads,
        total_appointments=total_appointments,
        bills_count=bills_count,
        total_revenue=total_revenue,
        recent_activities=[]
    )
    
    # Create Markdown Table
    table_header = "| Branch ID | Leads | Appointments | Bills | Revenue |\n|---|---|---|---|---|\n"
    table_rows = ""
    for d in details:
         table_rows += f"| {d.business_id} | {d.total_leads} | {d.total_appointments} | {d.bills_count} | ₹{d.total_revenue:,.2f} |\n"
    
    text = (
        f"Franchise Summary for businesses {business_ids} from {from_date} to {to_date}:\n\n"
        f"{table_header + table_rows}\n"
        f"**Totals:**\n"
        f"✅ Total Leads: {total_leads}\n"
        f"📅 Total Appointments: {total_appointments}\n"
        f"🧾 Total Bills: {bills_count}\n"
        f"💰 Total Revenue: ₹{total_revenue:,.2f}"
    )
    
    whatsAppText = format_whatsapp_franchise_summary(consolidated_data, details, from_date, to_date)
    
    return ToolResult(
        type="get_franchise_summary",
        data=consolidated_data,
        text=text,
        whatsAppText=whatsAppText
    )

def format_comparison_number(current: float, previous: float, is_currency: bool = False) -> str:
    """Format comparison with emoji arrows."""
    if previous == 0:
        if current == 0:
            return "0% (No change)"
        return "N/A (New)"
        
    change = ((current - previous) / previous) * 100
    icon = "⬆️" if change > 0 else "⬇️" if change < 0 else "➖"
    
    formatted_change = f"{icon} {abs(change):.1f}%"
    
    if is_currency:
        return f"₹{format_short_number(current)} ({formatted_change})"
    return f"{format_short_number(current)} ({formatted_change})"

async def get_business_performance_comparison(business_id: str = None, period: str = None, from_date: str = None, to_date: str = None, token: str = None, client_id: str = None) -> ToolResult:
    """
    Compare business performance between two periods (e.g. This Week vs Last Week).
    """
    from app.utils.date_utils import get_date_range, get_previous_date_range
    
    # Auto-detect business ID if missing (single business case)
    if not business_id and client_id:
        from app.utils.mappings import get_business_id_by_phone
        # Try to get a single primary ID
        detected_id = get_business_id_by_phone(client_id)
        if detected_id:
            business_id = str(detected_id)
            print(f"Auto-detected business ID for comparison: {business_id}")
            
    if not business_id:
         return ToolResult(
            type="get_business_performance_comparison",
            data=None,
            text="Please specify the business ID for comparison, or ensure your phone number is registered to a business.",
            whatsAppText=""
        )

    # 1. Determine Current Period
    period_to_check = period or from_date
    if period_to_check and isinstance(period_to_check, str) and period_to_check.lower() in ["today", "yesterday", "this week", "last week", "this month", "last month"]:
        from_date, to_date = get_date_range(period_to_check)
    
    if not from_date or not to_date:
        from_date, to_date = get_date_range("today")
        period = "today"

    # Normalize dates
    from_date = from_date.replace("-", "/")
    to_date = to_date.replace("-", "/")

    # 2. Determine Previous Period
    prev_from, prev_to = get_previous_date_range(period, from_date, to_date)
    
    if not prev_from or not prev_to:
        return ToolResult(type="error", text="Could not determine previous comparison period.")

    service = get_service(token, client_id)
    
    # 3. Fetch Data
    current_data = await service.get_summary_for_business(business_id, from_date, to_date)
    prev_data = await service.get_summary_for_business(business_id, prev_from, prev_to)
    
    # 4. Format Output
    text = (
        f"📊 Performance Comparison for Business {business_id}\n"
        f"Current: {from_date} - {to_date}\n"
        f"Previous: {prev_from} - {prev_to}\n\n"
        f"✅ Enquiries: {current_data.total_leads} (vs {prev_data.total_leads})\n"
        f"💰 Revenue: ₹{current_data.total_revenue:,.2f} (vs ₹{prev_data.total_revenue:,.2f})\n"
        f"📅 Bookings: {current_data.total_appointments} (vs {prev_data.total_appointments})\n"
    )
    
    # WhatsApp Formatting
    message = (
        f"📊 *Performance Insight*\n"
        f"_{period.title() if period else 'Custom Period'} vs Previous_\n\n"
        f"✅ *Enquiries*: {format_comparison_number(current_data.total_leads, prev_data.total_leads)}\n"
        f"💰 *Revenue*: {format_comparison_number(current_data.total_revenue, prev_data.total_revenue, True)}\n"
        f"📅 *Bookings*: {format_comparison_number(current_data.total_appointments, prev_data.total_appointments)}\n\n"
        f"🚀 *Keep growing!*"
    )
    
    whatsAppText = json.dumps(message, ensure_ascii=True)[1:-1]
    
    return ToolResult(
        type="get_business_performance_comparison",
        data={
            "current": current_data,
            "previous": prev_data
        },
        text=text,
        whatsAppText=whatsAppText
    )
