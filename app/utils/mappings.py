import json
import os
from typing import Optional
from app.config import settings

MAPPINGS_FILE = settings.MAPPINGS_FILE

# These are now loaded from JSON via settings
MAPPINGS_FILE = settings.MAPPINGS_FILE
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

def _load_mappings() -> dict:
    return _load_json_file(MAPPINGS_FILE, {})

def _save_mappings(mappings: dict):
    _save_json_file(MAPPINGS_FILE, mappings)

def _load_franchise_mappings() -> dict:
    return _load_json_file(FRANCHISE_FILE, {})

def get_business_id_by_phone(phone_number: str) -> Optional[int]:
    """
    Returns the business ID for a given phone number.
    Returns None if the phone number is not found.
    """
    normalized_phone = "".join(filter(str.isdigit, phone_number))
    mappings = _load_mappings()
    entry = mappings.get(normalized_phone)
    if entry is None:
        return None
    if isinstance(entry, dict):
        biz_id = entry.get("id")
        return int(biz_id) if biz_id is not None else None
    return int(entry)

def add_mapping(phone_number: str, business_id: int) -> bool:
    """
    Adds a new mapping. A business ID can only be assigned to one phone number.
    Returns True if successful, False if the business ID is already assigned.
    """
    normalized_phone = "".join(filter(str.isdigit, phone_number))
    mappings = _load_mappings()
    
    # Check if business_id is already assigned to a DIFFERENT phone number
    for phone, entry in mappings.items():
        if isinstance(entry, dict):
            mapped_id = entry.get("id")
        else:
            mapped_id = entry
            
        if mapped_id is not None and int(mapped_id) == int(business_id) and phone != normalized_phone:
            return False
            
    # Preserve existing structure if it's a dict
    existing = mappings.get(normalized_phone)
    if isinstance(existing, dict):
        existing["id"] = business_id
        mappings[normalized_phone] = existing
    else:
        mappings[normalized_phone] = business_id
        
    _save_mappings(mappings)
    return True

def get_franchise_map_by_phone(phone_number: str) -> dict:
    """
    Returns a dict of business_id -> code for a given phone number.
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
    mappings = _load_mappings()
    for entry in mappings.values():
        if isinstance(entry, dict) and int(entry.get("id")) == int(business_id):
            return entry.get("code")
    return None
