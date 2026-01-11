from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Optional
from fastapi import Header
from app.agent import Agent
from app.website_agent import WebsiteAgent
import logging
import sys
from app.utils.mappings import get_business_id_by_phone, add_mapping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI(title="QTick MCP Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from app.config import settings
    logging.info("Starting QTick MCP Service...")
    logging.info(f"Configuration:")
    logging.info(f"  USE_MOCK_DATA: {settings.USE_MOCK_DATA}")
    logging.info(f"  LLM_PROVIDER: {settings.LLM_PROVIDER}")
    logging.info(f"  JAVA_API_BASE_URL: {settings.JAVA_API_BASE_URL}")
    logging.info(f"  GEMINI_MODEL: {settings.GEMINI_MODEL}")
    # Mask keys
    openai_key = settings.OPENAI_API_KEY
    if openai_key:
        logging.info(f"  OPENAI_API_KEY: {openai_key[:4]}...{openai_key[-4:]}")
    else:
        logging.info(f"  OPENAI_API_KEY: Not set")
        
    gemini_key = settings.GEMINI_API_KEY
    if gemini_key:
        logging.info(f"  GEMINI_API_KEY: {gemini_key[:4]}...{gemini_key[-4:]}")
    else:
        logging.info(f"  GEMINI_API_KEY: Not set")

    java_token = settings.QTICK_JAVA_SERVICE_TOKEN
    if java_token:
        logging.info(f"  QTICK_JAVA_SERVICE_TOKEN: {java_token[:4]}...{java_token[-4:]}")
    else:
        logging.info(f"  QTICK_JAVA_SERVICE_TOKEN: Not set")

    # Debug JavaService path
    from app.services.java_service import JavaService
    import os
    logging.info(f"  JAVA_SERVICE_FILE: {os.path.abspath(JavaService.__init__.__code__.co_filename)}")

agent = Agent()
website_agent = WebsiteAgent()

class ChatRequest(BaseModel):
    prompt: str
    business_id: int

class ChatResponse(BaseModel):
    prompt: str
    type: str
    response_text: str
    response_value: Any
    whatsAppText: Optional[str] = ""

class WebsiteChatRequest(BaseModel):
    message: str
    history: list = []

class WebsiteChatResponse(BaseModel):
    response_text: str
    action: Optional[str] = None

class BusinessLookupRequest(BaseModel):
    phone: str

class BusinessRegisterRequest(BaseModel):
    phone: str
    business_id: int

class PhoneChatRequest(BaseModel):
    phone: str
    prompt: str



@app.post("/agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    token = None
    if authorization:
        auth_parts = authorization.split(" ")
        if len(auth_parts) > 1 and auth_parts[0].lower() == "bearer":
            token = auth_parts[1]


    try:
        agent_response = await agent.process_prompt(request.prompt, request.business_id, token)
        return ChatResponse(
            prompt=request.prompt,
            type=agent_response.get("type", "Chat"),
            response_text=agent_response.get("response_text", ""),
            response_value=agent_response.get("response_value"),
            whatsAppText=agent_response.get("whatsAppText", "")
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/phone/chat", response_model=ChatResponse)
async def phone_chat(request: PhoneChatRequest, authorization: Optional[str] = Header(None)):
    token = None
    if authorization:
        auth_parts = authorization.split(" ")
        if len(auth_parts) > 1 and auth_parts[0].lower() == "bearer":
            token = auth_parts[1]

    business_id = get_business_id_by_phone(request.phone)
    if not business_id:
        raise HTTPException(status_code=404, detail=f"No business found for phone number {request.phone}")

    try:
        agent_response = await agent.process_prompt(request.prompt, business_id, token)
        return ChatResponse(
            prompt=request.prompt,
            type=agent_response.get("type", "Chat"),
            response_text=agent_response.get("response_text", ""),
            response_value=agent_response.get("response_value"),
            whatsAppText=agent_response.get("whatsAppText", "")
        )
    except Exception as e:
        logging.error(f"Error processing phone chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/website/chat", response_model=WebsiteChatResponse)
async def website_chat(request: WebsiteChatRequest, authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    try:
        response = await website_agent.process_message(request.message, request.history, token)
        return WebsiteChatResponse(
            response_text=response.get("response_text", ""),
            action=response.get("action")
        )
    except Exception as e:
        logging.error(f"Error processing website chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/business/lookup", response_model=int)
async def business_lookup(request: BusinessLookupRequest):
    business_id = get_business_id_by_phone(request.phone)
    if business_id:
        return business_id
    else:
        raise HTTPException(status_code=404, detail="Business not found for the given phone number")

@app.post("/business/register")
async def business_register(request: BusinessRegisterRequest):
    success = add_mapping(request.phone, request.business_id)
    if success:
        return {"message": "Mapping registered successfully", "phone": request.phone, "business_id": request.business_id}
    else:
        raise HTTPException(status_code=400, detail=f"Business ID {request.business_id} is already assigned to another phone number")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/debug/ip")
async def debug_ip():
    import httpx
    r = httpx.get("https://ipinfo.io/json", timeout=5)
    return r.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
