from abc import ABC, abstractmethod
from typing import List, Optional
from app.models import Lead, Appointment, Invoice, BusinessSummary, LeadCreateRequest, LeadCreateResponse, LeadSummary, LeadListResponse

class BaseService(ABC):
    
    # Leads
    @abstractmethod
    async def create_lead(self, request: 'LeadCreateRequest') -> 'LeadCreateResponse':
        pass

    @abstractmethod
    async def list_leads(self, business_id: int) -> 'LeadListResponse':
        pass

    # Appointments
    @abstractmethod
    async def create_appointment(self, appointment: Appointment) -> Appointment:
        pass

    @abstractmethod
    async def list_appointments(self) -> List[Appointment]:
        pass

    @abstractmethod
    async def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        pass

    # Invoices
    @abstractmethod
    async def create_invoice(self, invoice: Invoice) -> Invoice:
        pass

    @abstractmethod
    async def list_invoices(self) -> List[Invoice]:
        pass

    @abstractmethod
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        pass

    # Business
    @abstractmethod
    async def get_summary_for_business(self, business_id: str) -> BusinessSummary:
        pass
