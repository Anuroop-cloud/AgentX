"""
Mobile AgentX - Main Entry Point

The complete mobile-first AI agent platform built on AgentSphere architecture.
Demonstrates how to adapt existing multi-agent patterns for mobile automation.
"""

# Core imports
from .orchestrator.mobile_orchestrator import (
    mobile_agentx_orchestrator,
    process_mobile_request
)
from .demos.demo_workflows import (
    get_all_demos,
    run_demo_scenario,
    HACKATHON_DEMO_GUIDE
)
from .workflows.mobile_workflows import (
    meeting_prep_workflow,
    morning_routine_workflow,
    communication_triage_workflow,
    smart_scheduling_workflow
)

# Individual agents
from .agents.mobile_gmail_agent import mobile_gmail_agent
from .agents.mobile_whatsapp_agent import mobile_whatsapp_agent
from .agents.mobile_calendar_agent import mobile_calendar_agent

# App connectors
from .app_connectors import (
    GmailConnector,
    WhatsAppConnector,
    CalendarConnector,
    MapsConnector,
    SpotifyConnector
)


class MobileAgentX:
    """
    Main Mobile AgentX platform class
    
    Provides a high-level interface for mobile automation workflows
    using AI agents that coordinate across smartphone apps.
    """
    
    def __init__(self, mock_mode: bool = True):
        """
        Initialize Mobile AgentX platform
        
        Args:
            mock_mode: Use mock responses for demo/development (default: True)
        """
        self.mock_mode = mock_mode
        self.orchestrator = mobile_agentx_orchestrator
        self.available_demos = get_all_demos()
        
        # Initialize app connectors
        self.connectors = {
            "gmail": GmailConnector(mock_mode=mock_mode),
            "whatsapp": WhatsAppConnector(mock_mode=mock_mode),
            "calendar": CalendarConnector(mock_mode=mock_mode),
            "maps": MapsConnector(mock_mode=mock_mode),
            "spotify": SpotifyConnector(mock_mode=mock_mode)
        }
        
        print("🚀 Mobile AgentX initialized!")
        print(f"📱 Mock mode: {'ON' if mock_mode else 'OFF'}")
        print(f"🤖 Available workflows: {len(self.available_demos)}")
        print("✨ Ready for mobile automation!")
    
    def process_request(self, user_input: str) -> dict:
        """
        Process a natural language automation request
        
        Args:
            user_input: User's natural language request
            
        Returns:
            Dict with workflow routing and execution plan
        """
        print(f"\n🎯 Processing: '{user_input}'")
        result = process_mobile_request(user_input)
        print(f"📋 Workflow: {result.get('workflow', 'single_agent')}")
        print(f"⏱️ Estimated time: {result.get('estimated_time', 'N/A')}")
        return result
    
    def run_demo(self, demo_name: str, custom_input: str = None) -> dict:
        """
        Run a specific demo workflow
        
        Args:
            demo_name: Name of demo ('meeting_prep', 'morning_routine', 'communication_triage')
            custom_input: Optional custom input text
            
        Returns:
            Demo execution results
        """
        print(f"\n🎬 Running demo: {demo_name}")
        return run_demo_scenario(demo_name, custom_input)
    
    def list_capabilities(self) -> dict:
        """List all platform capabilities"""
        return {
            "workflows": list(self.available_demos.keys()),
            "apps": list(self.connectors.keys()),
            "agents": [
                "mobile_gmail_agent",
                "mobile_whatsapp_agent", 
                "mobile_calendar_agent",
                "mobile_maps_agent",
                "mobile_summary_agent"
            ],
            "workflow_types": [
                "Sequential (step-by-step)",
                "Parallel (simultaneous)",
                "Hybrid (parallel + sequential)"
            ]
        }
    
    def get_connection_status(self) -> dict:
        """Check connection status of all app connectors"""
        status = {}
        for app_name, connector in self.connectors.items():
            status[app_name] = connector.get_connection_status()
        return status
    
    def show_demo_guide(self):
        """Display the hackathon demo guide"""
        print(HACKATHON_DEMO_GUIDE)


# --- Convenience functions for quick usage ---
def quick_demo():
    """Run a quick demo of Mobile AgentX capabilities"""
    agentx = MobileAgentX(mock_mode=True)
    
    print("\n" + "="*60)
    print("🚀 MOBILE AGENTX QUICK DEMO")
    print("="*60)
    
    # Demo scenarios
    demo_inputs = [
        "Prepare for my 3 PM client meeting",
        "Plan my productive morning", 
        "Summarize and prioritize my messages"
    ]
    
    for i, demo_input in enumerate(demo_inputs, 1):
        print(f"\n📱 Demo {i}: {demo_input}")
        result = agentx.process_request(demo_input)
        print(f"✅ Routed to: {result.get('workflow', 'single_agent')}")
        print(f"🔄 Agents: {', '.join(result.get('agents_involved', ['single_agent']))}")
    
    print(f"\n🎯 Platform capabilities:")
    capabilities = agentx.list_capabilities()
    print(f"📊 Workflows: {len(capabilities['workflows'])}")
    print(f"📱 Apps: {len(capabilities['apps'])}")
    print(f"🤖 Agents: {len(capabilities['agents'])}")
    
    print(f"\n💡 Try running: agentx.run_demo('meeting_prep')")
    return agentx


def hackathon_demo():
    """Run the full hackathon demo sequence"""
    agentx = MobileAgentX(mock_mode=True)
    agentx.show_demo_guide()
    
    print("\n🎯 HACKATHON DEMO SEQUENCE")
    print("-" * 40)
    
    # Run all three main demos
    demos = ['meeting_prep', 'morning_routine', 'communication_triage']
    
    for demo in demos:
        print(f"\n🎬 Running {demo.replace('_', ' ').title()} Demo...")
        result = agentx.run_demo(demo)
        print(f"✅ Status: {result['status']}")
        print(f"🔄 Workflow: {result['workflow_type']}")
        print(f"📊 Agents: {result['agent_count']}")
    
    return agentx


# --- Main execution ---
if __name__ == "__main__":
    # Run quick demo when script is executed directly
    agentx = quick_demo()


# --- Exports ---
__all__ = [
    "MobileAgentX",
    "mobile_agentx_orchestrator", 
    "quick_demo",
    "hackathon_demo",
    
    # Workflows
    "meeting_prep_workflow",
    "morning_routine_workflow", 
    "communication_triage_workflow",
    "smart_scheduling_workflow",
    
    # Individual agents
    "mobile_gmail_agent",
    "mobile_whatsapp_agent",
    "mobile_calendar_agent",
    
    # Connectors
    "GmailConnector",
    "WhatsAppConnector",
    "CalendarConnector", 
    "MapsConnector",
    "SpotifyConnector"
]