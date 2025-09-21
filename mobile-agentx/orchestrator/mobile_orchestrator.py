"""
Mobile AgentX Orchestrator

Main orchestrator agent that handles natural language input and routes tasks
to appropriate mobile workflows. Adapts the multi-agent manager pattern from
AgentSphere for mobile automation.
"""

from google.adk.agents import Agent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import workflows and individual agents
from ..workflows.mobile_workflows import (
    meeting_prep_workflow,
    morning_routine_workflow,
    communication_triage_workflow,
    smart_scheduling_workflow
)
from ..agents.mobile_gmail_agent import mobile_gmail_agent
from ..agents.mobile_whatsapp_agent import mobile_whatsapp_agent
from ..agents.mobile_calendar_agent import mobile_calendar_agent


# --- Workflow Intent Detection Schema ---
class WorkflowIntent(BaseModel):
    workflow_type: str = Field(
        description="Type of mobile workflow: 'meeting_prep', 'morning_routine', 'communication_triage', 'smart_scheduling', 'single_app'",
        enum=["meeting_prep", "morning_routine", "communication_triage", "smart_scheduling", "single_app"]
    )
    target_app: Optional[str] = Field(
        description="For single_app workflows, specify: 'gmail', 'whatsapp', 'calendar'",
        default=None
    )
    user_intent: str = Field(
        description="Processed user intent for the workflow"
    )
    priority: str = Field(
        description="Urgency level: 'high', 'medium', 'low'",
        enum=["high", "medium", "low"]
    )
    context_hints: List[str] = Field(
        description="Additional context extracted from user input",
        default=[]
    )


# --- Intent Analysis Agent ---
mobile_intent_analyzer = LlmAgent(
    name="mobile_intent_analyzer",
    model="gemini-2.0-flash",
    instruction="""
        You are a Mobile Intent Analysis specialist for AgentX.
        Your task is to analyze user input and determine the appropriate mobile workflow.

        WORKFLOW TYPES:
        
        1. MEETING_PREP - "prepare for meeting", "get ready for call", "meeting preparation"
           → Sequential: Calendar → Gmail → Maps → WhatsApp → Summary
           
        2. MORNING_ROUTINE - "plan my day", "morning briefing", "daily overview"  
           → Parallel: Calendar + Gmail + WhatsApp, then Summary
           
        3. COMMUNICATION_TRIAGE - "check messages", "prioritize communications", "message summary"
           → Sequential: Gmail → WhatsApp → Summary with priorities
           
        4. SMART_SCHEDULING - "schedule meeting", "find time for", "book appointment"
           → Sequential: Calendar (find time) → Maps (location) → Calendar (create) → Gmail (confirm)
           
        5. SINGLE_APP - Direct app actions: "send email", "check calendar", "WhatsApp message"
           → Route to specific app agent (gmail, whatsapp, calendar)

        CONTEXT EXTRACTION:
        - Extract time references ("3 PM", "tomorrow", "next week")
        - Identify people/contacts mentioned
        - Detect location references 
        - Determine urgency indicators ("urgent", "ASAP", "when convenient")
        - Note app-specific keywords

        MOBILE AWARENESS:
        - Consider mobile user context (on-the-go, quick actions needed)
        - Prioritize efficiency and brevity
        - Assume user wants immediate, actionable results

        OUTPUT: WorkflowIntent object with appropriate workflow routing
    """,
    description="Analyzes user input to determine optimal mobile workflow routing",
    output_schema=WorkflowIntent,
    output_key="workflow_intent"
)


# --- Custom Workflow Router Function ---
def route_workflow(intent: WorkflowIntent, original_input: str) -> Dict[str, Any]:
    """Route user input to appropriate workflow based on intent analysis"""
    
    timestamp = datetime.now().isoformat()
    
    if intent.workflow_type == "meeting_prep":
        return {
            "status": "routing_to_workflow",
            "workflow": "meeting_prep_workflow", 
            "description": "Preparing for meeting with cross-app coordination",
            "agents_involved": ["calendar", "gmail", "maps", "whatsapp", "summary"],
            "estimated_time": "30-45 seconds",
            "user_input": original_input,
            "processed_intent": intent.user_intent,
            "priority": intent.priority,
            "timestamp": timestamp
        }
    
    elif intent.workflow_type == "morning_routine":
        return {
            "status": "routing_to_workflow",
            "workflow": "morning_routine_workflow",
            "description": "Gathering morning information with parallel processing", 
            "agents_involved": ["calendar", "gmail", "whatsapp", "summary"],
            "estimated_time": "20-30 seconds",
            "parallel_processing": True,
            "user_input": original_input,
            "processed_intent": intent.user_intent,
            "priority": intent.priority,
            "timestamp": timestamp
        }
    
    elif intent.workflow_type == "communication_triage":
        return {
            "status": "routing_to_workflow", 
            "workflow": "communication_triage_workflow",
            "description": "Analyzing and prioritizing all communications",
            "agents_involved": ["gmail", "whatsapp", "summary"],
            "estimated_time": "25-35 seconds", 
            "user_input": original_input,
            "processed_intent": intent.user_intent,
            "priority": intent.priority,
            "timestamp": timestamp
        }
    
    elif intent.workflow_type == "smart_scheduling":
        return {
            "status": "routing_to_workflow",
            "workflow": "smart_scheduling_workflow", 
            "description": "Intelligent scheduling with location awareness",
            "agents_involved": ["calendar", "maps", "gmail"],
            "estimated_time": "35-45 seconds",
            "user_input": original_input,
            "processed_intent": intent.user_intent, 
            "priority": intent.priority,
            "timestamp": timestamp
        }
    
    elif intent.workflow_type == "single_app":
        app_routing = {
            "gmail": "mobile_gmail_agent",
            "whatsapp": "mobile_whatsapp_agent", 
            "calendar": "mobile_calendar_agent"
        }
        
        return {
            "status": "routing_to_single_agent",
            "agent": app_routing.get(intent.target_app, "unknown"),
            "description": f"Direct {intent.target_app} action",
            "estimated_time": "10-15 seconds",
            "user_input": original_input,
            "processed_intent": intent.user_intent,
            "priority": intent.priority,
            "timestamp": timestamp
        }
    
    else:
        return {
            "status": "error",
            "message": f"Unknown workflow type: {intent.workflow_type}",
            "user_input": original_input,
            "timestamp": timestamp
        }


