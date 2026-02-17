import asyncio
from app.services.java_service import JavaService
from app.config import settings

async def main():
    print("Initializing JavaService...")
    # Initialize without client_id, and ensure no token is passed if we want to test that.
    # But the key is that search_services should ignore whatever is there.
    service = JavaService(token="DUMMY_TOKEN")
    
    print("Calling search_services...")
    try:
        # 96 is the business_id used in other tests
        results = await service.search_services(business_id=96, text="facial")
        print(f"Success! Found {len(results)} services.")
        for s in results:
            print(f"- {s.name} ({s.id})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
