import os
import json
from typing import Dict, Any, List
from app.config import settings
from app.models import ToolResult
from app.tools import leads, appointments, invoices, business, catalog, help, offers

# Tool definitions for the LLM
TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_lead",
            "description": "Create a new lead",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "business_id": {"type": "integer"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "source": {"type": "string"},
                    "notes": {"type": "string"},
                    "location": {"type": "string"},
                    "enquiry_for": {"type": "string", "description": "Subject of enquiry. If not specified, the system will use the original chat message as the default."},
                    "details": {"type": "string"},
                    "interest": {"type": "integer"},
                    "follow_up_date": {"type": "string"},
                    "enquired_on": {"type": "string"},
                    "enquiry_for_time": {"type": "string"},
                    "attention_staff_id": {"type": "integer"},
                    "attention_channel": {"type": "string"},
                    "third_status": {"type": "string"},
                    "service_name": {"type": "string", "description": "The name of the service the lead is interested in"}
                },
                "required": ["name", "business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_leads",
            "description": "List all leads",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "integer"}
                },
                "required": ["business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "Create a new appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "integer"},
                    "phone": {"type": "string"},
                    "service_ids": {"type": "array", "items": {"type": "integer"}},
                    "date_time": {"type": "string", "description": "Appointment date/time. Supports natural language (e.g., 'tomorrow at 10am', 'next Friday', 'Dec 24') or ISO 8601 format."}
                },
                "required": ["business_id", "phone", "service_ids", "date_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_appointments",
            "description": "List all appointments",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "integer"},
                    "period": {"type": "string", "enum": ["today", "yesterday", "this week", "last week", "this month", "last month"], "description": "Quick period selection"},
                    "from_date": {"type": "string", "description": "Start date in YYYY/MM/DD format (optional if period is used)"},
                    "to_date": {"type": "string", "description": "End date in YYYY/MM/DD format (optional if period is used)"}
                },
                "required": ["business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointment",
            "description": "Get appointment details",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"}
                },
                "required": ["appointment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_invoice",
            "description": "Create a new invoice",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "string"},
                    "customer_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "items": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["business_id", "customer_id", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_invoices",
            "description": "List all invoices",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_invoice",
            "description": "Get invoice details",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string"}
                },
                "required": ["invoice_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary_for_business",
            "description": "Get business summary (leads, revenue, appointments). Use the current business ID from context if the user doesn't specify one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "string", "description": "The business ID to summarize. Defaults to the current active business context."},
                    "period": {"type": "string", "enum": ["today", "yesterday", "this week", "last week", "this month", "last month"], "description": "Quick period selection"},
                    "from_date": {"type": "string", "description": "Start date in YYYY/MM/DD format (optional if period is used)"},
                    "to_date": {"type": "string", "description": "End date in YYYY/MM/DD format (optional if period is used)"}
                },
                "required": ["business_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_services",
            "description": "Search for services in the business catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "integer"},
                    "text": {"type": "string", "description": "Search text for service name"},
                    "group_id": {"type": "integer", "description": "Group ID (default 0)"}
                },
                "required": ["business_id", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_help_guide",
            "description": "Get a guide of the assistant's capabilities for greetings, 'hi', 'hello', or help requests",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_franchise_summary",
            "description": "Get a consolidated summary report for multiple branches/businesses mentioned by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_ids": {"type": "string", "description": "Comma separated list of business IDs mentioned by the user (e.g., '96,97')"},
                    "period": {"type": "string", "enum": ["today", "yesterday", "this week", "last week", "this month", "last month"], "description": "Quick period selection"},
                    "from_date": {"type": "string", "description": "Start date in YYYY/MM/DD format (optional if period is used)"},
                    "to_date": {"type": "string", "description": "End date in YYYY/MM/DD format (optional if period is used)"}
                },
                "required": ["business_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_offers",
            "description": "List active offers",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "string", "description": "Business ID to fetch offers for"}
                },
                "required": ["business_id"]
            }
        }
    }
]

