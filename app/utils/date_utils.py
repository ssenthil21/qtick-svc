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
