import httpx
from app.models import Lead, Appointment, Invoice, BusinessSummary, LeadCreateRequest, LeadCreateResponse, LeadSummary, LeadListResponse, Service, BookingRequest, BookingResponse
from typing import List, Optional, Dict, Any
from app.services.base import BaseService
from app.config import settings

class JavaService(BaseService):
    def __init__(self, token: str = None):
        self.base_url = settings.JAVA_API_BASE_URL
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        elif settings.QTICK_JAVA_SERVICE_TOKEN:
            headers["Authorization"] = f"Bearer {settings.QTICK_JAVA_SERVICE_TOKEN}"
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers)

    async def create_lead(self, request: LeadCreateRequest) -> LeadCreateResponse:
        try:
            now_iso = _utc_now_iso()
            follow_up_date = request.follow_up_date or now_iso
            enquired_on = request.enquired_on or now_iso
            enquiry_for_time = request.enquiry_for_time or now_iso

            details_lines: List[str] = []
            if request.details:
                details_lines.append(request.details)
            if request.notes and request.notes not in details_lines:
                details_lines.append(request.notes)
            if request.source and request.source not in ("", None):
                details_lines.append(f"Source: {request.source}")

            payload: Dict[str, Any] = {
                "bizId": request.business_id,
                "phone": request.phone.replace('+', '') if request.phone else None,
                "custName": request.name,
                "location": request.location,
                "enqFor": request.enquiry_for,
                "srcChannel": _map_source_to_channel(request.source),
                "campId": 38,
                "campName": 'Campaign',
                "location":"Serangoon",
                "enqFor":"Offer",
                "details": "",
                "thdStatus": "A",
                "interest": 3,
                "followUpDate": follow_up_date,
                "enquiredOn": enquired_on,
                "enqForTime": enquiry_for_time,
                "attnStaffId": request.attention_staff_id or 21,
                "attnChannel": request.attention_channel or "P",
            }
            # payload = _filter_payload(payload, preserve_keys={"campId", "campName"}) # Simplified: sending full payload for now

            import logging
            logging.info(f"Sending create_lead payload: {payload}")

            data = await self._post("/biz/sales-enq", payload)
            
            record = {
                "bizId": data.get("bizId"),
                "custId": data.get("custId"),
                "enqNo": data.get("enqNo"),
                "custName": data.get("custName"),
                "phone": data.get("phone"),
                "enqFor": data.get("enqFor"),
                "status": data.get("status"),
                "followUpDate": data.get("followUpDate"),
                "thdStatus": data.get("thdStatus"),
                "threadCount": data.get("threadCount"),
            }
            
            print(record)
            return LeadCreateResponse(
                lead_id=str(record["bizId"]),         # fixed
                status=str(record["status"]), 
                created_at=str(enquired_on),
                next_action=str("Followup"),
            )
        except Exception as exc:
            raise Exception(f"Failed to create lead: {exc}")

    async def _post(self, url: str, json_data: dict) -> dict:
        import logging
        # Log headers to debug authentication (be careful with secrets in prod!)
        logging.info(f"POST {url}")
        logging.info(f"Headers: {dict(self.client.headers)}")
        response = await self.client.post(url, json=json_data)
        response.raise_for_status()
        return response.json()

    async def list_leads(self, business_id: int) -> LeadListResponse:
        params = {
            "searchText": "",
            "status": "",
            "periodType": "",
            "periodFilterBy": "A",
            "fromDate": "",
            "toDate": "",
        }
        data = await self._get(
            f"/api/biz/{business_id}/sales-enq/list", params=params
        )
        
        leads: List[LeadSummary] = []

        for item in data:
            lead = LeadSummary(
                lead_id=str(item.get("enqNo")),           # using enqNo as unique lead id
                name=item.get("custName") or "Unknown",
                status=str(item.get("status", "")),
                created_at=item.get("enquiredOn", ""),
                phone=item.get("phone") or "N/A",
                email=item.get("email") or "N/A",         # Java API might not have email, default to N/A
                source=item.get("srcChannel") or "N/A",
                value=float(item.get("value", 0.0))       # Default value to 0.0
            )
            leads.append(lead)

        return LeadListResponse(
            total=len(leads),
            items=leads
        )

    async def _get(self, url: str, params: dict = None) -> dict:
        import logging
        logging.info(f"GET {url}")
        logging.info(f"Headers: {dict(self.client.headers)}")
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def create_appointment(self, request: BookingRequest) -> BookingResponse:
        headers = self.client.headers.copy()
        headers["Authorization"] = "bizprofile-web:D9yGl4wpT1"
        headers["Accept"] = "application/json"
        
        # We need to ensure we don't double-wrap the payload if httpx does it automatically
        # But here we are passing a Pydantic model dict
        payload = request.dict()
        
        response = await self.client.post("/web/v2/booking", json=payload, headers=headers)
        
        if response.is_success:
            return BookingResponse(**response.json())
        
        # Handle error response
        try:
            error_data = response.json()
            if "message" in error_data:
                raise Exception(error_data["message"])
        except ValueError:
            # Not JSON or parsing failed, fall through to raise_for_status
            pass
            
        response.raise_for_status()
        # Should not be reached if raise_for_status raises, but for type safety:
        raise Exception(f"Unknown error: {response.status_code}")

    async def list_appointments(self) -> List[Appointment]:
        response = await self.client.get("/appointments")
        response.raise_for_status()
        return [Appointment(**item) for item in response.json()]

    async def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        response = await self.client.get(f"/appointments/{appointment_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Appointment(**response.json())

    async def create_invoice(self, invoice: Invoice) -> Invoice:
        response = await self.client.post("/invoices", json=invoice.dict(exclude={"id", "created_at"}))
        response.raise_for_status()
        return Invoice(**response.json())

    async def list_invoices(self) -> List[Invoice]:
        response = await self.client.get("/invoices")
        response.raise_for_status()
        return [Invoice(**item) for item in response.json()]

    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        response = await self.client.get(f"/invoices/{invoice_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Invoice(**response.json())

    async def get_summary_for_business(self, business_id: str, from_date: str, to_date: str) -> BusinessSummary:
        params = {
            "fromDate": from_date,
            "toDate": to_date
        }
        # The user request specified POST for this endpoint
        response = await self.client.get(f"/api/biz/{business_id}/summary", params=params)
        response.raise_for_status()
        data = response.json()
        
        return BusinessSummary(
            business_id=str(business_id),
            total_leads=data.get("leadsCount", 0),
            total_appointments=data.get("appointmentsCount", 0),
            total_revenue=float(data.get("totalRevenue", 0.0)),
            recent_activities=data.get("recentActivities", [])
        )

    async def search_services(self, business_id: int, text: str, group_id: int = 0) -> List[Service]:
        params = {
            "bizId": int(business_id),
            "text": text,
            "groupId": int(group_id)
        }
        response = await self.client.get("/web/biz/services", params=params)
        response.raise_for_status()
        return [Service(**item) for item in response.json()]

def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def _map_source_to_channel(source: Optional[str]) -> str:
    # Simple mapping logic
    if not source:
        return "Manual"
    return source[:10] # Placeholder logic
