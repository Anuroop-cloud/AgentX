"""
Mobile Workflow Agents for AgentX

Implements Sequential, Parallel, and Loop agents for mobile automation
workflows using the existing AgentSphere patterns.
"""

# Import your existing workflow agent types
from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
from google.adk.tools.agent_tool import AgentTool

# Import the mobile agents we created
from ..agents.mobile_gmail_agent import mobile_gmail_agent
from ..agents.mobile_whatsapp_agent import mobile_whatsapp_agent  
from ..agents.mobile_calendar_agent import mobile_calendar_agent


# --- Supporting Agents for Workflows ---

# Maps/Navigation Agent (using existing LlmAgent pattern)
mobile_maps_agent = LlmAgent(
    name="mobile_maps_agent",
    model="gemini-2.0-flash",
    instruction="""
        You are a Mobile Maps Assistant for location and navigation tasks.
        
        CAPABILITIES:
        - Get directions between locations
        - Check traffic conditions and travel time
        - Find nearby places (restaurants, gas stations, etc.)
        - Provide location-based recommendations
        
        MOBILE CONTEXT:
        - Consider current location and mobile user needs
        - Provide travel time estimates including traffic
        - Suggest the fastest routes for mobile navigation
        - Include relevant place details (ratings, phone numbers)
        
        Always provide actionable location information optimized for mobile users.
    """,
    description="Mobile Maps agent for location and navigation automation",
    output_key="maps_info"
)

# Notification/Summary Agent (using existing LlmAgent pattern)
mobile_summary_agent = LlmAgent(
    name="mobile_summary_agent", 
    model="gemini-2.0-flash",
    instruction="""
        You are a Mobile Summary Assistant for workflow consolidation.
        
        CAPABILITIES:
        - Summarize information from multiple mobile apps
        - Create actionable mobile notifications
        - Prioritize information by urgency and importance
        - Format summaries for mobile screen viewing
        
        MOBILE OPTIMIZATION:
        - Keep summaries concise and scannable
        - Highlight key actions and deadlines
        - Use bullet points and clear formatting
        - Prioritize most important information first
        
        Create mobile-friendly summaries that help users quickly understand and act.
    """,
    description="Mobile Summary agent for workflow consolidation and notifications",
    output_key="summary_info"
)


# --- Sequential Workflow: Meeting Preparation Pipeline ---
# Adapts your lead_qualification_agent pattern for mobile meeting prep

meeting_prep_workflow = SequentialAgent(
    name="MeetingPrepWorkflow",
    sub_agents=[
        mobile_calendar_agent,  # 1. Get meeting details from calendar
        mobile_gmail_agent,     # 2. Search for relevant emails with attendees
        mobile_maps_agent,      # 3. Get directions and traffic info
        mobile_whatsapp_agent,  # 4. Send updates to relevant contacts
        mobile_summary_agent    # 5. Create summary of prep actions
    ],
    description="Sequential mobile workflow for comprehensive meeting preparation"
)


# --- Parallel Workflow: Morning Routine Orchestrator ---
# Adapts your system_monitor_agent pattern for mobile morning tasks

# Create parallel agent for simultaneous morning data gathering
morning_info_gatherer = ParallelAgent(
    name="morning_info_gatherer",
    sub_agents=[
        mobile_calendar_agent,  # Check today's schedule
        mobile_gmail_agent,     # Check overnight emails
        mobile_whatsapp_agent   # Check overnight messages
    ]
)

# Sequential wrapper for morning routine (parallel then summary)
morning_routine_workflow = SequentialAgent(
    name="MorningRoutineWorkflow",
    sub_agents=[
        morning_info_gatherer,  # Parallel: Gather all morning info
        mobile_summary_agent    # Sequential: Create morning briefing
    ],
    description="Mobile morning routine with parallel info gathering and summary"
)


# --- Communication Triage Workflow ---
# Sequential workflow for message prioritization and response

communication_triage_workflow = SequentialAgent(
    name="CommunicationTriageWorkflow", 
    sub_agents=[
        mobile_gmail_agent,     # 1. Read recent emails
        mobile_whatsapp_agent,  # 2. Read recent messages  
        mobile_summary_agent    # 3. Prioritize and summarize all communications
    ],
    description="Sequential mobile workflow for communication triage and prioritization"
)


# --- Smart Scheduling Workflow ---
# Uses calendar and maps for intelligent meeting scheduling

smart_scheduling_workflow = SequentialAgent(
    name="SmartSchedulingWorkflow",
    sub_agents=[
        mobile_calendar_agent,  # 1. Find free time slots
        mobile_maps_agent,      # 2. Consider travel time and location
        mobile_calendar_agent,  # 3. Create optimized event
        mobile_gmail_agent      # 4. Send confirmation email
    ],
    description="Sequential mobile workflow for intelligent meeting scheduling with location awareness"
)


# --- Export all workflow agents ---
__all__ = [
    "meeting_prep_workflow",
    "morning_routine_workflow", 
    "communication_triage_workflow",
    "smart_scheduling_workflow",
    "mobile_maps_agent",
    "mobile_summary_agent"
]