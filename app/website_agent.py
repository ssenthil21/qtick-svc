import logging
import json
from typing import Dict, Any, List
from app.config import settings
from app.services.rag_service import SimpleRAGService
from app.tools.website_tools import capture_lead

logger = logging.getLogger(__name__)

# Tool definition for the LLM - DISABLED for now
# WEBSITE_TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "capture_lead",
#             "description": "Save user contact details when they provide them.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string"},
#                     "phone": {"type": "string"},
#                     "email": {"type": "string"},
#                     "interest": {"type": "string", "description": "What feature they are interested in"}
#                 },
#                 "required": ["name"]
#             }
#         }
#     }
# ]

class WebsiteAgent:
    def __init__(self):
        self.rag = SimpleRAGService()
        self.provider = settings.LLM_PROVIDER

    async def process_message(self, message: str, history: List[Dict[str, str]] = [], token: str = None) -> Dict[str, Any]:
        # 1. Retrieve context via RAG
        context = self.rag.retrieve(message)
        
        # 2. Construct System Prompt
        system_prompt = (
            "You are a helpful QTick Sales Agent. Your goal is to explain QTick features based on the user's questions.\n"
            "Use the provided context to answer questions accurately. If the context doesn't have the answer, say you don't know but can arrange a call.\n"
            "Be concise and friendly. Do not hallucinate features.\n"
            f"CONTEXT:\n{context}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        # Add history (limit to last 5 turns to save tokens)
        messages.extend(history[-5:])
        messages.append({"role": "user", "content": message})

        if self.provider == "openai":
            return await self._process_openai(messages, token)
        elif self.provider == "gemini":
            return await self._process_gemini(messages, token)
        else:
            return {"response_text": "Unsupported LLM provider"}

    async def _process_openai(self, messages: List[Dict[str, str]], token: str = None) -> Dict[str, Any]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            # tools=WEBSITE_TOOLS,
            # tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        # tool_calls = response_message.tool_calls
        
        # if tool_calls:
        #     # Handle tool call (only capture_lead supported)
        #     for tool_call in tool_calls:
        #         if tool_call.function.name == "capture_lead":
        #             args = json.loads(tool_call.function.arguments)
        #             if token:
        #                 args["token"] = token
        #             result = await capture_lead(**args)
        #             return {"response_text": result.text, "action": "lead_captured"}
        
        return {"response_text": response_message.content}

    async def _process_gemini(self, messages: List[Dict[str, str]], token: str = None) -> Dict[str, Any]:
        import google.generativeai as genai
        from google.generativeai.types import FunctionDeclaration, Tool
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # gemini_tools = [
        #     FunctionDeclaration(
        #         name="capture_lead",
        #         description="Save user contact details when they provide them.",
        #         parameters={
        #             "type": "object",
        #             "properties": {
        #                 "name": {"type": "string"},
        #                 "phone": {"type": "string"},
        #                 "email": {"type": "string"},
        #                 "interest": {"type": "string"}
        #             },
        #             "required": ["name"]
        #         }
        #     )
        # ]
        
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            # tools=[Tool(function_declarations=gemini_tools)]
        )
        
        # Convert messages to Gemini format
        chat_history = []
        for msg in messages:
            if msg["role"] == "system":
                # Gemini doesn't support system messages in chat history directly in the same way, 
                # usually passed as system_instruction to model. 
                # For simplicity here, we prepend to user message or use system_instruction in model init.
                # We already set system_instruction in model init in agent.py, but here we are creating a new model instance.
                # Let's use the system prompt logic properly.
                pass 
            else:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
        
        # Extract system prompt from the first message we constructed
        system_instruction = messages[0]["content"]
        
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            # tools=[Tool(function_declarations=gemini_tools)],
            system_instruction=system_instruction
        )

        chat = model.start_chat(history=chat_history[:-1]) # All except last user message
        last_user_msg = messages[-1]["content"]
        
        response = await chat.send_message_async(last_user_msg)
        
        # part = response.candidates[0].content.parts[0]
        
        # if part.function_call:
        #     if part.function_call.name == "capture_lead":
        #         args = dict(part.function_call.args)
        #         if token:
        #             args["token"] = token
        #         result = await capture_lead(**args)
        #         return {"response_text": result.text, "action": "lead_captured"}
        
        return {"response_text": response.text}
