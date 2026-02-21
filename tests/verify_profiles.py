import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

def test_mappings_switch():
    print("Testing Mappings File Switching...")
    
    # Test Default
    os.environ["APP_ENV"] = "local"
    from importlib import reload
    import app.config
    import app.utils.mappings
    reload(app.config)
    reload(app.utils.mappings)
    print(f"APP_ENV='local' -> MAPPINGS_FILE: {app.utils.mappings.MAPPINGS_FILE}")
    
    # Test QA
    os.environ["APP_ENV"] = "qa"
    reload(app.config)
    reload(app.utils.mappings)
    print(f"APP_ENV='qa'    -> MAPPINGS_FILE: {app.utils.mappings.MAPPINGS_FILE}")
    
    # Test PROD
    os.environ["APP_ENV"] = "prod"
    reload(app.config)
    reload(app.utils.mappings)
    print(f"APP_ENV='prod'  -> MAPPINGS_FILE: {app.utils.mappings.MAPPINGS_FILE}")

if __name__ == "__main__":
    test_mappings_switch()
