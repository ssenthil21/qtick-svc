import json
import os
from typing import Optional

MAPPINGS_FILE = "data/phone_mappings.json"

INITIAL_DATA = {
    "6592701525": 96,
    "6590306703": 11,
    "919080534415": 11,
}

def _load_mappings() -> dict:
    if not os.path.exists(MAPPINGS_FILE):
        return INITIAL_DATA
    
    try:
        with open(MAPPINGS_FILE, "r") as f:
            data = json.load(f)
            return data if data else INITIAL_DATA
    except (json.JSONDecodeError, IOError):
        return INITIAL_DATA

def _save_mappings(mappings: dict):
    os.makedirs(os.path.dirname(MAPPINGS_FILE), exist_ok=True)
    with open(MAPPINGS_FILE, "w") as f:
        json.dump(mappings, f, indent=4)

def get_business_id_by_phone(phone_number: str) -> Optional[int]:
    """
    Returns the business ID for a given phone number.
    Returns None if the phone number is not found.
    """
    normalized_phone = "".join(filter(str.isdigit, phone_number))
    mappings = _load_mappings()
    return mappings.get(normalized_phone)

def add_mapping(phone_number: str, business_id: int) -> bool:
    """
    Adds a new mapping. A business ID can only be assigned to one phone number.
    Returns True if successful, False if the business ID is already assigned.
    """
    normalized_phone = "".join(filter(str.isdigit, phone_number))
    mappings = _load_mappings()
    
    # Check if business_id is already assigned to a DIFFERENT phone number
    for phone, biz_id in mappings.items():
        if biz_id == business_id and phone != normalized_phone:
            return False
            
    mappings[normalized_phone] = business_id
    _save_mappings(mappings)
    return True
