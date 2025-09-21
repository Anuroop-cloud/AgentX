"""
Intelligent AI Mobile AgentX - Vision-based automation using Gemini AI
Analyzes screenshots with AI to make intelligent decisions instead of hardcoded rules
"""

import subprocess
import asyncio
import os
import time
import base64
from PIL import Image
from datetime import datetime
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class IntelligentMobileAgentX:
    def __init__(self):
        self.adb_path = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
        self.device_connected = False
        self.current_screenshot = None
        self.vision_model = None
        self.text_model = None
        
        print("🧠 Intelligent AI Mobile AgentX - Vision-based Automation")
        print("=" * 60)
        
        # Initialize Gemini AI
        if GEMINI_AVAILABLE:
            print("🔄 Initializing Gemini AI Vision...")
            try:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
                    self.text_model = genai.GenerativeModel('gemini-1.5-flash')
                    print("✅ Gemini AI Vision ready - Intelligent automation active")
                else:
                    print("❌ GEMINI_API_KEY not found in environment variables")
                    print("   This system requires Gemini API for intelligent automation")
                    exit(1)
            except Exception as e:
                print(f"❌ Gemini initialization failed: {e}")
                exit(1)
        else:
            print("❌ Gemini not available - install google-generativeai")
            exit(1)
    
    def run_adb_command(self, command):
        """Execute ADB command with error handling"""
        try:
            full_command = [self.adb_path] + command.split()
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
    
    def check_device_connection(self):
        """Check and establish device connection"""
        print("📱 Checking device connection...")
        success, stdout, stderr = self.run_adb_command("devices")
        
        if not success:
            print(f"❌ ADB error: {stderr}")
            return False
        
        lines = stdout.strip().split('\n')[1:]
        connected_devices = [line for line in lines if line.strip() and 'device' in line]
        
        if not connected_devices:
            print("❌ No devices connected")
            print("\n🔧 Setup Instructions:")
            print("   1. Enable Developer Options: Settings → About Phone → Tap 'Build Number' 7 times")
            print("   2. Enable USB Debugging: Settings → Developer Options → USB Debugging")
            print("   3. Connect device via USB and allow debugging")
            return False
        
        device_id = connected_devices[0].split()[0]
        print(f"✅ Device connected: {device_id}")
        self.device_connected = True
        return True
    
    def capture_screen(self):
        """Capture device screen"""
        if not self.device_connected:
            print("❌ No device connected for screen capture")
            return None
        
        print("📸 Capturing device screen...")
        temp_path = "/sdcard/agentx_screenshot.png"
        
        # Capture screenshot on device
        success, _, stderr = self.run_adb_command(f"shell screencap -p {temp_path}")
        if not success:
            print(f"❌ Screenshot capture failed: {stderr}")
            return None
        
        # Pull screenshot to local machine
        local_temp = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        success, _, stderr = self.run_adb_command(f"pull {temp_path} {local_temp}")
        if not success:
            print(f"❌ Screenshot pull failed: {stderr}")
            return None
        
        try:
            if os.path.exists(local_temp):
                image = Image.open(local_temp)
                self.current_screenshot = image.copy()
                image.close()
                
                # Cleanup
                time.sleep(0.1)
                try:
                    os.remove(local_temp)
                except:
                    pass
                self.run_adb_command(f"shell rm {temp_path}")
                
                print(f"✅ Screenshot captured: {self.current_screenshot.size[0]}x{self.current_screenshot.size[1]}")
                return self.current_screenshot
            else:
                print("❌ Screenshot file not found")
                return None
                
        except Exception as e:
            print(f"❌ Screenshot processing error: {e}")
            return None
    
    def analyze_screen_with_ai(self, goal, context=""):
        """Analyze screen using AI vision to determine next action"""
        if not self.current_screenshot:
            print("❌ No screenshot available for analysis")
            return None
        
        print(f"🧠 AI analyzing screen for goal: {goal}")
        
        try:
            # Convert image to base64 for API
            import io
            buffer = io.BytesIO()
            self.current_screenshot.save(buffer, format='PNG')
            image_data = buffer.getvalue()
            
            prompt = f"""
            You are an intelligent mobile automation assistant. Analyze this Android screenshot and determine the best next action to achieve the goal.
            
            GOAL: {goal}
            CONTEXT: {context}
            
            Please analyze the screenshot and provide a JSON response with the following structure:
            {{
                "action_type": "tap|type|swipe|back|home|wait",
                "target_element": "description of element to interact with",
                "coordinates": [x, y],
                "text_to_type": "text to input if action is type",
                "confidence": 0.95,
                "reasoning": "why this action will help achieve the goal",
                "next_steps": ["what should happen after this action"],
                "screen_analysis": "what you see on the screen",
                "elements_detected": ["list of key UI elements you can see"],
                "app_state": "what app and screen we're currently on"
            }}
            
            Guidelines:
            - Be very specific about coordinates - use the exact center of elements
            - Only suggest actions that are clearly visible on screen
            - For WhatsApp: distinguish between contacts and UI elements carefully
            - For text input: be precise about what to type
            - Use confidence scores to indicate certainty
            - If goal cannot be achieved with current screen, suggest navigation steps
            
            Return ONLY the JSON response, no other text.
            """
            
            response = self.vision_model.generate_content([prompt, self.current_screenshot])
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(response_text)
            
            print(f"🎯 AI Analysis:")
            print(f"   Action: {analysis['action_type']}")
            print(f"   Target: {analysis['target_element']}")
            print(f"   Confidence: {analysis['confidence']}")
            print(f"   Reasoning: {analysis['reasoning']}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return None
    
    def execute_action(self, action_analysis):
        """Execute the action determined by AI"""
        if not action_analysis:
            return False
        
        action = action_analysis['action_type']
        
        try:
            if action == "tap":
                x, y = action_analysis['coordinates']
                print(f"👆 Tapping at ({x}, {y}) - {action_analysis['target_element']}")
                success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
                return success
            
            elif action == "type":
                text = action_analysis['text_to_type']
                print(f"⌨️ Typing: {text}")
                # Escape special characters for ADB
                escaped_text = text.replace(' ', '%s').replace('"', '\\"').replace("'", "\\'")
                success, _, stderr = self.run_adb_command(f"shell input text '{escaped_text}'")
                return success
            
            elif action == "swipe":
                # Implement swipe if coordinates provided
                print("👆 Swiping...")
                return True
            
            elif action == "back":
                print("⬅️ Going back")
                success, _, _ = self.run_adb_command("shell input keyevent 4")
                return success
            
            elif action == "home":
                print("🏠 Going home")
                success, _, _ = self.run_adb_command("shell input keyevent 3")
                return success
            
            elif action == "wait":
                wait_time = action_analysis.get('wait_time', 2)
                print(f"⏱️ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return True
            
            else:
                print(f"❌ Unknown action: {action}")
                return False
                
        except Exception as e:
            print(f"❌ Action execution failed: {e}")
            return False
    
    async def intelligent_automation(self, goal, max_steps=10):
        """Perform intelligent automation to achieve a goal"""
        print(f"\n🎯 INTELLIGENT AUTOMATION")
        print(f"Goal: {goal}")
        print("=" * 50)
        
        context = ""
        
        for step in range(max_steps):
            print(f"\n📍 Step {step + 1}/{max_steps}")
            
            # Capture current screen
            if not self.capture_screen():
                print("❌ Failed to capture screen")
                return False
            
            # Analyze with AI
            analysis = self.analyze_screen_with_ai(goal, context)
            if not analysis:
                print("❌ AI analysis failed")
                return False
            
            # Check if goal is achieved
            if analysis.get('goal_achieved', False):
                print("🎉 Goal achieved!")
                return True
            
            # Execute action
            if not self.execute_action(analysis):
                print("❌ Action execution failed")
                return False
            
            # Update context for next iteration
            context = f"Previous action: {analysis['action_type']} on {analysis['target_element']}. Screen state: {analysis['app_state']}"
            
            # Wait before next step
            await asyncio.sleep(2)
        
        print("⚠️ Maximum steps reached. Goal may not be fully achieved.")
        return False
    
    async def smart_whatsapp_message(self, contact_name, message):
        """Send WhatsApp message using intelligent automation"""
        
        # First enhance the message with AI
        enhanced_message = await self.enhance_message(message, contact_name)
        
        goal = f"Send WhatsApp message '{enhanced_message}' to contact '{contact_name}'"
        
        print(f"💬 Smart WhatsApp Message")
        print(f"📝 Original: {message}")
        print(f"✨ Enhanced: {enhanced_message}")
        print(f"👤 To: {contact_name}")
        
        return await self.intelligent_automation(goal)
    
    async def enhance_message(self, message, recipient=None):
        """Enhance message using AI"""
        try:
            prompt = f"""
            Enhance this message to be more natural, friendly, and well-written while keeping the original meaning:
            
            Message: "{message}"
            {"Recipient: " + recipient if recipient else ""}
            
            Make it:
            - Natural and conversational
            - Grammatically correct
            - Appropriately casual/formal
            - Concise but complete
            
            Return only the enhanced message, no quotes or explanations.
            """
            
            response = self.text_model.generate_content(prompt)
            enhanced = response.text.strip().strip('"').strip("'")
            
            return enhanced
        except:
            return message  # Fallback to original
    
    async def interactive_session(self):
        """Main interactive session with intelligent automation"""
        print("\n🧠 INTELLIGENT AI MOBILE AGENTX")
        print("Powered by Gemini Vision AI")
        print("=" * 40)
        
        if not self.check_device_connection():
            return
        
        while True:
            print("\n🎯 INTELLIGENT AUTOMATION OPTIONS")
            print("=" * 35)
            print("1. 💬 Smart WhatsApp message")
            print("2. 📧 Smart Gmail compose")
            print("3. 🚀 Open and navigate to app")
            print("4. 🎵 Control Spotify")
            print("5. 🗺️ Navigate with Maps")
            print("6. 📅 Create calendar event")
            print("7. 🤖 Custom goal automation")
            print("8. 📸 Analyze current screen")
            print("0. 🚪 Exit")
            
            choice = input("\n👉 Enter choice (0-8): ").strip()
            
            try:
                if choice == "0":
                    print("👋 Thanks for using Intelligent Mobile AgentX!")
                    break
                
                elif choice == "1":
                    contact = input("👤 Contact name: ").strip()
                    message = input("💬 Message: ").strip()
                    if contact and message:
                        await self.smart_whatsapp_message(contact, message)
                    else:
                        print("❌ Contact name and message required")
                
                elif choice == "2":
                    recipient = input("📧 Recipient: ").strip()
                    subject = input("📝 Subject: ").strip()
                    body = input("✍️ Body: ").strip()
                    if recipient and subject and body:
                        goal = f"Compose and send Gmail email to '{recipient}' with subject '{subject}' and body '{body}'"
                        await self.intelligent_automation(goal)
                    else:
                        print("❌ All fields required")
                
                elif choice == "3":
                    app_name = input("🚀 App to open: ").strip()
                    if app_name:
                        goal = f"Open {app_name} app and navigate to main screen"
                        await self.intelligent_automation(goal)
                    else:
                        print("❌ App name required")
                
                elif choice == "4":
                    action = input("🎵 Spotify action (play song, pause, next, etc.): ").strip()
                    if action:
                        goal = f"Open Spotify and {action}"
                        await self.intelligent_automation(goal)
                    else:
                        print("❌ Action required")
                
                elif choice == "5":
                    destination = input("🗺️ Where to navigate: ").strip()
                    if destination:
                        goal = f"Open Google Maps and navigate to {destination}"
                        await self.intelligent_automation(goal)
                    else:
                        print("❌ Destination required")
                
                elif choice == "6":
                    event_title = input("📅 Event title: ").strip()
                    if event_title:
                        goal = f"Open Calendar app and create event '{event_title}'"
                        await self.intelligent_automation(goal)
                    else:
                        print("❌ Event title required")
                
                elif choice == "7":
                    custom_goal = input("🤖 Describe what you want to do: ").strip()
                    if custom_goal:
                        await self.intelligent_automation(custom_goal)
                    else:
                        print("❌ Goal description required")
                
                elif choice == "8":
                    if self.capture_screen():
                        analysis = self.analyze_screen_with_ai("Analyze this screen and describe what you see")
                        if analysis:
                            print(f"\n📱 Screen Analysis:")
                            print(f"   App: {analysis.get('app_state', 'Unknown')}")
                            print(f"   Description: {analysis.get('screen_analysis', 'No analysis')}")
                            print(f"   Elements: {', '.join(analysis.get('elements_detected', []))}")
                    else:
                        print("❌ Failed to capture screen")
                
                else:
                    print("❌ Invalid choice")
                
            except KeyboardInterrupt:
                print("\n⏸️ Action cancelled")
            except Exception as e:
                print(f"\n💥 Error: {e}")

async def main():
    """Initialize and run the intelligent system"""
    try:
        agent = IntelligentMobileAgentX()
        await agent.interactive_session()
    except KeyboardInterrupt:
        print("\n👋 System shutdown by user")
    except Exception as e:
        print(f"\n💥 System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())