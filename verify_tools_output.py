import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')

from app.config import settings
# Force mock data for this verification
settings.USE_MOCK_DATA = True

from app.tools.offers import list_offers
from app.tools.business import get_franchise_summary

async def main():
    print("--- Testing List Offers Tool ---")
    offers_result = await list_offers(business_id="123")
    print(f"Type: {offers_result.type}")
    print(f"Text Response:\n{offers_result.text}")
    print(f"WhatsApp Text:\n{offers_result.whatsAppText}")
    print("-" * 30)

    print("\n--- Testing Franchise Summary Tool ---")
    franchise_result = await get_franchise_summary(business_ids="1,2,3", period="this month")
    print(f"Type: {franchise_result.type}")
    print(f"Text Response:\n{franchise_result.text}")
    print(f"WhatsApp Text:\n{franchise_result.whatsAppText}")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
