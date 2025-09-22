"""
MCP-First AgentX Orchestrator
Core service that manages MCP services and provides unified API
"""
import json
import logging
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import asyncio
import aiofiles

# Using built-in modules to avoid disk quota issues
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    FASTAPI_AVAILABLE = False

# Pydantic models for MCP protocol
class ToolMetadata(BaseModel):
    tool_id: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

class ServiceMetadata(BaseModel):
    name: str
    url: str
    tools: List[ToolMetadata]
    last_seen: datetime
    health_status: str = "unknown"

class InvokeRequest(BaseModel):
    tool_id: str
    inputs: Dict[str, Any]
    request_id: Optional[str] = None

class InvokeResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class ServiceRegistryRequest(BaseModel):
    name: str
    url: str
    tools: List[ToolMetadata]

class AgentXOrchestrator:
    def __init__(self):
        self.services: Dict[str, ServiceMetadata] = {}
        self.init_database()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
    def init_database(self):
        """Initialize SQLite database for service registry"""
        self.conn = sqlite3.connect('orchestrator.db', check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                name TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                tools TEXT NOT NULL,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                health_status TEXT DEFAULT 'unknown'
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS invocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT,
                tool_id TEXT NOT NULL,
                inputs TEXT NOT NULL,
                service_name TEXT NOT NULL,
                status TEXT NOT NULL,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def register_service(self, service: ServiceRegistryRequest) -> Dict[str, str]:
        """Register a new MCP service"""
        try:
            tools_json = json.dumps([tool.dict() for tool in service.tools])
            
            self.conn.execute('''
                INSERT OR REPLACE INTO services (name, url, tools, last_seen, health_status)
                VALUES (?, ?, ?, ?, ?)
            ''', (service.name, service.url, tools_json, datetime.now(), "registered"))
            self.conn.commit()
            
            # Update in-memory registry
            service_metadata = ServiceMetadata(
                name=service.name,
                url=service.url,
                tools=service.tools,
                last_seen=datetime.now(),
                health_status="registered"
            )
            self.services[service.name] = service_metadata
            
            self.logger.info(f"Registered service: {service.name} with {len(service.tools)} tools")
            return {"status": "registered", "service": service.name}
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service.name}: {e}")
            return {"status": "error", "message": str(e)}
            
    def get_all_tools(self) -> List[ToolMetadata]:
        """Get all tools from all registered services"""
        all_tools = []
        for service in self.services.values():
            all_tools.extend(service.tools)
        return all_tools
        
    async def invoke_tool(self, request: InvokeRequest) -> InvokeResponse:
        """Invoke a tool on the appropriate MCP service"""
        try:
            # Find the service that owns this tool
            service_name = None
            service_metadata = None
            
            for name, service in self.services.items():
                for tool in service.tools:
                    if tool.tool_id == request.tool_id:
                        service_name = name
                        service_metadata = service
                        break
                if service_name:
                    break
                    
            if not service_name:
                return InvokeResponse(
                    status="error",
                    error={"code": "TOOL_NOT_FOUND", "message": f"Tool {request.tool_id} not found"}
                )
            
            # For now, simulate the tool invocation since we have stub services
            result = await self._simulate_tool_invocation(request.tool_id, request.inputs)
            
            # Log the invocation
            self.conn.execute('''
                INSERT INTO invocations (request_id, tool_id, inputs, service_name, status, response)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request.request_id, request.tool_id, json.dumps(request.inputs), 
                  service_name, "success", json.dumps(result)))
            self.conn.commit()
            
            return InvokeResponse(status="ok", result=result)
            
        except Exception as e:
            self.logger.error(f"Tool invocation failed: {e}")
            return InvokeResponse(
                status="error", 
                error={"code": "INVOCATION_ERROR", "message": str(e)}
            )
    
    async def _simulate_tool_invocation(self, tool_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate tool invocation for demo purposes"""
        if tool_id.startswith("time."):
            if tool_id == "time.current_time":
                return {"current_time": datetime.now().isoformat(), "timezone": "UTC"}
            elif tool_id == "time.parse_natural":
                return {"parsed_time": datetime.now().isoformat(), "confidence": 0.9}
                
        elif tool_id.startswith("whatsapp."):
            if tool_id == "whatsapp.read_chats":
                return {"chats": [
                    {"chat_id": "dev_team", "display_name": "Dev Team", 
                     "messages": [{"id": "1", "from": "John", "text": "Meeting at 3pm", "ts": datetime.now().isoformat()}]}
                ]}
            elif tool_id == "whatsapp.send_message":
                return {"message_id": f"msg_{int(time.time())}", "status": "sent"}
                
        elif tool_id.startswith("gmail."):
            if tool_id == "gmail.read_inbox":
                return {"emails": [
                    {"id": "1", "from": "boss@company.com", "subject": "Project Update", 
                     "snippet": "Please provide status update", "ts": datetime.now().isoformat()}
                ]}
            elif tool_id == "gmail.send_email":
                return {"message_id": f"email_{int(time.time())}", "status": "sent"}
                
        elif tool_id.startswith("calendar."):
            if tool_id == "calendar.list_events":
                return {"events": [
                    {"id": "1", "title": "Team Meeting", "start": datetime.now().isoformat(), 
                     "end": datetime.now().isoformat()}
                ]}
            elif tool_id == "calendar.create_event":
                return {"event_id": f"event_{int(time.time())}", "status": "created"}
        
        return {"result": "simulated_success", "tool_id": tool_id}

# Initialize the orchestrator
orchestrator = AgentXOrchestrator()

# FastAPI app setup
if FASTAPI_AVAILABLE:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Register built-in services
        await register_builtin_services()
        yield
        # Shutdown
        orchestrator.conn.close()

    app = FastAPI(
        title="AgentX MCP Orchestrator",
        description="MCP-First AgentX System - Service Registry and Tool Orchestration",
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "message": "AgentX MCP Orchestrator",
            "version": "1.0.0",
            "services": len(orchestrator.services),
            "total_tools": len(orchestrator.get_all_tools())
        }

    @app.post("/orchestrator/register")
    async def register_service(service: ServiceRegistryRequest):
        return orchestrator.register_service(service)

    @app.get("/orchestrator/tools")
    async def get_tools():
        return {"tools": orchestrator.get_all_tools()}

    @app.post("/orchestrator/invoke")
    async def invoke_tool(request: InvokeRequest):
        return await orchestrator.invoke_tool(request)

    @app.get("/orchestrator/services")
    async def get_services():
        return {"services": list(orchestrator.services.values())}

    @app.get("/health")
    async def health():
        return {"status": "ok", "uptime": time.time()}

async def register_builtin_services():
    """Register built-in MCP services"""
    
    # Time MCP
    time_tools = [
        ToolMetadata(
            tool_id="time.current_time",
            description="Get current time in ISO format",
            input_schema={},
            output_schema={"current_time": "string", "timezone": "string"}
        ),
        ToolMetadata(
            tool_id="time.parse_natural",
            description="Parse natural language time expression",
            input_schema={"text": "string"},
            output_schema={"parsed_time": "string", "confidence": "number"}
        )
    ]
    
    # WhatsApp MCP
    whatsapp_tools = [
        ToolMetadata(
            tool_id="whatsapp.read_chats",
            description="Read WhatsApp chats and messages",
            input_schema={"limit": "number", "since": "string", "chat_id": "string"},
            output_schema={"chats": "array"}
        ),
        ToolMetadata(
            tool_id="whatsapp.send_message",
            description="Send WhatsApp message",
            input_schema={"chat_id": "string", "message": "string"},
            output_schema={"message_id": "string", "status": "string"}
        )
    ]
    
    # Gmail MCP
    gmail_tools = [
        ToolMetadata(
            tool_id="gmail.read_inbox",
            description="Read Gmail inbox",
            input_schema={"label": "string", "unread_only": "boolean", "limit": "number"},
            output_schema={"emails": "array"}
        ),
        ToolMetadata(
            tool_id="gmail.send_email",
            description="Send Gmail email",
            input_schema={"to": "array", "subject": "string", "body": "string"},
            output_schema={"message_id": "string", "status": "string"}
        )
    ]
    
    # Calendar MCP
    calendar_tools = [
        ToolMetadata(
            tool_id="calendar.list_events",
            description="List calendar events",
            input_schema={"start": "string", "end": "string"},
            output_schema={"events": "array"}
        ),
        ToolMetadata(
            tool_id="calendar.create_event",
            description="Create calendar event",
            input_schema={"title": "string", "start": "string", "end": "string"},
            output_schema={"event_id": "string", "status": "string"}
        )
    ]
    
    # Register all services
    services_to_register = [
        ServiceRegistryRequest(name="time_mcp", url="builtin", tools=time_tools),
        ServiceRegistryRequest(name="whatsapp_mcp", url="builtin", tools=whatsapp_tools),
        ServiceRegistryRequest(name="gmail_mcp", url="builtin", tools=gmail_tools),
        ServiceRegistryRequest(name="calendar_mcp", url="builtin", tools=calendar_tools),
    ]
    
    for service in services_to_register:
        orchestrator.register_service(service)

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    else:
        print("FastAPI not available, running basic HTTP server...")
        # Fallback HTTP server implementation would go here