import pytest
from app.utils.date_utils import get_date_range
from datetime import datetime, timedelta

def test_get_date_range_today():
    start, end = get_date_range("today")
    now_str = datetime.now().strftime("%Y/%m/%d")
    assert start == now_str
    assert end == now_str

def test_get_date_range_yesterday():
    start, end = get_date_range("yesterday")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    assert start == yesterday_str
    assert end == yesterday_str

def test_get_date_range_this_week():
    start, end = get_date_range("this week")
    now = datetime.now()
    expected_start = (now - timedelta(days=now.weekday())).strftime("%Y/%m/%d")
    expected_end = now.strftime("%Y/%m/%d")
    assert start == expected_start
    assert end == expected_end

def test_get_date_range_last_month():
    start, end = get_date_range("last month")
    now = datetime.now()
    first_day_this_month = now.replace(day=1)
    expected_end = (first_day_this_month - timedelta(days=1))
    expected_start = expected_end.replace(day=1)
    
    assert start == expected_start.strftime("%Y/%m/%d")
    assert end == expected_end.strftime("%Y/%m/%d")

@pytest.mark.asyncio
async def test_business_summary_tool_integration(mocker):
    from app.tools.business import get_summary_for_business
    from app.models import ToolResult, BusinessSummary
    
    # Mock JavaService.get_summary_for_business
    mock_data = BusinessSummary(
        business_id="123",
        total_leads=10,
        total_appointments=5,
        bills_count=5,
        total_revenue=5000.0,
        recent_activities=[]
    )
    
    # Mock get_service to return a mock object
    class MockSvc:
        async def get_summary_for_business(self, bid, f, t):
            # Capture for verification
            self.captured_from = f
            self.captured_to = t
            return mock_data

    mock_svc = MockSvc()
    mocker.patch("app.tools.business.get_service", return_value=mock_svc)
    
    # Test with period="today"
    result: ToolResult = await get_summary_for_business(business_id="123", period="today")
    
    now_str = datetime.now().strftime("%Y/%m/%d")
    assert mock_svc.captured_from == now_str
    assert mock_svc.captured_to == now_str
    assert "Business Summary for ID 123 from" in result.text
    assert "₹5,000.00" in result.text

if __name__ == "__main__":
    import asyncio
    # Simple manual run if needed
    print(get_date_range("today"))
    print(get_date_range("this week"))
