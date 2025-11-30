from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
from app.agent import Agent
import logging
import sys

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

agent = Agent()

class ChatRequest(BaseModel):
    prompt: str
    business_id: int

class ChatResponse(BaseModel):
    prompt: str
    type: str
    response_text: str
    response_value: Any

from fastapi import Header
from typing import Optional

@app.post("/agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    try:
        agent_response = await agent.process_prompt(request.prompt, request.business_id, token)
        return ChatResponse(
            prompt=request.prompt,
            type=agent_response.get("type", "Chat"),
            response_text=agent_response.get("response_text", ""),
            response_value=agent_response.get("response_value")
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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
