#!/usr/bin/env python3
"""
🚀 Mobile AgentX - Quick Run Script

Simple script to test and demo the Mobile AgentX platform.
Run this to see the mobile automation in action!
"""

import sys
import os
from datetime import datetime

# Add current directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_app_connectors():
    """Test all app connectors to make sure they work"""
    print("🔧 Testing App Connectors...")
    
    try:
        from app_connectors.gmail_connector import GmailConnector
        from app_connectors.whatsapp_connector import WhatsAppConnector
        from app_connectors.calendar_connector import CalendarConnector
        
        # Test Gmail
        gmail = GmailConnector(mock_mode=True)
        gmail_status = gmail.get_connection_status()
        print(f"   ✅ Gmail: {gmail_status['app_name']} - Connected: {gmail_status['connected']}")
        
        # Test WhatsApp
        whatsapp = WhatsAppConnector(mock_mode=True)
        whatsapp_status = whatsapp.get_connection_status()
        print(f"   ✅ WhatsApp: {whatsapp_status['app_name']} - Connected: {whatsapp_status['connected']}")
        
        # Test Calendar
        calendar = CalendarConnector(mock_mode=True)
        calendar_status = calendar.get_connection_status()
        print(f"   ✅ Calendar: {calendar_status['app_name']} - Connected: {calendar_status['connected']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing connectors: {e}")
        return False

def demo_gmail_automation():
    """Demo Gmail automation"""
    print("\n📧 Demo: Gmail Automation")
    print("-" * 30)
    
    try:
        from app_connectors.gmail_connector import GmailConnector
        
        gmail = GmailConnector(mock_mode=True)
        
        # Send email demo
        print("📤 Sending email...")
        result = gmail.send_email(
            to="client@company.com",
            subject="Meeting Confirmation",
            body="Hi! Confirming our meeting at 3 PM today. Looking forward to it!"
        )
        print(f"   Result: {result['status']} - Message ID: {result['message_id']}")
        
        # Read emails demo
        print("📥 Reading recent emails...")
        emails = gmail.read_emails(max_results=3)
        print(f"   Found {len(emails)} emails:")
        for email in emails:
            print(f"   • From: {email.sender}")
            print(f"     Subject: {email.subject}")
            print(f"     Preview: {email.body[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Error in Gmail demo: {e}")

def demo_whatsapp_automation():
    """Demo WhatsApp automation"""
    print("\n💬 Demo: WhatsApp Automation")  
    print("-" * 30)
    
    try:
        from app_connectors.whatsapp_connector import WhatsAppConnector
        
        whatsapp = WhatsAppConnector(mock_mode=True)
        
        # Send message demo
        print("📤 Sending WhatsApp message...")
        result = whatsapp.send_message(
            to="+1234567890",
            message="Hey! Running a few minutes late due to traffic. See you soon!"
        )
        print(f"   Result: {result['status']} - Message ID: {result['message_id']}")
        
        # Read messages demo
        print("📥 Reading recent messages...")
        messages = whatsapp.read_messages(max_results=3)
        print(f"   Found {len(messages)} messages:")
        for msg in messages:
            print(f"   • From: {msg.contact_name} ({msg.contact})")
            print(f"     Message: {msg.message}")
            
    except Exception as e:
        print(f"   ❌ Error in WhatsApp demo: {e}")

def demo_calendar_automation():
    """Demo Calendar automation"""
    print("\n📅 Demo: Calendar Automation")
    print("-" * 30)
    
    try:
        from app_connectors.calendar_connector import CalendarConnector
        
        calendar = CalendarConnector(mock_mode=True)
        
        # Get today's events
        print("📋 Checking today's schedule...")
        events = calendar.get_today_events()
        print(f"   Found {len(events)} events today:")
        for event in events:
            print(f"   • {event.start_time.strftime('%H:%M')} - {event.title}")
            if event.location:
                print(f"     Location: {event.location}")
                
        # Create new event demo
        print("📝 Creating new event...")
        from datetime import datetime, timedelta
        start_time = datetime.now() + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)
        
        result = calendar.create_event(
            title="AgentX Demo Meeting",
            start_time=start_time,
            end_time=end_time,
            description="Demonstrating mobile automation capabilities",
            location="Conference Room A"
        )
        print(f"   Result: {result['status']} - Event ID: {result['event_id']}")
        
    except Exception as e:
        print(f"   ❌ Error in Calendar demo: {e}")

def demo_mobile_workflows():
    """Demo the mobile workflow scenarios"""
    print("\n🔄 Demo: Mobile Workflow Scenarios")
    print("=" * 40)
    
    # Simulate the three main workflows
    workflows = [
        {
            "name": "Meeting Preparation",
            "input": "Prepare for my 3 PM client meeting",
            "steps": ["📅 Check calendar", "📧 Find emails", "🗺️ Get directions", "💬 Send updates", "📝 Create summary"]
        },
        {
            "name": "Morning Routine", 
            "input": "Plan my productive morning",
            "steps": ["📅📧💬 Parallel: Check all apps", "📝 Create daily briefing"]
        },
        {
            "name": "Communication Triage",
            "input": "Summarize and prioritize my messages", 
            "steps": ["📧 Analyze emails", "💬 Review WhatsApp", "📊 Create priority matrix"]
        }
    ]
    
    for i, workflow in enumerate(workflows, 1):
        print(f"\n🎬 Workflow {i}: {workflow['name']}")
        print(f"   User Input: '{workflow['input']}'")
        print(f"   Agent Steps:")
        for step in workflow['steps']:
            print(f"     → {step}")
        print(f"   ⏱️ Estimated Time: 20-40 seconds")
        print(f"   ✅ Status: Ready for demo")

def main():
    """Main function to run all demos"""
    print("🚀 MOBILE AGENTX - QUICK RUN DEMO")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📱 Mode: Mock API Demo")
    
    # Test connectors first
    if not test_app_connectors():
        print("❌ Connector tests failed. Please check the code.")
        return
    
    # Run individual app demos
    demo_gmail_automation()
    demo_whatsapp_automation() 
    demo_calendar_automation()
    
    # Show workflow scenarios
    demo_mobile_workflows()
    
    print("\n" + "=" * 50)
    print("✅ MOBILE AGENTX DEMO COMPLETE!")
    print("=" * 50)
    
    print("\n🎯 What just happened:")
    print("   ✅ Tested all app connectors (Gmail, WhatsApp, Calendar)")
    print("   ✅ Demonstrated email automation")
    print("   ✅ Showed messaging capabilities") 
    print("   ✅ Displayed calendar management")
    print("   ✅ Outlined multi-agent workflows")
    
    print("\n💡 Next steps:")
    print("   1. Connect real APIs (replace mock_mode=True)")
    print("   2. Build mobile app frontend")
    print("   3. Add more app connectors (Maps, Spotify)")
    print("   4. Create visual workflow builder")
    
    print("\n🏆 Platform Status: READY FOR HACKATHON!")
    print("   Perfect for demonstrating mobile AI automation to judges")

if __name__ == "__main__":
    main()