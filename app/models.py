from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ToolResult(BaseModel):
    type: str
    data: Any
    text: str
from datetime import datetime

class Lead(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    status: str = "new"
    created_at: Optional[datetime] = None

class LeadCreateRequest(BaseModel):
    business_id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = "manual"
    notes: Optional[str] = None
    location: Optional[str] = None
    enquiry_for: Optional[str] = None
    details: Optional[str] = None
    interest: Optional[int] = None
    follow_up_date: Optional[str] = None
    enquired_on: Optional[str] = None
    enquiry_for_time: Optional[str] = None
    attention_staff_id: Optional[int] = None
    attention_channel: Optional[str] = None
    third_status: Optional[str] = None
    service_name: Optional[str] = None

class LeadCreateResponse(BaseModel):
    lead_id: str
    status: str
    created_at: str
    next_action: str
    follow_up_required: bool = True
    custName: Optional[str] = None
    phone: Optional[str] = None
    enqFor: Optional[str] = None
    value: float = 0.0

class LeadSummary(BaseModel):
    lead_id: str
    name: str
    status: str
    created_at: str
    phone: Optional[str] = "N/A"
    email: Optional[str] = "N/A"
    source: Optional[str] = "N/A"
    value: float = 0.0

class LeadListResponse(BaseModel):
    total: int
    items: List[LeadSummary]

class Appointment(BaseModel):
    id: Optional[str] = None
    customer_id: str
    service_name: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    status: str = "scheduled"

class Invoice(BaseModel):
    id: Optional[str] = None
    business_id: str
    customer_id: str
    amount: float
    currency: str = "USD"
    status: str = "draft"
    items: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None

class BusinessSummary(BaseModel):
    business_id: str
    total_leads: int
    total_appointments: int
    total_revenue: float
    recent_activities: List[str]

class Service(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    gender: Optional[str] = None
    type: Optional[str] = None

class BookingRequest(BaseModel):
    bizId: int
    phone: str
    serviceIds: List[int]
    dateTime: str

class BookingResponse(BaseModel):
    bookingId: int
    date: str
    time: str
    custName: str
    bizInfo: Dict[str, Any]
    services: List[str]
    additionalDescription: Optional[str] = None
    accessToken: Optional[str] = None
