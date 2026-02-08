import uuid
from datetime import datetime
from typing import List, Optional
from app.models import Lead, Appointment, Invoice, BusinessSummary, LeadCreateRequest, LeadCreateResponse, LeadSummary, LeadListResponse, Service, BookingRequest, BookingResponse, Offer
from app.services.base import BaseService

class MockService(BaseService):
    def __init__(self, token: str = None):
        self.leads: List[Lead] = []
        self.appointments: List[Appointment] = []
        self.invoices: List[Invoice] = []

    async def create_lead(self, request: LeadCreateRequest) -> LeadCreateResponse:
        lead = Lead(
            id=str(uuid.uuid4()),
            name=request.name,
            email=request.email or "",
            phone=request.phone,
            created_at=datetime.now()
        )
        self.leads.append(lead)
        return LeadCreateResponse(
            lead_id=lead.id,
            status="new",
            created_at=lead.created_at.isoformat(),
            next_action="Followup",
            custName=request.name,
            phone=request.phone,
            enqFor=request.enquiry_for,
            value=0.0,
            leadValue=0.0
        )

    async def list_leads(self, business_id: int) -> LeadListResponse:
        summaries = [
            LeadSummary(
                lead_id=l.id,
                name=l.name,
                status=l.status,
                created_at=l.created_at.isoformat() if l.created_at else "",
                phone=l.phone or "N/A",
                email=l.email or "N/A",
                source="mock",
                value=0.0,
                leadValue=0.0
            ) for l in self.leads
        ]
        return LeadListResponse(total=len(summaries), items=summaries)

    async def create_appointment(self, request: BookingRequest) -> BookingResponse:
        return BookingResponse(
            bookingId=123,
            date=request.dateTime.split('T')[0],
            time=request.dateTime.split('T')[1].split('.')[0],
            custName="Mock Customer",
            bizInfo={"name": "Mock Business", "id": request.bizId},
            services=[f"Service {sid}" for sid in request.serviceIds]
        )

    async def list_appointments(self) -> List[Appointment]:
        return self.appointments

    async def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        for appt in self.appointments:
            if appt.id == appointment_id:
                return appt
        return None

    async def create_invoice(self, invoice: Invoice) -> Invoice:
        invoice.id = str(uuid.uuid4())
        invoice.created_at = datetime.now()
        self.invoices.append(invoice)
        return invoice

    async def list_invoices(self) -> List[Invoice]:
        return self.invoices

    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        for inv in self.invoices:
            if inv.id == invoice_id:
                return inv
        return None

    async def get_summary_for_business(self, business_id: str, from_date: str = None, to_date: str = None) -> BusinessSummary:
        # Mock logic to calculate summary
        total_leads = len(self.leads) # In real app, filter by business_id
        total_appointments = len(self.appointments)
        total_revenue = sum(inv.amount for inv in self.invoices)
        
        return BusinessSummary(
            business_id=business_id,
            total_leads=total_leads,
            total_appointments=total_appointments,
            bills_count=total_appointments,
            total_revenue=total_revenue,
            recent_activities=["New lead created", "Invoice paid"]
        )

    async def search_services(self, business_id: int, text: str, group_id: int = 0) -> List[Service]:
        return [
            Service(id=454, name="Simple Facial", price=590.0, gender=None, type="S")
        ]

    async def list_offers(self, business_id: str) -> List[Offer]:
        return [
            Offer(
                title="Summer Special",
                details="Get 20% off on all facials",
                startDate="2024-06-01T10:00:00",
                endDate="2024-06-30T20:00:00",
                bp_link="https://qtick.biz/offers/summer-special",
                activeCampaigns={"whatsapp": "link"}
            ),
            Offer(
                title="Weekend Bonanza",
                details="Buy 1 Get 1 Free on hair spa",
                startDate="2024-06-07T10:00:00",
                endDate="2024-06-09T20:00:00",
                bp_link="https://qtick.biz/offers/weekend-bonanza",
                activeCampaigns={}
            )
        ]
