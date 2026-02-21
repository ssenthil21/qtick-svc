import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.tools.business import get_franchise_summary
from app.models import ToolResult

async def verify_franchise_hashes():
    logging.basicConfig(level=logging.INFO)
    
    # Test phone with multiple branches and hashes (from franchise_mappings.json)
    phone = "6592701525"
    
    print(f"\n--- Verifying Franchise Summaries for Phone: {phone} ---\n")
    
    # This will call get_franchise_summary which should:
    # 1. Map phone to branches 96, 97, 119, 219
    # 2. Extract hashes: HASH_96_CHE, HASH_97_MUM, etc.
    # 3. Call service.get_summary_for_business with these hashes
    
    result = await get_franchise_summary(client_id=phone)
    
    print("\n--- Summary Result ---")
    print(f"Text matches expected IDs? {'Yes' in str(result.text) or 'CHE' in str(result.text)}")
    print("\n--- Result Text ---\n")
    print(result.text)
    
    print("\n--- URL Verification (Check logs above for api/biz/HASH_.../summary) ---")

if __name__ == "__main__":
    asyncio.run(verify_franchise_hashes())
