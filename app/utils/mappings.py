import json
import os
from typing import Optional
from app.config import settings

FRANCHISE_FILE = settings.FRANCHISE_FILE

def _load_json_file(file_path: str, default_value: dict) -> dict:
    if not os.path.exists(file_path):
        return default_value
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data if data is not None else default_value
    except (json.JSONDecodeError, IOError):
        return default_value

def _save_json_file(file_path: str, data: dict):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def _load_franchise_mappings() -> dict:
    return _load_json_file(FRANCHISE_FILE, {})

def get_business_id_by_phone(phone_number: str) -> Optional[dict]:
    """
    Returns the primary business mapping info for a given phone number.
    Uses franchise_mappings.json as the single source.
    """
    if not phone_number:
        return None
        
    num = "".join(filter(str.isdigit, phone_number))
    franchise_data = _load_franchise_mappings()
    
    # Try exact match
    entry = franchise_data.get(num)
    
    # Try with '65' prefix if missing (Singapore default)
    if entry is None and len(num) == 8:
        entry = franchise_data.get("65" + num)
        
    # Try removing '65' prefix if present
    if entry is None and num.startswith("65") and len(num) > 8:
        entry = franchise_data.get(num[2:])
        
    if entry:
        if isinstance(entry, dict) and len(entry) > 0:
            # Pick first business in the franchise as primary
            biz_id_str = next(iter(entry))
            biz_info = entry[biz_id_str]
            
            if isinstance(biz_info, dict):
                return {
                    "bizId": int(biz_id_str),
                    "bizHash": biz_info.get("hash")
                }
            else:
                # Old string format: "id": "code"
                return {
                    "bizId": int(biz_id_str),
                    "bizHash": None
                }
        elif isinstance(entry, list) and len(entry) > 0:
            # Legacy list format
            return {"bizId": int(entry[0]), "bizHash": None}
            
    return None

def add_mapping(phone_number: str, business_id: int, biz_hash: str = None) -> bool:
    """
    Adds a new mapping to franchise_mappings.json.
    """
    normalized_phone = "".join(filter(str.isdigit, phone_number))
    franchise_data = _load_franchise_mappings()
    
    # Check if business_id is already assigned to a DIFFERENT phone number
    for phone, branches in franchise_data.items():
        if phone != normalized_phone:
            if isinstance(branches, dict) and str(business_id) in branches:
                return False
            elif isinstance(branches, list) and business_id in branches:
                return False
            
    if normalized_phone not in franchise_data:
        franchise_data[normalized_phone] = {}
        
    entry = franchise_data[normalized_phone]
    if not isinstance(entry, dict):
        # Migrate old format if necessary
        entry = {str(business_id): entry}
        
    biz_item = entry.get(str(business_id), {})
    if not isinstance(biz_item, dict):
        biz_item = {"code": biz_item}
        
    if biz_hash:
        biz_item["hash"] = biz_hash
        
    entry[str(business_id)] = biz_item
    franchise_data[normalized_phone] = entry
        
    _save_json_file(FRANCHISE_FILE, franchise_data)
    return True

def get_franchise_map_by_phone(phone_number: str) -> dict:
    """
    Returns a dict of business_id -> info (code or dict) for a given phone number.
    Returns an empty dict if not found.
    """
    normalized_phone = "".join(filter(str.isdigit, phone_number))
    franchise_data = _load_franchise_mappings()
    entry = franchise_data.get(normalized_phone, {})
    if isinstance(entry, list):
        # Fallback for old list format: use last 3 digits as code
        return {str(i): str(i)[-3:] for i in entry}
    return entry

def get_franchise_ids_by_phone(phone_number: str) -> list[int]:
    """
    Returns a list of business IDs for a given phone number (franchise).
    Returns an empty list if not found.
    """
    f_map = get_franchise_map_by_phone(phone_number)
    return [int(k) for k in f_map.keys()]

def get_code_by_business_id(business_id: int) -> Optional[str]:
    """
    Returns the code for a given business ID by searching all mappings.
    """
    franchise_data = _load_franchise_mappings()
    for phone_entry in franchise_data.values():
        if isinstance(phone_entry, dict):
            biz_info = phone_entry.get(str(business_id))
            if biz_info:
                if isinstance(biz_info, dict):
                    return biz_info.get("code")
                return biz_info # old string format
    return None
