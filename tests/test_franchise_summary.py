import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from unittest.mock import AsyncMock, patch
from app.tools.business import get_franchise_summary
from app.models import BusinessSummary

@pytest.mark.asyncio
async def test_get_franchise_summary():
    # Setup mock service response
    mock_data = BusinessSummary(
        business_id="1",
        total_leads=10,
        total_appointments=5,
        bills_count=2,
        total_revenue=1000.0,
        recent_activities=[]
    )
    
    # We patch get_service to return our mock service
    with patch('app.tools.business.get_service') as mock_get_service:
        mock_service = AsyncMock()
        mock_service.get_summary_for_business.return_value = mock_data
        mock_get_service.return_value = mock_service
        
        # Call the function with two business IDs
        result = await get_franchise_summary("1, 2", period="today")
        
        # Verify calls
        assert mock_service.get_summary_for_business.call_count == 2
        
        # Verify aggregation
        assert result.type == "get_franchise_summary"
        # Leads: 10 + 10 = 20
        # Revenue: 1000 + 1000 = 2000
        assert result.data.total_leads == 20
        assert result.data.total_revenue == 2000.0
        assert result.data.business_id == "FRANCHISE_GROUP"
        
        # Verify text output (Markdown table)
        assert "| Branch ID | Leads |" in result.text
        assert "| 1 | 10 |" in result.text
        
        
        # Verify WhatsApp text (Unicode table)
        import json
        decoded_text = json.loads(f'"{result.whatsAppText}"')
        
        assert "Franchise Report" in decoded_text
        assert "Total Performance" in decoded_text
        # We check for the column headers or structure
        assert "\U0001f194" in decoded_text

if __name__ == "__main__":
    pytest.main([__file__])
