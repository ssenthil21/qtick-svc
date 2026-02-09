import dateparser
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def parse_date_flexible(date_str: str) -> str:
    """
    Parses a flexible date string (natural language or ISO) and returns 
    the format required by the Java API: YYYY-MM-DDTHH:MM:SS.000+0000
    """
    if not date_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000+0000")

    # Try parsing with dateparser
    dt = dateparser.parse(
        date_str, 
        settings={
            'RELATIVE_BASE': datetime.now(),
            'PREFER_DATES_FROM': 'future',
            'RETURN_AS_TIMEZONE_AWARE': True
        }
    )

    # Fallback for "next X" which dateparser sometimes struggles with
    if not dt and "next" in date_str.lower():
        try:
            from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
            days = {"monday": MO, "tuesday": TU, "wednesday": WE, "thursday": TH, "friday": FR, "saturday": SA, "sunday": SU}
            for day_name, day_code in days.items():
                if day_name in date_str.lower():
                    # "next monday" usually means the Monday of next week
                    # relativedelta(weekday=MO(+2)) or similar
                    dt = datetime.now(timezone.utc) + relativedelta(weekday=day_code(+1))
                    if dt <= datetime.now(timezone.utc):
                         dt += relativedelta(weeks=1)
                    break
        except Exception as e:
            logger.error(f"Error in next-day fallback: {e}")

    if not dt:
        logger.warning(f"Could not parse date string: {date_str}. Falling back to now.")
        dt = datetime.now(timezone.utc)
    
    # Ensure it's in UTC/canonical format for Java
    # Format: 2025-12-20T03:41:00.000+0000
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000+0000")

def get_date_range(period: str):
    """
    Calculates start and end dates for a given period string.
    Returns: (from_date, to_date) as YYYY-MM-DD
    """
    from datetime import timedelta
    now = datetime.now()
    period = period.lower().strip()
    
    if period == "today":
        start = now
        end = now
    elif period == "yesterday":
        start = now - timedelta(days=1)
        end = now - timedelta(days=1)
    elif period == "this week":
        start = now - timedelta(days=now.weekday())
        end = now
    elif period == "last week":
        last_sunday = now - timedelta(days=now.weekday() + 1)
        start = last_sunday - timedelta(days=6)
        end = last_sunday
    elif period == "this month":
        start = now.replace(day=1)
        end = now
    elif period == "last month":
        first_day_this_month = now.replace(day=1)
        end = first_day_this_month - timedelta(days=1)
        start = end.replace(day=1)
    else:
        return None, None

    return start.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")

def get_previous_date_range(period: str = None, from_date: str = None, to_date: str = None):
    """
    Calculates the previous period's start and end dates.
    If period is provided, uses logical previous period (e.g. today -> yesterday).
    If dates are provided, calculates duration and shifts back.
    """
    from datetime import timedelta
    
    # 1. Logical Period-based shift
    if period:
        period = period.lower().strip()
        if period == "today":
            return get_date_range("yesterday")
        elif period == "yesterday":
            # Day before yesterday
            now = datetime.now()
            start = now - timedelta(days=2)
            end = now - timedelta(days=2)
            return start.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")
        elif period == "this week":
            return get_date_range("last week")
        elif period == "this month":
            return get_date_range("last month")
        elif period == "last month":
            # Month before last
            now = datetime.now()
            first_this = now.replace(day=1)
            last_prev = first_this - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            
            last_prev_prev = first_prev - timedelta(days=1)
            first_prev_prev = last_prev_prev.replace(day=1)
            return first_prev_prev.strftime("%Y/%m/%d"), last_prev_prev.strftime("%Y/%m/%d")
            
    # 2. Date-based shift
    if from_date and to_date:
        try:
            start = datetime.strptime(from_date, "%Y/%m/%d")
            end = datetime.strptime(to_date, "%Y/%m/%d")
            duration = end - start
            
            # Shift back by duration + 1 day
            prev_end = start - timedelta(days=1)
            prev_start = prev_end - duration
            
            return prev_start.strftime("%Y/%m/%d"), prev_end.strftime("%Y/%m/%d")
        except ValueError:
            return None, None
            
    return None, None
