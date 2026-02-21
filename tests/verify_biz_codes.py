import asyncio
import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

async def test_biz_codes():
    print("Testing BIZ Codes Integration...")
    
    # 1. Setup mock mode and local env
    os.environ["APP_ENV"] = "local"
    os.environ["USE_MOCK_DATA"] = "true"
    
    from importlib import reload
    import app.config
    import app.utils.mappings
    import app.tools.business
    import app.services.java_service
    
    reload(app.config)
    reload(app.utils.mappings)
    reload(app.services.java_service)
    reload(app.tools.business)
    
    from app.tools.business import get_franchise_summary
    
    # Test for phone mapping with multiple branches (from franchise_mappings.json)
    # 6592701525 -> {96: CHE, 97: MUM, 119: BLR, 219: HYD}
    print("\n--- Testing Franchise Summary with BIZ Codes ---")
    result = await get_franchise_summary(client_id="6592701525")
    
    # Avoid printing Rupee symbol to prevent encoding errors
    clean_text = result.text.replace("\u20b9", "Rs")
    print(f"Text Response Snippet:\n{clean_text[:200]}...")
    
    print(f"\nWhatsApp Text Full Response:\n")
    # Replace the escaped newline and the rupee symbol
    wa_text = result.whatsAppText.replace("\\n", "\n").replace("\u20b9", "Rs")
    print(wa_text)

if __name__ == "__main__":
    # Ensure UTF-8 output even on Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    asyncio.run(test_biz_codes())
