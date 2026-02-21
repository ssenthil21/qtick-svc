import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

def test_robust_mappings():
    print("Testing Robust Phone Mappings...")
    os.environ["APP_ENV"] = "local"
    
    from importlib import reload
    import app.config
    import app.utils.mappings
    reload(app.config)
    reload(app.utils.mappings)
    
    from app.utils.mappings import get_business_id_by_phone
    
    # 1. Test 10-digit to 10-digit (Exact)
    biz_id_1 = get_business_id_by_phone("6592701525")
    print(f"Match 6592701525 -> {biz_id_1} (Expected: 96)")
    
    # 2. Test 8-digit to 10-digit (Prefix auto-add)
    biz_id_2 = get_business_id_by_phone("92701525")
    print(f"Match 92701525 -> {biz_id_2} (Expected: 96)")
    
    # 3. Test with spaces/plus
    biz_id_3 = get_business_id_by_phone("+65 9270 1525")
    print(f"Match +65 9270 1525 -> {biz_id_3} (Expected: 96)")
    
    # 4. Test missing number
    biz_id_4 = get_business_id_by_phone("9876543210")
    print(f"Match 9876543210 -> {biz_id_4} (Expected: None)")

if __name__ == "__main__":
    test_robust_mappings()
