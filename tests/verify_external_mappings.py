import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

def test_external_mappings():
    print("Testing External Mappings Loading...")
    
    # Force default environment
    os.environ["APP_ENV"] = "local"
    from importlib import reload
    import app.config
    import app.utils.mappings
    reload(app.config)
    reload(app.utils.mappings)
    
    from app.utils.mappings import get_business_id_by_phone, get_franchise_ids_by_phone
    
    # Test Business Mapping (from data/phone_mappings.json)
    biz_id = get_business_id_by_phone("6592701525")
    print(f"Phone 6592701525 -> Biz ID: {biz_id} (Expected: 96)")
    
    # Test Franchise Mapping (from data/franchise_mappings.json)
    franchise_ids = get_franchise_ids_by_phone("6592701525")
    print(f"Phone 6592701525 -> Franchise IDs: {franchise_ids} (Expected: [96, 97, 119, 219])")
    
    # Test QA environment
    os.environ["APP_ENV"] = "qa"
    reload(app.config)
    reload(app.utils.mappings)
    biz_id_qa = get_business_id_by_phone("6592701525")
    print(f"QA: Phone 6592701525 -> Biz ID: {biz_id_qa} (Expected: None since QA file is empty)")

if __name__ == "__main__":
    test_external_mappings()