# --- Main Mobile AgentX Orchestrator ---
# Adapts your manager agent pattern for mobile workflows
mobile_agentx_orchestrator = Agent(
    name="mobile_agentx_orchestrator",
    model="gemini-2.0-flash",
    description="Mobile AgentX orchestrator for smartphone automation workflows",
    instruction="""
        You are the Mobile AgentX Orchestrator, the main intelligence for smartphone automation.
        Your role is to understand natural language requests and coordinate mobile app workflows.

        CORE CAPABILITIES:
        🤖 Multi-Agent Coordination: Route tasks to specialized mobile agents
        📱 Mobile Context Awareness: Optimize for smartphone usage patterns  
        🔄 Workflow Intelligence: Chain agents for complex multi-app tasks
        ⚡ Real-Time Processing: Handle urgent mobile automation needs

        WORKFLOW ROUTING:
        Always analyze user input first using the intent analyzer, then route appropriately:
        
        - Meeting preparation → meeting_prep_workflow
        - Daily planning → morning_routine_workflow  
        - Message management → communication_triage_workflow
        - Event scheduling → smart_scheduling_workflow
        - Single app actions → direct agent routing

        MOBILE OPTIMIZATION PRINCIPLES:
        - Prioritize speed and efficiency for mobile users
        - Provide concise, actionable outputs
        - Consider mobile context (location, time, urgency)
        - Handle interruptions and context switching gracefully
        - Optimize for touch interaction and small screens

        AGENT DELEGATION STRATEGY:
        1. First, analyze user intent and determine workflow type
        2. Route to appropriate workflow or single agent
        3. Coordinate execution across multiple mobile apps
        4. Provide real-time status updates
        5. Return mobile-optimized results

        You have access to:
        - Intent Analyzer: For understanding user requests
        - Gmail Agent: For email automation
        - WhatsApp Agent: For messaging automation  
        - Calendar Agent: For scheduling automation
        - Multi-agent workflows: For complex task orchestration

        Always delegate tasks to the appropriate agents and coordinate their responses effectively.
    """,
    sub_agents=[
        # No sub_agents - we use tools for delegation to avoid conflicts
    ],
    tools=[
        AgentTool(mobile_intent_analyzer),
        AgentTool(mobile_gmail_agent),
        AgentTool(mobile_whatsapp_agent),
        AgentTool(mobile_calendar_agent),
        route_workflow  # Custom routing function
    ]
)


# --- Convenience Functions for Demo ---
def process_mobile_request(user_input: str) -> Dict[str, Any]:
    """
    Process a mobile automation request through the orchestrator
    
    Args:
        user_input: Natural language request from user
        
    Returns:
        Dictionary with workflow routing and execution plan
    """
    # This would typically involve calling the orchestrator agent
    # For demo purposes, we'll simulate the process
    
    # Step 1: Analyze intent (simulated)
    intent_keywords = {
        "meeting": "meeting_prep",
        "prepare": "meeting_prep", 
        "morning": "morning_routine",
        "day": "morning_routine",
        "message": "communication_triage",
        "email": "single_app",
        "calendar": "single_app",
        "schedule": "smart_scheduling"
    }
    
    detected_workflow = "morning_routine"  # default
    for keyword, workflow in intent_keywords.items():
        if keyword in user_input.lower():
            detected_workflow = workflow
            break
    
    # Step 2: Route to workflow
    mock_intent = WorkflowIntent(
        workflow_type=detected_workflow,
        user_intent=user_input,
        priority="medium",
        context_hints=[]
    )
    
    return route_workflow(mock_intent, user_input)


# --- Export main orchestrator ---
__all__ = [
    "mobile_agentx_orchestrator",
    "mobile_intent_analyzer", 
    "WorkflowIntent",
    "process_mobile_request",
    "route_workflow"
]