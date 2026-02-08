import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

import asyncio
from app.tools.offers import list_offers
from app.models import Offer, OfferListResponse

# Mock data for testing
MOCK_OFFERS_RESPONSE = [
    {
        "title": "Sample Offer",
        "image": "",
        "startDate": "2024-03-28T16:00:00.000+0000",
        "endDate": "2024-04-29T16:00:00.000+0000",
        "pubStatus": "U",
        "details": "This is a sample offer...",
        "detailFormat": "P",
        "buttonHeader": "Grab the offer",
        "serviceId": 0,
        "activeCampaigns": {
            "WS": "https://qa.qtick.biz/pk-beauty-parlour?cb=269",
            "BP": "https://qa.qtick.biz/pk-beauty-parlour?cb=458"
        }
    }
]

@pytest.mark.asyncio
async def test_list_offers(mocker):
    # Mock the JavaService.list_offers method
    # We need to mock the underlying service call
    
    # Mocking at the tool level dependency
    # But since current implementation of get_service instantiates JavaService directly or checks settings,
    # we'll mock the JavaService class itself within app.tools.offers or app.services.java_service
    
    # Let's mock the 'get_service' in app.tools.offers to return a mock service
    mock_service = mocker.AsyncMock()
    mock_service.list_offers.return_value = [
        Offer(
            title="Sample Offer",
            details="This is a sample offer...",
            startDate="2024-03-28T16:00:00.000+0000",
            endDate="2024-04-29T16:00:00.000+0000",
            activeCampaigns={
                "BP": "https://qa.qtick.biz/pk-beauty-parlour?cb=458"
            },
            bp_link="https://qa.qtick.biz/pk-beauty-parlour?cb=458"
        )
    ]
    
    mocker.patch('app.tools.offers.get_service', return_value=mock_service)
    
    result = await list_offers(business_id="2")
    
    assert result.type == "list_offers"
    assert len(result.data) == 1
    assert result.data[0].title == "Sample Offer"
    assert result.data[0].bp_link == "https://qa.qtick.biz/pk-beauty-parlour?cb=458"
    assert "https://qa.qtick.biz/pk-beauty-parlour?cb=458" in result.text

if __name__ == "__main__":
    pytest.main([__file__])
