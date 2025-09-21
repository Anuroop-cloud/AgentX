"""
Demo Workflows for Mobile AgentX

Three impressive demo workflows that showcase mobile automation capabilities:
1. Meeting Preparation Assistant
2. Morning Routine Orchestrator  
3. Communication Triage System
"""

from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
from ..workflows.mobile_workflows import (
    meeting_prep_workflow,
    morning_routine_workflow,
    communication_triage_workflow
)


# --- Demo Workflow 1: Meeting Preparation Assistant ---
class MeetingPrepDemo:
    """
    Impressive demo workflow that automatically prepares for upcoming meetings
    by coordinating across Calendar, Gmail, Maps, and WhatsApp.
    """
    
    def __init__(self):
        self.workflow = meeting_prep_workflow
        self.demo_description = """
        DEMO: "Prepare for my 3 PM client meeting"
        
        Agent Actions:
        1. 📅 Calendar Agent: Retrieves meeting details, attendees, location
        2. 📧 Gmail Agent: Searches for relevant emails with client/attendees  
        3. 🗺️ Maps Agent: Gets directions, traffic conditions, travel time
        4. 💬 WhatsApp Agent: Sends updates to team about meeting timing
        5. 📝 Summary Agent: Creates meeting prep summary with key points
        
        Result: Comprehensive meeting preparation with all context ready
        """
        
    def get_demo_input(self):
        return "Prepare for my 3 PM client meeting with TechCorp"
        
    def get_expected_output(self):
        return {
            "meeting_details": "Client Meeting - TechCorp at 3 PM",
            "relevant_emails": "3 emails found with client correspondence",
            "travel_info": "35 minutes drive with current traffic",
            "team_updates": "WhatsApp sent to team about timing",
            "prep_summary": "Meeting brief with key topics and attendee info"
        }


# --- Demo Workflow 2: Morning Routine Orchestrator ---
class MorningRoutineDemo:
    """
    Parallel processing demo that simultaneously gathers morning information
    from multiple apps and creates an intelligent daily briefing.
    """
    
    def __init__(self):
        self.workflow = morning_routine_workflow
        self.demo_description = """
        DEMO: "Plan my productive morning"
        
        Parallel Agent Actions (Simultaneous):
        📅 Calendar Agent: Checks today's schedule and priorities
        📧 Gmail Agent: Reviews overnight emails for urgency  
        💬 WhatsApp Agent: Checks personal and work messages
        
        Sequential Summary:
        📝 Summary Agent: Creates prioritized morning briefing
        
        Result: Complete morning context in one mobile-friendly summary
        """
        
    def get_demo_input(self):
        return "Plan my productive morning routine"
        
    def get_expected_output(self):
        return {
            "todays_schedule": "4 meetings, 1 deadline, 2 personal events",
            "urgent_emails": "2 urgent emails requiring response",
            "important_messages": "1 client message, 3 team updates",
            "morning_briefing": "Prioritized action list with time blocks"
        }


# --- Demo Workflow 3: Communication Triage System ---
class CommunicationTriageDemo:
    """
    Sequential processing demo that analyzes all incoming communications
    and creates an intelligent priority system for mobile productivity.
    """
    
    def __init__(self):
        self.workflow = communication_triage_workflow
        self.demo_description = """
        DEMO: "Summarize and prioritize my messages"
        
        Sequential Agent Actions:
        1. 📧 Gmail Agent: Reads recent emails with urgency analysis
        2. 💬 WhatsApp Agent: Reviews messages from contacts and groups
        3. 📝 Summary Agent: Creates priority matrix with response suggestions
        
        Result: Intelligent message triage with recommended actions
        """
        
    def get_demo_input(self):
        return "Summarize and prioritize all my messages"
        
    def get_expected_output(self):
        return {
            "email_summary": "5 emails: 2 urgent, 2 important, 1 low priority",
            "whatsapp_summary": "8 messages: 1 urgent client, 3 team, 4 personal",
            "priority_matrix": "Response order with time estimates",
            "suggested_actions": "Quick responses for high-priority items"
        }


# --- Combined Demo Orchestrator ---
demo_workflows = {
    "meeting_prep": MeetingPrepDemo(),
    "morning_routine": MorningRoutineDemo(), 
    "communication_triage": CommunicationTriageDemo()
}


def get_all_demos():
    """Return all available demo workflows"""
    return demo_workflows


def run_demo_scenario(demo_name: str, user_input: str = None):
    """
    Run a specific demo scenario
    
    Args:
        demo_name: Name of demo to run ('meeting_prep', 'morning_routine', 'communication_triage')
        user_input: Optional custom input, uses demo default if not provided
    """
    if demo_name not in demo_workflows:
        return {"error": f"Demo '{demo_name}' not found. Available: {list(demo_workflows.keys())}"}
    
    demo = demo_workflows[demo_name]
    input_text = user_input or demo.get_demo_input()
    
    # In a real implementation, you would run the workflow here
    # For demo purposes, return the expected output structure
    return {
        "demo_name": demo_name,
        "input": input_text,
        "description": demo.demo_description,
        "expected_output": demo.get_expected_output(),
        "workflow_type": type(demo.workflow).__name__,
        "agent_count": len(demo.workflow.sub_agents) if hasattr(demo.workflow, 'sub_agents') else 1,
        "status": "demo_ready"
    }


# --- Demo Instructions for Hackathon ---
HACKATHON_DEMO_GUIDE = """
🚀 MOBILE AGENTX DEMO SCENARIOS

Choose from these impressive workflows:

1. 📅 MEETING PREP (Sequential Workflow)
   Input: "Prepare for my 3 PM client meeting"
   Shows: Cross-app coordination, context gathering, intelligent preparation

2. 🌅 MORNING ROUTINE (Parallel + Sequential)  
   Input: "Plan my productive morning"
   Shows: Parallel processing, information synthesis, mobile briefing

3. 💬 MESSAGE TRIAGE (Sequential Analysis)
   Input: "Summarize and prioritize my messages"  
   Shows: Communication intelligence, priority ranking, action suggestions

Each demo showcases:
✅ Natural language input → AI workflow execution
✅ Multi-agent coordination across mobile apps
✅ Mobile-optimized outputs and actions
✅ Real-world productivity scenarios

Perfect for hackathon judges - shows technical depth + practical value!
"""


__all__ = [
    "MeetingPrepDemo",
    "MorningRoutineDemo", 
    "CommunicationTriageDemo",
    "demo_workflows",
    "get_all_demos",
    "run_demo_scenario",
    "HACKATHON_DEMO_GUIDE"
]