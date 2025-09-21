"""
AI Mobile AgentX - Demo Runner
Easy way to test and demonstrate the AI automation capabilities
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the ai-mobile-agentx directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now we can import our modules
from testing.mock_mode import SafeTestRunner, TestCase, MockAction, main as mock_main

async def run_demo():
    """Run a comprehensive demo of AI Mobile AgentX"""
    print("🤖 AI Mobile AgentX - Reformed Automation Demo")
    print("=" * 50)
    
    print("\n📱 This system uses AI and OCR to automate mobile apps")
    print("🔍 No hardcoded coordinates - dynamic text detection")
    print("🧪 Running in SAFE MOCK MODE (no real device needed)")
    print("📊 Visual feedback and screenshots will be generated")
    
    print("\n🚀 Starting mock automation demo...")
    
    # Run the mock testing framework
    await mock_main()
    
    print("\n✅ Demo completed!")
    print("📁 Check 'test_results' folder for screenshots and reports")
    print("🎯 This shows how the AI system would interact with real apps")

def show_architecture_info():
    """Display information about the AI Mobile AgentX architecture"""
    print("\n🏗️ AI Mobile AgentX Architecture:")
    print("=" * 40)
    print("📸 Screen Capture: Cross-platform mobile screen capture")
    print("👁️  OCR Engine: Multi-engine text recognition (Tesseract, EasyOCR)")
    print("🎯 Tap Coordinator: Human-like interaction with safety bounds")
    print("🤖 Automation Engine: Smart workflow orchestration")
    print("🧠 Position Cache: Intelligent caching for performance")
    print("\n📱 App Connectors Available:")
    print("✉️  Gmail: Email automation")
    print("💬 WhatsApp: Messaging automation") 
    print("🎵 Spotify: Music control")
    print("🗺️  Maps: Navigation and location")
    print("📅 Calendar: Event management")

def show_testing_options():
    """Show available testing options"""
    print("\n🧪 Testing Options:")
    print("=" * 30)
    print("1. Mock Testing (SAFE) - Visual demo without device")
    print("2. Component Testing - Test individual AI components")
    print("3. Connector Testing - Test specific app connectors")
    print("4. Performance Testing - Benchmark OCR and caching")

if __name__ == "__main__":
    try:
        show_architecture_info()
        show_testing_options()
        
        print("\n🎬 Starting comprehensive demo...")
        asyncio.run(run_demo())
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("💡 This is expected if OCR engines aren't installed")
        print("📖 See README.md for full setup instructions")