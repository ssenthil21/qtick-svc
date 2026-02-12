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
    # Monospaced Table inside Code Block
    # Monospaced Table inside Code Block
    # Cols: ID(3), Enq(3), Rev(5), Bkg(3)
    # Header using icons (assuming approx 2 chars width for emoji)
    # ID: "🆔 " (2+1=3?) No, usually emoji is 2 chars. Let's try to center/align.
    # We'll use a mix of spaces to align. 
    # Note: Emojis inside code blocks on WhatsApp can be tricky. 
    # Best compromise: ID | ✅ | 💰  | 📅
    
    # Header: "🆔 | ✅|   💰| 📅"
    # Separator: "---|---|-----|---" (matches data widths: 3, 3, 5, 3)
    
    # Visual Alignment (assuming straight pipes and Emoji=2 chars):
    # Expanded widths for better alignment: 4, 4, 6, 4
    # Col 1 (4): "🆔  " (Emoji+2 Spaces)
    # Col 2 (4): "  ✅" (2 Spaces+Emoji)
    # Col 3 (6): "    💰" (4 Spaces+Emoji)
    # Col 4 (4): "  📅" (2 Spaces+Emoji)
    
    header = "🆔  |  ✅|    💰|  📅"
    
    table_lines = ["```", header]
    # Separator: ----|----|------|----
    table_lines.append("----|----|------|----")
    
    for s in details:
        # Business ID (last 3 chars)
        bid = str(s.business_id)[-3:].ljust(4)
        # Enquiries
        enq = str(s.total_leads).rjust(4)
        # Revenue (e.g. 12.5K, 0)
        rev = format_short_number(s.total_revenue).rjust(6)
        # Bookings
        bkg = str(s.total_appointments).rjust(4)
        
        line = f"{bid}|{enq}|{rev}|{bkg}"
        table_lines.append(line)
        
    table_lines.append("```")
    table_str = "\n".join(table_lines)

    message = (
        f"📊 *Branch Summary* ({start_str} - {end_str})\n"
        f"{table_str}\n"
        f"🔥 *Total Performance:*\n"
        f"✅ *Enquiries:* {consolidated.total_leads}\n"
        f"💰 *Revenue:* ₹{format_short_number(consolidated.total_revenue)}\n"
        f"📅 *Bookings:* {consolidated.total_appointments}\n"
    )
    
    # Escape for JSON but keep newlines for WhatsApp
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

async def get_franchise_summary(business_ids: str = None, from_date: str = None, to_date: str = None, period: str = None, token: str = None, client_id: str = None) -> ToolResult:
    """
    Get a consolidated summary for multiple businesses (franchise report).
    
    Args:
        business_ids: Comma-separated list of business IDs (e.g. "1,2,3"). Optional if client_id is provided.
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
    """Format comparison as: Previous -> Current (Icon Change%)."""
    
    # helper for value formatting
    def fmt(val):
        return f"₹{format_short_number(val)}" if is_currency else str(int(val))

    if previous == 0:
        if current == 0:
            return f"{fmt(previous)} → {fmt(current)} (➖ 0%)"
        return f"{fmt(previous)} → {fmt(current)} (🟢 New)"
        
    change = ((current - previous) / previous) * 100
    if change > 0:
        icon = "🟢 ⬆️"
    elif change < 0:
        icon = "🔴 ⬇️"
    else:
        icon = "➖"
    
    return f"{fmt(previous)} → {fmt(current)} ({icon} {abs(change):.1f}%)"

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
    else:
        # If dates are manual, use them directly
        pass

    if not from_date or not to_date:
        from_date, to_date = get_date_range("today")
        period_to_check = period_to_check or "today" # Ensure period_to_check is set for get_previous_date_range

    # 2. Determine Previous Period
    prev_from, prev_to = get_previous_date_range(period_to_check, from_date, to_date)
    
    if not prev_from or not prev_to:
         return ToolResult(
            type="get_business_performance_comparison",
            data=None,
            text="Could not determine comparison period.",
            whatsAppText=""
        )

    # Normalize dates
    if from_date: from_date = from_date.replace("-", "/")
    if to_date: to_date = to_date.replace("-", "/")
    
    # 3. Fetch Data
    service = get_service(token, client_id)
    current_data = await service.get_summary_for_business(business_id, from_date, to_date)
    prev_data = await service.get_summary_for_business(business_id, prev_from, prev_to)
    
    # 4. Calculate Comparisons
    leads_comp = format_comparison_number(current_data.total_leads, prev_data.total_leads)
    revenue_comp = format_comparison_number(current_data.total_revenue, prev_data.total_revenue, is_currency=True)
    appt_comp = format_comparison_number(current_data.total_appointments, prev_data.total_appointments)
    
    text = (
        f"📊 Performance Comparison for Business {business_id}\n"
        f"Current: {from_date} - {to_date}\n"
        f"Previous: {prev_from} - {prev_to}\n\n"
        f"✅ Enquiries: {current_data.total_leads} (vs {prev_data.total_leads})\n"
        f"💰 Revenue: ₹{current_data.total_revenue:,.2f} (vs ₹{prev_data.total_revenue:,.2f})\n"
        f"📅 Bookings: {current_data.total_appointments} (vs {prev_data.total_appointments})\n"
    )
    
    # WhatsApp Format
    # Clean Business ID
    biz_id_str = str(business_id).replace(".0", "")
    
    # Dynamic Title based on Period
    # period_to_check could be "this week", "today", "last month" etc.
    p = (period_to_check or "").lower()
    if "week" in p:
        title = "Weekly Comparison"
    elif "month" in p:
        title = "Monthly Comparison"
    elif "day" in p or "today" in p or "yesterday" in p:
        title = "Daily Comparison"
    else:
        title = "Performance Insight"
        
    header_text = f"📈 *{title}* (Biz #{biz_id_str})"
    period_text = f"_{period_to_check.title() if period_to_check else 'Custom'} vs Previous_"
    
    message = (
        f"{header_text}\n"
        f"{period_text}\n\n"
        f"✅ *Enquiries:* {leads_comp}\n"
        f"� *Bookings:* {appt_comp}\n"
        f"� *Revenue:* {revenue_comp}\n\n"
        f"🚀 *Keep growing!*"
    )
    
    escaped_message = json.dumps(message, ensure_ascii=True)[1:-1]

    return ToolResult(
        type="get_business_performance_comparison",
        data={
            "current": current_data.dict(),
            "previous": prev_data.dict()
        },
        text=text,
        whatsAppText=escaped_message
    )

