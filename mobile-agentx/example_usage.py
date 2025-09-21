#!/usr/bin/env python3
"""
Mobile AgentX Example Script

Demonstrates how to use the mobile automation platform
for hackathon demos and development.
"""

import sys
import os

# Add the mobile-agentx directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from mobile_agentx import MobileAgentX, hackathon_demo
except ImportError:
    # If running directly, import from current directory
    from __init__ import MobileAgentX, hackathon_demo


def main():
    """Main example script demonstrating Mobile AgentX capabilities"""
    
    print("🚀 Mobile AgentX - Example Usage")
    print("="*50)
    
    # Initialize the platform
    print("\n📱 Initializing Mobile AgentX...")
    agentx = MobileAgentX(mock_mode=True)
    
    print("\n🎯 Platform Capabilities:")
    capabilities = agentx.list_capabilities()
    print(f"   📊 Workflows: {', '.join(capabilities['workflows'])}")
    print(f"   📱 Apps: {', '.join(capabilities['apps'])}")
    print(f"   🤖 Agents: {len(capabilities['agents'])} specialized agents")
    
    print("\n🔗 Connection Status:")
    status = agentx.get_connection_status()
    for app, info in status.items():
        emoji = "✅" if info['connected'] else "❌"
        mode = " (MOCK)" if info.get('mock_mode') else ""
        print(f"   {emoji} {info['app_name']}{mode}")
    
    print("\n" + "="*50)
    print("🎬 DEMO SCENARIOS")
    print("="*50)
    
    # Example 1: Meeting Preparation
    print("\n📅 Example 1: Meeting Preparation")
    print("-" * 30)
    user_input_1 = "Prepare for my 3 PM client meeting with TechCorp"
    print(f"User: '{user_input_1}'")
    
    result_1 = agentx.process_request(user_input_1)
    print(f"🤖 AgentX Response:")
    print(f"   Workflow: {result_1.get('workflow', 'N/A')}")
    print(f"   Description: {result_1.get('description', 'N/A')}")
    print(f"   Agents: {', '.join(result_1.get('agents_involved', []))}")
    print(f"   Est. Time: {result_1.get('estimated_time', 'N/A')}")
    
    # Example 2: Morning Routine
    print("\n🌅 Example 2: Morning Routine")
    print("-" * 30)
    user_input_2 = "Plan my productive morning routine"
    print(f"User: '{user_input_2}'")
    
    result_2 = agentx.process_request(user_input_2)
    print(f"🤖 AgentX Response:")
    print(f"   Workflow: {result_2.get('workflow', 'N/A')}")
    print(f"   Description: {result_2.get('description', 'N/A')}")
    print(f"   Parallel Processing: {result_2.get('parallel_processing', False)}")
    print(f"   Est. Time: {result_2.get('estimated_time', 'N/A')}")
    
    # Example 3: Communication Triage
    print("\n💬 Example 3: Communication Triage")
    print("-" * 30)
    user_input_3 = "Summarize and prioritize all my messages"
    print(f"User: '{user_input_3}'")
    
    result_3 = agentx.process_request(user_input_3)
    print(f"🤖 AgentX Response:")
    print(f"   Workflow: {result_3.get('workflow', 'N/A')}")
    print(f"   Description: {result_3.get('description', 'N/A')}")
    print(f"   Agents: {', '.join(result_3.get('agents_involved', []))}")
    print(f"   Est. Time: {result_3.get('estimated_time', 'N/A')}")
    
    print("\n" + "="*50)
    print("🎪 RUNNING DETAILED DEMOS")
    print("="*50)
    
    # Run actual demo workflows
    demo_names = ['meeting_prep', 'morning_routine', 'communication_triage']
    
    for demo_name in demo_names:
        print(f"\n🎬 Running {demo_name.replace('_', ' ').title()} Demo...")
        demo_result = agentx.run_demo(demo_name)
        
        print(f"   Status: {demo_result['status']}")
        print(f"   Input: {demo_result['input']}")
        print(f"   Workflow Type: {demo_result['workflow_type']}")
        print(f"   Agent Count: {demo_result['agent_count']}")
        
        if 'expected_output' in demo_result:
            print(f"   Expected Results:")
            for key, value in demo_result['expected_output'].items():
                print(f"     • {key}: {value}")
    
    print("\n" + "="*50)
    print("✨ MOBILE AGENTX DEMO COMPLETE!")
    print("="*50)
    
    print("\n🎯 Key Highlights:")
    print("   ✅ Natural language input → AI workflow execution")
    print("   ✅ Multi-agent coordination across mobile apps") 
    print("   ✅ Sequential, Parallel, and Hybrid workflows")
    print("   ✅ Mobile-optimized outputs and actions")
    print("   ✅ Built on proven AgentSphere architecture")
    
    print("\n💡 Next Steps:")
    print("   1. Integrate real APIs (Gmail, WhatsApp Business)")
    print("   2. Build React Native mobile frontend")
    print("   3. Add visual workflow builder")
    print("   4. Create agent marketplace")
    
    print(f"\n🚀 Ready for hackathon presentation!")
    
    return agentx


def run_hackathon_sequence():
    """Run the full hackathon demo sequence"""
    print("🎪 HACKATHON DEMO SEQUENCE")
    print("="*50)
    
    # This will show the demo guide and run all scenarios
    agentx = hackathon_demo()
    
    print("\n🏆 Hackathon Demo Complete!")
    print("   Perfect for judges - shows technical depth + practical value")
    
    return agentx


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--hackathon":
        # Run hackathon demo sequence
        run_hackathon_sequence()
    else:
        # Run regular example
        main()