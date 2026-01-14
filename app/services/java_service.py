import httpx
import logging
from app.models import Lead, Appointment, AppointmentSummary, Invoice, BusinessSummary, LeadCreateRequest, LeadCreateResponse, LeadSummary, LeadListResponse, Service, BookingRequest, BookingResponse
from typing import List, Optional, Dict, Any
from app.services.base import BaseService
from app.config import settings

logger = logging.getLogger(__name__)

class JavaService(BaseService):
    def __init__(self, token: str = None):
        # Initialize base_url from settings
        self.base_url = settings.JAVA_API_BASE_URL
        
        # Initialize headers dictionary
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        logging.info(f">>>> JAVA SERVICE INIT <<<<")
        logging.info(f"!!!! Config Token from .env: {settings.QTICK_JAVA_SERVICE_TOKEN[:10] if settings.QTICK_JAVA_SERVICE_TOKEN else 'None'}...")
        logging.info(f"!!!! Passed Token from Header: {token[:10] if token else 'None'}...")
        
        # Prioritize passed token over config token
        auth_token = token or settings.QTICK_JAVA_SERVICE_TOKEN
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        logging.info(f"!!!! Final Auth Header Used: {headers.get('Authorization')[:20] if headers.get('Authorization') else 'None'}...")
        
        # Ensure base_url ends with a slash for proper relative URL joining
        if self.base_url and not self.base_url.endswith('/'):
            self.base_url += '/'
            
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers, follow_redirects=True)

    async def create_lead(self, request: LeadCreateRequest) -> LeadCreateResponse:
        try:
            from datetime import datetime, timedelta, timezone
            now = datetime.now(timezone.utc)
            
            # Format: 2025-12-20T03:41:00.000+0000
            date_format = "%Y-%m-%dT%H:%M:%S.000+0000"
            enquired_on = request.enquired_on or now.strftime(date_format)
            follow_up_date = request.follow_up_date or (now + timedelta(days=2)).strftime(date_format)
            enquiry_for_time = request.enquiry_for_time or now.strftime(date_format)

            # Service Lookup
            services_payload = []
            if request.service_name:
                try:
                    found_services = await self.search_services(request.business_id, request.service_name)
                    if found_services:
                        # Take the first match
                        s = found_services[0]
                        services_payload.append({
                            "id": s.id,
                            "name": s.name
                        })
                        # Update enquiry_for to the canonical name of the service
                        request.enquiry_for = s.name
                except Exception as e:
                    import logging
                    logging.error(f"Error looking up service '{request.service_name}': {e}")

            payload: Dict[str, Any] = {
                "bizId": request.business_id,
                "phone": request.phone.replace('+', '') if request.phone else None,
                "email": request.email,
                "custName": request.name,
                "enqFor": request.enquiry_for[:100] if request.enquiry_for else None,
                "srcChannel": "PH", # Fixed as per user sample "PH"
                "campId": None,
                "campName": None,
                "details": request.details or "",
                "interest": request.interest or 2,
                "enqForTime": enquiry_for_time,
                "followUpDate": follow_up_date,
                "enquiredOn": enquired_on,
                "attnStaffId": request.attention_staff_id or 475,
                "enqNo": None,
                "custId": None,
                "services": services_payload
            }

            # Include null values as required by API
            # payload = {k: v for k, v in payload.items() if v is not None}

            import logging
            import json
            logging.info(f"Sending create_lead payload:\n{json.dumps(payload, indent=2, default=str)}")

            data = await self._post("api/biz/sales-enq", payload)
            logging.info(f"Received create_lead response:\n{json.dumps(data, indent=2, default=str)}")
            
            # The API returns several fields, we map them back
            return LeadCreateResponse(
                lead_id=str(data.get("enqNo") or data.get("bizId")),
                status=str(data.get("status") or "NEW"), 
                created_at=str(enquired_on),
                next_action="Followup",
                custName=data.get("custName"),
                phone=data.get("phone"),
                enqFor=data.get("enqFor"),
                value=float(data.get("value") or 0.0),
                leadValue=float(data.get("leadValue") or 0.0)
            )
        except Exception as exc:
            import logging
            logging.error(f"Failed to create lead: {exc}", exc_info=True)
            raise Exception(f"Failed to create lead: {exc}")

    async def _post(self, url: str, json_data: dict) -> dict:
        import logging
        import json
        
        # Ensure url does not have double slashes if base_url ends with one
        request_url = url.lstrip('/')
        
        logging.info(f"POST {request_url}")
        logging.info(f"Request Headers: {dict(self.client.headers)}")
        logging.info(f"Request Body: {json.dumps(json_data, indent=2)}")
        
        response = await self.client.post(request_url, json=json_data)
        
        logging.info(f"Response Status: {response.status_code}")
        logging.info(f"Response Headers: {dict(response.headers)}")
        logging.info(f"Response Content: '{response.text}'")
        
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(f"POST {request_url} failed with {response.status_code}: {response.text}")
            raise e

        if not response.content:
            logging.warning(f"POST {request_url} returned empty content")
            return {}

        try:
            return response.json()
        except Exception as e:
            logging.error(f"Failed to parse JSON from POST {request_url}. Content: {response.text}")
            raise e

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
            f"api/biz/{business_id}/sales-enq/list", params=params
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
                value=float(item.get("value", 0.0)),
                leadValue=float(item.get("leadValue", 0.0))
            )
            leads.append(lead)

        return LeadListResponse(
            total=len(leads),
            items=leads
        )

    async def _get(self, url: str, params: dict = None) -> Any:
        import logging
        
        request_url = url.lstrip('/')
        
        logging.info(f"GET {request_url}")
        logging.info(f"Params: {params}")
        logging.info(f"Request Headers: {dict(self.client.headers)}")
        
        response = await self.client.get(request_url, params=params)
        
        logging.info(f"Response Status: {response.status_code}")
        logging.info(f"Response Headers: {dict(response.headers)}")
        logging.info(f"Response Content: '{response.text}'")
        
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(f"GET {request_url} failed with {response.status_code}: {response.text}")
            raise e

        if not response.content:
            logging.warning(f"GET {request_url} returned empty content")
            return {}

        try:
            return response.json()
        except Exception as e:
            logging.error(f"Failed to parse JSON from GET {request_url}. Content: {response.text}")
            raise e

    async def create_appointment(self, request: BookingRequest) -> BookingResponse:
        headers = self.client.headers.copy()
        headers["Authorization"] = "bizprofile-web:D9yGl4wpT1"
        headers["Accept"] = "application/json"
        
        payload = request.dict()
        
        response = await self.client.post("web/v2/booking", json=payload, headers=headers)
        
        if response.is_success:
            return BookingResponse(**response.json())
        
        # Handle error response
        try:
            error_data = response.json()
            if "message" in error_data:
                raise Exception(error_data["message"])
        except ValueError:
            pass
            
        response.raise_for_status()
        raise Exception(f"Unknown error: {response.status_code}")

    async def list_appointments(self, business_id: int, start_date: str, end_date: str, status: str = "QU,BO,PE") -> List[AppointmentSummary]:
        params = {
            "date": start_date,
            "startDate": start_date,
            "endDate": end_date,
            "status": status,
            "sessionId": ""
        }
        
        # Use _get for proper logging and error handling
        response_data = await self._get(f"api/biz/{business_id}/bookings/", params=params)
        
        appointments = []
        for item in response_data:
            # Extract service names
            services = item.get("services", [])
            service_names = ", ".join([s.get("serviceName", "") for s in services])
            
            # Extract customer info
            customer = item.get("customerInfo", {})
            
            summary = AppointmentSummary(
                booking_id=str(item.get("bookingId")),
                customer_name=customer.get("name") or "Unknown",
                service_name=service_names or "No Service",
                start_time=item.get("bkStartTime") or item.get("startTime"),
                status=item.get("status"),
                phone=customer.get("phone") or "N/A"
            )
            appointments.append(summary)
            
        return appointments

    async def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        response = await self.client.get(f"appointments/{appointment_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Appointment(**response.json())

    async def create_invoice(self, invoice: Invoice) -> Invoice:
        response = await self.client.post("invoices", json=invoice.dict(exclude={"id", "created_at"}))
        response.raise_for_status()
        return Invoice(**response.json())

    async def list_invoices(self) -> List[Invoice]:
        response = await self.client.get("invoices")
        response.raise_for_status()
        return [Invoice(**item) for item in response.json()]

    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        response = await self.client.get(f"invoices/{invoice_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Invoice(**response.json())

    async def get_summary_for_business(self, business_id: str, from_date: str, to_date: str) -> BusinessSummary:
        params = {
            "fromDate": from_date,
            "toDate": to_date
        }
        # Fixed to use self._get which handles relative URLs correctly
        data = await self._get(f"api/biz/{business_id}/summary", params=params)
        
        return BusinessSummary(
            business_id=str(business_id),
            total_leads=data.get("leadsCount", 0),
            total_appointments=data.get("appointmentsCount", 0),
            bills_count=data.get("billsCount", 0),
            total_revenue=float(data.get("totalRevenue") or data.get("revenue") or 0.0),
            recent_activities=data.get("recentActivities", [])
        )

    async def search_services(self, business_id: int, text: str, group_id: int = 0) -> List[Service]:
        params = {
            "bizId": int(business_id),
            "text": text,
            "groupId": int(group_id)
        }
        # Fixed to use self._get which handles relative URLs correctly
        response = await self._get("web/biz/services", params=params)
        return [Service(**item) for item in response]

def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def _map_source_to_channel(source: Optional[str]) -> str:
    # Simple mapping logic
    if not source:
        return "Manual"
    return source[:10] # Placeholder logic
