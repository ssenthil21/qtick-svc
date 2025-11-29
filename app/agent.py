import os
import json
from typing import Dict, Any, List
from app.config import settings
from app.models import ToolResult
from app.tools import leads, appointments, invoices, business

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
                    "enquiry_for": {"type": "string"},
                    "details": {"type": "string"},
                    "interest": {"type": "integer"},
                    "follow_up_date": {"type": "string"},
                    "enquired_on": {"type": "string"},
                    "enquiry_for_time": {"type": "string"},
                    "attention_staff_id": {"type": "integer"},
                    "attention_channel": {"type": "string"},
                    "third_status": {"type": "string"}
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
                    "customer_id": {"type": "string"},
                    "service_name": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO 8601 format"},
                    "end_time": {"type": "string", "description": "ISO 8601 format"},
                    "description": {"type": "string"}
                },
                "required": ["customer_id", "service_name", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_appointments",
            "description": "List all appointments",
            "parameters": {"type": "object", "properties": {}}
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
            "description": "Get business summary",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "string"}
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
        
    async def process_prompt(self, prompt: str, business_id: int, token: str = None) -> Dict[str, Any]:
        # Append business context to prompt
        updated_prompt = f"{prompt} for business Id {business_id}"
        logger.info(f"Processing prompt: {updated_prompt}")
        if self.provider == "openai":
            return await self._process_openai(updated_prompt, token)
        elif self.provider == "gemini":
            return await self._process_gemini(updated_prompt, token)
        else:
            return {"type": "Error", "response_text": "Unsupported LLM provider", "response_value": None}

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], token: str = None) -> Any:
        logger.info(f"Executing tool '{tool_name}' with args: {arguments}")
        # Inject token into arguments if available
        if token:
            arguments["token"] = token
            
        try:
            if tool_name == "create_lead":
                result = await leads.create_lead(**arguments)
            elif tool_name == "list_leads":
                result = await leads.list_leads(**arguments)
            elif tool_name == "create_appointment":
                result = await appointments.create_appointment(**arguments)
            elif tool_name == "list_appointments":
                result = await appointments.list_appointments()
            elif tool_name == "get_appointment":
                result = await appointments.get_appointment(**arguments)
            elif tool_name == "create_invoice":
                result = await invoices.create_invoice(**arguments)
            elif tool_name == "list_invoices":
                result = await invoices.list_invoices()
            elif tool_name == "get_invoice":
                result = await invoices.get_invoice(**arguments)
            elif tool_name == "get_summary_for_business":
                result = await business.get_summary_for_business(**arguments)
            else:
                logger.error(f"Tool '{tool_name}' not found")
                return f"Error: Tool {tool_name} not found"
            
            logger.info(f"Tool '{tool_name}' execution successful")
            return result
                
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return f"Error executing tool {tool_name}: {str(e)}"

    async def _process_openai(self, prompt: str, token: str = None) -> Dict[str, Any]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        messages = [{"role": "system", "content": "You are a helpful assistant for QTick. When listing items (leads, appointments, invoices), return ONLY a clean Markdown table. Use Title Case for headers (e.g., 'Lead ID', 'Name', 'Status', 'Created At', 'Phone', 'Email', 'Source', 'Value'). Do not include conversational filler."},
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
                raw_result = await self._execute_tool(function_name, function_args, token)
                
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
        
        if last_tool_result:
            if isinstance(last_tool_result, ToolResult):
                response_value = last_tool_result.data
                if hasattr(response_value, "dict"):
                    response_value = response_value.dict()
                # Use the text from the tool result as the main response text
                response_text = last_tool_result.text
                # Use the type from the tool result
                response_type = last_tool_result.type
            elif isinstance(last_tool_result, list):
                response_value = [item.dict() for item in last_tool_result]
            elif hasattr(last_tool_result, "dict"):
                response_value = last_tool_result.dict()
            else:
                response_value = last_tool_result

        return {
            "type": response_type,
            "response_text": response_text,
            "response_value": response_value
        }

    async def _process_gemini(self, prompt: str, token: str = None) -> Dict[str, Any]:
        import google.generativeai as genai
        from google.generativeai.types import FunctionDeclaration, Tool
        
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
            
        # Create the model with tools (declarations only)
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            tools=[Tool(function_declarations=gemini_tools)],
            system_instruction="You are a helpful assistant for QTick. When listing items (leads, appointments, invoices), return ONLY a clean Markdown table. Use Title Case for headers (e.g., 'Lead ID', 'Name', 'Status', 'Created At', 'Phone', 'Email', 'Source', 'Value'). Do not include conversational filler."
        )
        
        # Disable automatic function calling so we can handle async execution manually
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        logger.info("Sending prompt to Gemini...")
        response = await chat.send_message_async(prompt)
        
        last_tool_name = "Chat"
        last_tool_result = None
        
        # Check if the model wants to call a function
        # Gemini returns function calls in candidates[0].content.parts
        # We need to loop until the model stops calling functions
        
        while True:
            part = response.candidates[0].content.parts[0]
            
            if part.function_call:
                function_name = part.function_call.name
                function_args = dict(part.function_call.args)
                
                logger.info(f"Gemini requested tool call: {function_name}")
                
                # Execute the tool (awaiting the async function)
                # _execute_tool now returns the raw object (Pydantic model or list)
                raw_result = await self._execute_tool(function_name, function_args, token)
                
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
                
                logger.info(f"Tool Raw Result: {raw_result}")
                logger.info(f"Tool Formatted Result: {json_result}")
                
                
                # Send the response back to the model
                # We need to construct the response part correctly
                from google.ai.generativelanguage import Part, FunctionResponse
                
                logger.info(f"Sending tool result back to Gemini")
                
                # The library expects a specific format for function responses
                response = await chat.send_message_async(
                    Part(function_response=FunctionResponse(
                        name=function_name,
                        response={"result": json_result}
                    ))
                )
            else:
                # No more function calls, return the text response
                logger.info("Gemini response complete")
                
                # Prepare response value for API
                response_value = None
                response_text = response.text
                response_type = last_tool_name
                
                if last_tool_result:
                    if isinstance(last_tool_result, ToolResult):
                        response_value = last_tool_result.data
                        if hasattr(response_value, "dict"):
                            response_value = response_value.dict()
                        # Use the text from the tool result as the main response text
                        response_text = last_tool_result.text
                        # Use the type from the tool result
                        response_type = last_tool_result.type
                    elif isinstance(last_tool_result, list):
                        response_value = [item.dict() for item in last_tool_result]
                    elif hasattr(last_tool_result, "dict"):
                        response_value = last_tool_result.dict()
                    else:
                        response_value = last_tool_result

                return {
                    "type": response_type,
                    "response_text": response_text,
                    "response_value": response_value
                }
