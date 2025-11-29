import asyncio
import os
from app.services.mock_service import MockService
from app.models import Lead, Appointment

async def test_mock_flow():
    print("Testing Mock Service Flow...")
    service = MockService()
    
    # Test Create Lead
    print("1. Creating Lead...")
    # lead = Lead(name="John Doe", email="john@example.com") # Old way
    
    # New way using tool wrapper or direct service call with request model
    # Since we are testing service directly, we use the model
    from app.models import LeadCreateRequest
    request = LeadCreateRequest(
        business_id=123,
        name="John Doe", 
        email="john@example.com",
        phone="555-1234"
    )
    created_lead_response = await service.create_lead(request)
    print(f"   Created Lead: {created_lead_response.lead_id} - Status: {created_lead_response.status}")
    assert created_lead_response.lead_id is not None
    
    # Test List Leads
    print("2. Listing Leads...")
    lead_list = await service.list_leads(business_id=123)
    print(f"   Found {lead_list.total} leads")
    assert lead_list.total == 1
    assert lead_list.items[0].name == "John Doe"
    
    # Test Create Appointment
    print("3. Creating Appointment...")
    appt = Appointment(
        customer_id="CUST-001",
        service_name="Consultation Service",
        start_time="2023-10-27T10:00:00",
        end_time="2023-10-27T11:00:00"
    )
    created_appt = await service.create_appointment(appt)
    print(f"   Created Appointment: {created_appt.id} - {created_appt.service_name}")
    assert created_appt.id is not None
    
    # Test List Appointments
    print("4. Listing Appointments...")
    appts = await service.list_appointments()
    print(f"   Found {len(appts)} appointments")
    assert len(appts) == 1
    
    print("Mock Service Flow Verification Successful!")

if __name__ == "__main__":
    asyncio.run(test_mock_flow())
