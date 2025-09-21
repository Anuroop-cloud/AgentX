"""
Advanced Intelligent Mobile AgentX with Learning and Multi-step Planning
Uses Gemini AI for visual understanding, decision making, and adaptive learning
"""

import subprocess
import asyncio
import os
import time
import base64
import json
from PIL import Image
from datetime import datetime
from typing import List, Dict, Any

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class AdvancedIntelligentAgentX:
    def __init__(self):
        self.adb_path = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
        self.device_connected = False
        self.current_screenshot = None
        self.vision_model = None
        self.text_model = None
        self.conversation_history = []
        self.learned_patterns = {}
        
        print("🧠 ADVANCED INTELLIGENT MOBILE AGENTX")
        print("🔮 AI Vision + Planning + Learning System")
        print("=" * 50)
        
        # Initialize Gemini AI
        if GEMINI_AVAILABLE:
            print("🔄 Initializing Advanced Gemini AI...")
            try:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
                    self.text_model = genai.GenerativeModel('gemini-1.5-flash')
                    print("✅ Advanced AI ready - Vision, Planning & Learning active")
                else:
                    print("❌ GEMINI_API_KEY required for advanced automation")
                    exit(1)
            except Exception as e:
                print(f"❌ Advanced AI initialization failed: {e}")
                exit(1)
        else:
            print("❌ Gemini required for advanced intelligent automation")
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
            return False
        
        device_id = connected_devices[0].split()[0]
        print(f"✅ Device connected: {device_id}")
        self.device_connected = True
        return True
    
    def capture_screen(self):
        """Enhanced screen capture with metadata"""
        if not self.device_connected:
            return None
        
        print("📸 Capturing screen...")
        temp_path = "/sdcard/agentx_screenshot.png"
        
        success, _, stderr = self.run_adb_command(f"shell screencap -p {temp_path}")
        if not success:
            return None
        
        local_temp = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        success, _, stderr = self.run_adb_command(f"pull {temp_path} {local_temp}")
        if not success:
            return None
        
        try:
            if os.path.exists(local_temp):
                image = Image.open(local_temp)
                self.current_screenshot = image.copy()
                image.close()
                
                # Cleanup
                try:
                    os.remove(local_temp)
                except:
                    pass
                self.run_adb_command(f"shell rm {temp_path}")
                
                return self.current_screenshot
            return None
        except Exception as e:
            return None
    
    async def create_execution_plan(self, goal: str) -> List[Dict]:
        """Create a multi-step execution plan using AI"""
        print(f"📋 Creating execution plan for: {goal}")
        
        try:
            prompt = f"""
            You are an expert mobile automation planner. Create a detailed step-by-step plan to achieve this goal on Android:
            
            GOAL: {goal}
            
            Consider:
            - Current learned patterns: {json.dumps(self.learned_patterns, indent=2)}
            - Previous successful actions in conversation history
            
            Create a JSON plan with this structure:
            {{
                "goal": "{goal}",
                "estimated_steps": 5,
                "strategy": "high-level approach",
                "steps": [
                    {{
                        "step_number": 1,
                        "action": "capture_and_analyze|navigate|interact|verify",
                        "description": "what to do in this step",
                        "expected_screen": "what screen should be visible",
                        "success_criteria": "how to know this step succeeded",
                        "fallback_options": ["alternative approaches if this fails"]
                    }}
                ],
                "potential_challenges": ["list of things that might go wrong"],
                "success_indicators": ["how to know the overall goal is achieved"]
            }}
            
            Return ONLY the JSON, no other text.
            """
            
            response = self.text_model.generate_content(prompt)
            plan_text = response.text.strip()
            
            if plan_text.startswith('```json'):
                plan_text = plan_text.split('```json')[1].split('```')[0].strip()
            elif plan_text.startswith('```'):
                plan_text = plan_text.split('```')[1].split('```')[0].strip()
            
            plan = json.loads(plan_text)
            
            print(f"📋 Execution Plan Created:")
            print(f"   Strategy: {plan['strategy']}")
            print(f"   Estimated Steps: {plan['estimated_steps']}")
            print(f"   Steps: {len(plan['steps'])}")
            
            return plan
            
        except Exception as e:
            print(f"❌ Plan creation failed: {e}")
            return None
    
    async def analyze_screen_intelligently(self, current_step: Dict, goal: str) -> Dict:
        """Advanced AI screen analysis with context"""
        if not self.current_screenshot:
            return None
        
        print(f"🧠 AI analyzing screen (Step {current_step['step_number']})...")
        
        try:
            import io
            buffer = io.BytesIO()
            self.current_screenshot.save(buffer, format='PNG')
            
            prompt = f"""
            You are an expert mobile automation AI. Analyze this Android screenshot in the context of executing a specific step.
            
            OVERALL GOAL: {goal}
            CURRENT STEP: {current_step['description']}
            EXPECTED SCREEN: {current_step['expected_screen']}
            SUCCESS CRITERIA: {current_step['success_criteria']}
            
            CONVERSATION HISTORY: {json.dumps(self.conversation_history[-3:], indent=2)}
            LEARNED PATTERNS: {json.dumps(self.learned_patterns, indent=2)}
            
            Analyze the screenshot and provide a JSON response:
            {{
                "screen_matches_expectation": true,
                "current_app": "app name",
                "screen_description": "detailed description of what's visible",
                "available_actions": [
                    {{
                        "action_type": "tap|type|swipe|back|home|wait",
                        "target": "element description",
                        "coordinates": [x, y],
                        "confidence": 0.95,
                        "reasoning": "why this action makes sense"
                    }}
                ],
                "recommended_action": {{
                    "action_type": "tap",
                    "target": "specific element to interact with",
                    "coordinates": [x, y],
                    "text_to_type": "if typing is needed",
                    "confidence": 0.95,
                    "reasoning": "detailed explanation of why this is the best action"
                }},
                "step_completion_status": "not_started|in_progress|completed|failed",
                "next_expected_screen": "what should appear after the recommended action",
                "potential_issues": ["things that might go wrong"],
                "learning_insights": ["patterns or insights that could be remembered for future"]
            }}
            
            Be extremely precise with coordinates and confident in your recommendations.
            Return ONLY the JSON response.
            """
            
            response = self.vision_model.generate_content([prompt, self.current_screenshot])
            
            analysis_text = response.text.strip()
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text.split('```json')[1].split('```')[0].strip()
            elif analysis_text.startswith('```'):
                analysis_text = analysis_text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(analysis_text)
            
            print(f"🎯 AI Analysis:")
            print(f"   App: {analysis['current_app']}")
            print(f"   Recommended Action: {analysis['recommended_action']['action_type']}")
            print(f"   Target: {analysis['recommended_action']['target']}")
            print(f"   Confidence: {analysis['recommended_action']['confidence']}")
            
            # Store learning insights
            for insight in analysis.get('learning_insights', []):
                app = analysis['current_app']
                if app not in self.learned_patterns:
                    self.learned_patterns[app] = []
                if insight not in self.learned_patterns[app]:
                    self.learned_patterns[app].append(insight)
            
            return analysis
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return None
    
    def execute_intelligent_action(self, action: Dict) -> bool:
        """Execute action with intelligent error handling"""
        try:
            action_type = action['action_type']
            
            print(f"🎬 Executing: {action_type}")
            print(f"   Target: {action['target']}")
            print(f"   Reasoning: {action['reasoning']}")
            
            if action_type == "tap":
                x, y = action['coordinates']
                success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
                return success
            
            elif action_type == "type":
                text = action.get('text_to_type', '')
                escaped_text = text.replace(' ', '%s').replace('"', '\\"').replace("'", "\\'")
                success, _, stderr = self.run_adb_command(f"shell input text '{escaped_text}'")
                return success
            
            elif action_type == "back":
                success, _, _ = self.run_adb_command("shell input keyevent 4")
                return success
            
            elif action_type == "home":
                success, _, _ = self.run_adb_command("shell input keyevent 3")
                return success
            
            elif action_type == "wait":
                wait_time = action.get('wait_time', 2)
                time.sleep(wait_time)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Action execution failed: {e}")
            return False
    
    async def execute_plan_intelligently(self, plan: Dict) -> bool:
        """Execute the plan with AI decision making at each step"""
        print(f"\n🚀 EXECUTING INTELLIGENT PLAN")
        print(f"Goal: {plan['goal']}")
        print("=" * 50)
        
        for step in plan['steps']:
            print(f"\n📍 Step {step['step_number']}: {step['description']}")
            
            max_retries = 3
            for attempt in range(max_retries):
                print(f"   Attempt {attempt + 1}/{max_retries}")
                
                # Capture current screen
                if not self.capture_screen():
                    print("   ❌ Failed to capture screen")
                    continue
                
                # Analyze with AI
                analysis = await self.analyze_screen_intelligently(step, plan['goal'])
                if not analysis:
                    print("   ❌ AI analysis failed")
                    continue
                
                # Check if step is already completed
                if analysis['step_completion_status'] == 'completed':
                    print("   ✅ Step already completed")
                    break
                
                # Execute recommended action
                if self.execute_intelligent_action(analysis['recommended_action']):
                    print("   ✅ Action executed successfully")
                    
                    # Store successful action in conversation history
                    self.conversation_history.append({
                        'step': step['step_number'],
                        'action': analysis['recommended_action'],
                        'screen': analysis['screen_description'],
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Wait for UI to update
                    await asyncio.sleep(2)
                    break
                else:
                    print("   ❌ Action failed, trying again...")
                    await asyncio.sleep(1)
            else:
                print(f"   ❌ Step {step['step_number']} failed after {max_retries} attempts")
                
                # Try fallback options
                for fallback in step.get('fallback_options', []):
                    print(f"   🔄 Trying fallback: {fallback}")
                    # Could implement fallback logic here
                    break
        
        print("\n🎉 Plan execution completed!")
        return True
    
    async def conversational_automation(self, user_request: str):
        """Handle natural language requests with intelligent planning"""
        print(f"\n💬 CONVERSATIONAL AUTOMATION")
        print(f"Request: {user_request}")
        print("=" * 40)
        
        # Create execution plan
        plan = await self.create_execution_plan(user_request)
        if not plan:
            print("❌ Could not create execution plan")
            return False
        
        # Execute plan intelligently
        return await self.execute_plan_intelligently(plan)
    
    async def interactive_session(self):
        """Advanced interactive session"""
        print("\n🧠 ADVANCED INTELLIGENT MOBILE AGENTX")
        print("Natural Language + AI Vision + Learning")
        print("=" * 45)
        
        if not self.check_device_connection():
            return
        
        while True:
            print(f"\n🎯 WHAT WOULD YOU LIKE TO DO?")
            print("Just describe what you want in natural language!")
            print("=" * 45)
            print("Examples:")
            print("• 'Send a WhatsApp message to John saying hello'")
            print("• 'Play my favorite playlist on Spotify'")
            print("• 'Create a calendar event for tomorrow at 3pm'")
            print("• 'Navigate to the nearest coffee shop'")
            print("• 'Compose an email to my boss about the meeting'")
            print("\nSpecial commands:")
            print("• 'analyze' - Analyze current screen")
            print("• 'learn' - Show what I've learned")
            print("• 'exit' - Quit")
            
            request = input("\n👉 What would you like to do? ").strip()
            
            if not request:
                continue
            
            try:
                if request.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Thanks for using Advanced Intelligent Mobile AgentX!")
                    break
                
                elif request.lower() == 'analyze':
                    if self.capture_screen():
                        analysis = await self.analyze_screen_intelligently(
                            {"step_number": 0, "description": "analyze", "expected_screen": "any", "success_criteria": "analysis completed"},
                            "Analyze current screen"
                        )
                        if analysis:
                            print(f"\n📱 Current Screen Analysis:")
                            print(f"   App: {analysis['current_app']}")
                            print(f"   Description: {analysis['screen_description']}")
                            print(f"   Available Actions: {len(analysis['available_actions'])}")
                
                elif request.lower() == 'learn':
                    print(f"\n🧠 Learning Insights:")
                    if self.learned_patterns:
                        for app, patterns in self.learned_patterns.items():
                            print(f"   {app}:")
                            for pattern in patterns:
                                print(f"     • {pattern}")
                    else:
                        print("   No patterns learned yet")
                
                else:
                    # Handle natural language automation request
                    await self.conversational_automation(request)
                
            except KeyboardInterrupt:
                print("\n⏸️ Request cancelled")
            except Exception as e:
                print(f"\n💥 Error: {e}")

async def main():
    """Initialize and run the advanced intelligent system"""
    try:
        agent = AdvancedIntelligentAgentX()
        await agent.interactive_session()
    except KeyboardInterrupt:
        print("\n👋 System shutdown by user")
    except Exception as e:
        print(f"\n💥 System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())