import logging

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        
    async def process_prompt(self, prompt: str, business_id: int, token: str = None, client_id: str = None) -> Dict[str, Any]:
        logger.info(f"Processing prompt: {prompt}")
        if self.provider == "openai":
            return await self._process_openai(prompt, business_id, token, client_id)
        elif self.provider == "gemini":
            return await self._process_gemini(prompt, business_id, token, client_id)
        else:
            return {"type": "Error", "response_text": "Unsupported LLM provider", "response_value": None}

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], token: str = None, prompt: str = None, client_id: str = None) -> Any:
        logger.info(f"Executing tool '{tool_name}' with args: {arguments}")
        # Inject token and client_id into arguments if available
        if token:
            arguments["token"] = token
        if client_id:
            arguments["client_id"] = client_id
            
        try:
            if tool_name == "create_lead":
                arguments["prompt"] = prompt
                result = await leads.create_lead(**arguments)
            elif tool_name == "list_leads":
                result = await leads.list_leads(**arguments)
            elif tool_name == "create_appointment":
                result = await appointments.create_appointment(**arguments)
            elif tool_name == "list_appointments":
                result = await appointments.list_appointments(**arguments)
            elif tool_name == "get_appointment":
                result = await appointments.get_appointment(**arguments)
            elif tool_name == "create_invoice":
                result = await invoices.create_invoice(**arguments)
            elif tool_name == "list_invoices":
                result = await invoices.list_invoices(**arguments)
            elif tool_name == "get_invoice":
                result = await invoices.get_invoice(**arguments)
            elif tool_name == "get_summary_for_business":
                result = await business.get_summary_for_business(**arguments)
            elif tool_name == "search_services":
                result = await catalog.search_services(**arguments)
            elif tool_name == "get_help_guide":
                result = await help.get_help_guide()
            elif tool_name == "get_franchise_summary":
                result = await business.get_franchise_summary(**arguments)
            elif tool_name == "list_offers":
                result = await offers.list_offers(**arguments)
            else:
                logger.error(f"Tool '{tool_name}' not found")
                return f"Error: Tool {tool_name} not found"
            
            logger.info(f"Tool '{tool_name}' execution successful")
            return result
                
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return f"Error executing tool {tool_name}: {str(e)}"

    async def _process_openai(self, prompt: str, business_id: int, token: str = None, client_id: str = None) -> Dict[str, Any]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = (
            "You are a helpful assistant for QTick. "
            f"CURRENT BUSINESS CONTEXT: ID {business_id}. "
            "Use this ID as the default for any tool calls (leads, appointments, summaries) unless the user explicitly mentions different business IDs. "
            "For greetings (e.g., 'hi', 'hello', 'hey', 'hi there') or general help requests ('guide me', 'what can you do?', 'help'), YOU MUST call the `get_help_guide` tool. DO NOT reply with text directly for greetings. The `get_help_guide` tool is mandatory for any initial greeting or general inquiry about your capabilities. "
            "When listing items (leads, appointments, invoices, services), return ONLY a clean Markdown table. "
            "Use Title Case for headers. "
            "For tools that accept a `period` argument (summaries, appointments), if the user uses relative time terms like 'last month', 'this week', 'yesterday', etc., YOU MUST pass that term into the `period` argument rather than calculating dates yourself. "
            "For appointment booking, if a service name is provided (not an ID), YOU MUST first use `search_services` to find the Service ID. "
            "If exactly one service is found, proceed to `create_appointment` with that ID. "
            "If multiple services are found, list them (ID, Name, Price) and ask the user to specify one. "
            "DO NOT guess the Service ID."
        )

        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS_DEFINITIONS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        last_tool_name = "Chat"
        last_tool_result = None
        
        if tool_calls:
            logger.info(f"Agent decided to call {len(tool_calls)} tools")
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Agent calling tool: {function_name}")
                raw_result = await self._execute_tool(function_name, function_args, token, prompt, client_id)
                
                last_tool_name = function_name
                last_tool_result = raw_result
                
                # Convert to JSON for LLM consumption
                if isinstance(raw_result, ToolResult):
                    inner_result = raw_result.data
                    if isinstance(inner_result, list):
                        json_result = json.dumps([item.dict() for item in inner_result], default=str)
                    elif hasattr(inner_result, "dict"):
                        json_result = json.dumps(inner_result.dict(), default=str)
                    else:
                        json_result = str(inner_result)
                elif isinstance(raw_result, list):
                    json_result = json.dumps([item.dict() for item in raw_result], default=str)
                elif hasattr(raw_result, "dict"):
                    json_result = json.dumps(raw_result.dict(), default=str)
                else:
                    json_result = str(raw_result)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json_result,
                })
            
            second_response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            response_text = second_response.choices[0].message.content
        else:
            response_text = response_message.content

        # Prepare response value for API
        response_value = None
        response_type = last_tool_name
        whatsapp_text = ""
        
        if last_tool_result:
            if isinstance(last_tool_result, ToolResult):
                response_value = last_tool_result.data
                if hasattr(response_value, "dict"):
                    response_value = response_value.dict()
                # Prefer the text from the tool result if it's provided
                if last_tool_result.text:
                    response_text = last_tool_result.text
                
                # Use the type from the tool result
                response_type = last_tool_result.type
                # Capture WhatsApp text
                if last_tool_result.whatsAppText:
                    whatsapp_text = last_tool_result.whatsAppText
            elif isinstance(last_tool_result, list):
                response_value = [item.dict() for item in last_tool_result]
            elif hasattr(last_tool_result, "dict"):
                response_value = last_tool_result.dict()
            else:
                response_value = last_tool_result

        return {
            "type": response_type,
            "response_text": response_text,
            "response_value": response_value,
            "whatsAppText": whatsapp_text if whatsapp_text else response_text
        }

    async def _process_gemini(self, prompt: str, business_id: int, token: str = None, client_id: str = None) -> Dict[str, Any]:
        import google.generativeai as genai
        from google.generativeai.types import FunctionDeclaration, Tool
        from google.ai.generativelanguage import Part, FunctionResponse
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Map our tool definitions to Gemini's format
        gemini_tools = []
        for tool_def in TOOLS_DEFINITIONS:
            func_def = tool_def["function"]
            gemini_tool = FunctionDeclaration(
                name=func_def["name"],
                description=func_def["description"],
                parameters=func_def["parameters"]
            )
            gemini_tools.append(gemini_tool)
        
        system_instruction = (
            "You are a helpful assistant for QTick. "
            f"CURRENT BUSINESS CONTEXT: ID {business_id}. "
            "Use this ID as the default for any tool calls (leads, appointments, summaries) unless the user explicitly mentions different business IDs. "
            "For greetings (e.g., 'hi', 'hello', 'hey', 'hi there') or general help requests ('guide me', 'what can you do?', 'help'), YOU MUST call the `get_help_guide` tool. DO NOT reply with text directly for greetings. The `get_help_guide` tool is mandatory for any initial greeting or general inquiry about your capabilities. "
            "When listing items (leads, appointments, invoices, services), return ONLY a clean Markdown table. "
            "Use Title Case for headers. "
            "For tools that accept a `period` argument (summaries, appointments), if the user uses relative time terms like 'last month', 'this week', 'yesterday', etc., YOU MUST pass that term into the `period` argument rather than calculating dates yourself. "
            "For appointment booking, if a service name is provided (not an ID), YOU MUST first use `search_services` to find the Service ID. "
            "If exactly one service is found, proceed to `create_appointment` with that ID. "
            "If multiple services are found, list them (ID, Name, Price) and ask the user to specify one. "
            "DO NOT guess the Service ID."
        )

        # Create the model with tools (declarations only)
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            tools=[Tool(function_declarations=gemini_tools)],
            system_instruction=system_instruction
        )
        
        # Disable automatic function calling so we can handle async execution manually
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        logger.info("Sending prompt to Gemini...")
        response = await chat.send_message_async(prompt)
        
        last_tool_name = "Chat"
        last_tool_result = None
        
        # Loop until the model stops calling functions
        while True:
            # Check for candidates and parts
            if not response.candidates:
                logger.error(f"Gemini returned no candidates: {response}")
                break

            candidate = response.candidates[0]
            parts = candidate.content.parts
            
            if not parts:
                logger.info("Response has no parts (possibly terminal or safety blocked)")
                break

            # Check if there are any function calls in any of the parts
            function_calls = [p.function_call for p in parts if p.function_call]
            
            if not function_calls:
                logger.info("No more function calls in this turn")
                break
                
            # Process all function calls in this turn
            responses = []
            for fc in function_calls:
                function_name = fc.name
                function_args = dict(fc.args)
                
                logger.info(f"Gemini requested tool call: {function_name}")
                
                # Execute the tool
                raw_result = await self._execute_tool(function_name, function_args, token, prompt, client_id)
                
                last_tool_name = function_name
                last_tool_result = raw_result
                
                # Convert to dict for LLM consumption
                if isinstance(raw_result, ToolResult):
                    inner_result = raw_result.data
                    if isinstance(inner_result, list):
                        msg_result = [json.loads(item.json()) if hasattr(item, "json") else item.dict() if hasattr(item, "dict") else item for item in inner_result]
                    elif hasattr(inner_result, "json"):
                        msg_result = json.loads(inner_result.json())
                    elif hasattr(inner_result, "dict"):
                        msg_result = inner_result.dict()
                    else:
                        msg_result = {"result": str(inner_result)}
                elif isinstance(raw_result, list):
                    msg_result = [item.dict() if hasattr(item, "dict") else item for item in raw_result]
                elif hasattr(raw_result, "dict"):
                    msg_result = raw_result.dict()
                else:
                    msg_result = {"result": str(raw_result)}
                
                logger.debug(f"Tool Formatted Result for Gemini: {msg_result}")
                
                # Add to responses list
                responses.append(Part(function_response=FunctionResponse(
                    name=function_name,
                    response=msg_result if isinstance(msg_result, dict) else {"result": msg_result}
                )))
            
            # Send all responses back in one message
            logger.info(f"Sending {len(responses)} tool results back to Gemini")
            response = await chat.send_message_async(responses)

        # Final terminal response processing
        response_text = ""
        response_value = None
        response_type = last_tool_name
        whatsapp_text = ""

        # Concatenate text from all parts if available
        if response.candidates and response.candidates[0].content.parts:
            text_parts = [p.text for p in response.candidates[0].content.parts if p.text]
            response_text = "\n".join(text_parts).strip()

        # If we have a tool result, prefer its text and data
        if last_tool_result:
            if isinstance(last_tool_result, ToolResult):
                response_value = last_tool_result.data
                if hasattr(response_value, "dict"):
                    response_value = response_value.dict()
                
                # Prefer the tool result text
                if last_tool_result.text:
                    response_text = last_tool_result.text
                
                response_type = last_tool_result.type
                # Capture WhatsApp text
                if last_tool_result.whatsAppText:
                    whatsapp_text = last_tool_result.whatsAppText
            elif isinstance(last_tool_result, list):
                response_value = [item.dict() if hasattr(item, "dict") else item for item in last_tool_result]
            elif hasattr(last_tool_result, "dict"):
                response_value = last_tool_result.dict()
            else:
                response_value = last_tool_result
        
        # Fallback for empty text
        if not response_text:
            response_text = "I've completed your request."

        return {
            "type": response_type,
            "response_text": response_text,
            "response_value": response_value,
            "whatsAppText": whatsapp_text if whatsapp_text else response_text
        }
