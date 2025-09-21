"""
AI Mobile AgentX - Complete Integrated System
All automation features with intelligent element detection and fixes
"""

import subprocess
import asyncio
import os
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import cv2
import numpy as np
import json
import requests

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class CompleteMobileAgentX:
    def __init__(self):
        self.adb_path = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
        self.device_connected = False
        self.current_screenshot = None
        self.detected_elements = []
        self.gemini_model = None
        
        print("🤖 AI Mobile AgentX - Complete System Loading...")
        
        # Initialize OCR
        if EASYOCR_AVAILABLE:
            print("🔄 Initializing AI OCR engine...")
            self.ocr_reader = easyocr.Reader(['en'])
            print("✅ AI OCR ready - Multi-language support active")
        else:
            print("⚠️ OCR not available - install easyocr for full functionality")
            self.ocr_reader = None
        
        # Initialize Gemini AI
        if GEMINI_AVAILABLE:
            print("🔄 Initializing Gemini AI for message enhancement...")
            try:
                # Try to get API key from environment variable
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                    print("✅ Gemini AI ready - Message enhancement active")
                else:
                    print("⚠️ GEMINI_API_KEY not found in environment variables")
                    print("   Set GEMINI_API_KEY to enable AI message enhancement")
                    self.gemini_model = None
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.gemini_model = None
        else:
            print("⚠️ Gemini not available - install google-generativeai for AI enhancement")
            self.gemini_model = None
    
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
        """Enhanced screen capture with error handling"""
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
    
    def analyze_screen_with_ai(self):
        """AI-powered screen analysis with intelligent element detection"""
        if not self.current_screenshot or not EASYOCR_AVAILABLE:
            print("⚠️ Cannot analyze screen - missing screenshot or OCR")
            return []
        
        print("🧠 AI analyzing screen elements...")
        
        try:
            # Convert image for OCR processing
            image_array = np.array(self.current_screenshot)
            results = self.ocr_reader.readtext(image_array)
            
            elements = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3 and text.strip():  # Filter low confidence and empty text
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    x1, y1 = int(min(x_coords)), int(min(y_coords))
                    x2, y2 = int(max(x_coords)), int(max(y_coords))
                    
                    elements.append({
                        'text': text.strip(),
                        'bbox': (x1, y1, x2, y2),
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                        'confidence': confidence,
                        'width': x2 - x1,
                        'height': y2 - y1,
                        'area': (x2 - x1) * (y2 - y1),
                        'type': self.classify_element_type(text.strip())
                    })
            
            # Sort by confidence and area
            self.detected_elements = sorted(elements, key=lambda x: (x['confidence'], x['area']), reverse=True)
            
            print(f"✅ AI analysis complete: {len(self.detected_elements)} elements detected")
            
            # Show summary by type
            element_types = {}
            for element in self.detected_elements:
                elem_type = element['type']
                if elem_type not in element_types:
                    element_types[elem_type] = 0
                element_types[elem_type] += 1
            
            print("📊 Element types found:")
            for elem_type, count in element_types.items():
                print(f"   {elem_type}: {count}")
            
            return self.detected_elements
            
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            return []
    
    def classify_element_type(self, text):
        """Classify element type based on text content"""
        text_lower = text.lower()
        
        # App names
        app_keywords = ['gmail', 'whatsapp', 'spotify', 'chrome', 'maps', 'calendar', 'camera', 'phone', 'settings']
        if any(app in text_lower for app in app_keywords):
            return "🚀 App"
        
        # UI elements
        ui_keywords = ['search', 'type', 'message', 'send', 'back', 'home', 'menu']
        if any(ui in text_lower for ui in ui_keywords):
            return "🔧 UI Element"
        
        # Contacts/People
        if len(text) > 2 and text.replace(' ', '').isalpha() and text[0].isupper():
            return "👤 Contact/Person"
        
        # Numbers
        if text.replace('.', '').replace(':', '').replace('%', '').isdigit():
            return "🔢 Number/Time"
        
        # Content
        if len(text) > 10:
            return "📄 Content"
        
        return "❓ Other"
    
    def smart_element_finder(self, target, element_type_filter=None):
        """Intelligently find elements with context awareness"""
        if not self.detected_elements:
            return []
        
        target_lower = target.lower()
        matches = []
        
        # Ultra-strict exclusion patterns for contact filtering
        exclusions = {
            'contact': [
                'search', 'type', 'message', 'call', 'video', 'new chat', 'status',
                'search for', 'search contacts', 'find', 'enter', 'tap to', 'type a message',
                'camera', 'attach', 'emoji', 'send', 'voice', 'chats', 'calls',
                'search chats and contacts', 'search contacts and messages',
                'search...', 'type here', 'enter message', 'tap here', 'click here',
                'search chat', 'find contact', 'look for', 'write message', 'compose',
                'input', 'field', 'box', 'bar', 'placeholder', 'hint', 'label'
            ],
            'app': ['search', 'notification', 'update', 'install'],
            'button': ['title', 'header', 'status', 'toolbar'],
            'content': ['search', 'type', 'input', 'textbox']
        }
        
        exclude_list = exclusions.get(element_type_filter, [])
        
        for element in self.detected_elements:
            text_lower = element['text'].lower()
            
            # Enhanced exclusion check - more aggressive for contacts
            should_exclude = False
            for exclude_pattern in exclude_list:
                if exclude_pattern in text_lower or text_lower in exclude_pattern:
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            # For contacts, ultra-strict filtering
            if element_type_filter == 'contact':
                # Must be substantial text (not single characters or short UI elements)
                if len(element['text'].strip()) < 3:
                    continue
                
                # Must have very large area (contacts in lists are typically large)
                if element['area'] < 5000:  # Increased to 5000 for maximum strictness
                    continue
                
                # Should look like a name (starts with capital, contains letters)
                if not (element['text'][0].isupper() and any(c.isalpha() for c in element['text'])):
                    continue
                
                # Must be positioned in the middle/lower area of screen (where contact lists appear)
                screen_height = 2400  # Typical phone height
                if element['center'][1] < screen_height * 0.3:  # Reject elements in top 30% of screen
                    continue
                
                # Reject if it contains ANY UI text patterns
                ui_patterns = [
                    'search', 'find', 'type', 'tap', 'enter', 'message', 'chat', 'call',
                    'video', 'voice', 'status', 'new', 'contact', 'group', 'broadcast',
                    'archived', 'settings', 'camera', 'gallery', 'document', 'location',
                    'hint', 'placeholder', 'label', 'field', 'input', 'box', 'bar'
                ]
                if any(pattern in element['text'].lower() for pattern in ui_patterns):
                    continue
                
                # Additional UI element detection
                ui_indicators = [':', '•', '○', '●', '▶', '⏸', '⏹', '|', '_', '+', '#', '@', '...', '→', '←', '(', ')']
                if any(indicator in element['text'] for indicator in ui_indicators):
                    continue
                
                # Reject if text is too long (likely to be UI description)
                if len(element['text']) > 25:  # Reduced from 30
                    continue
                
                # Must look like a proper name (only letters, spaces, maybe apostrophes)
                import re
                if not re.match(r"^[A-Z][a-zA-Z\s'.-]*$", element['text']):
                    continue
            
            # Exact match (highest priority)
            if target_lower == text_lower:
                element['match_type'] = 'exact'
                element['priority'] = 3
                matches.append(element)
            # Contains target (medium priority)
            elif target_lower in text_lower:
                element['match_type'] = 'contains'
                element['priority'] = 2
                matches.append(element)
            # Target contains element (lower priority)
            elif text_lower in target_lower and len(text_lower) > 2:
                element['match_type'] = 'partial'
                element['priority'] = 1
                matches.append(element)
        
        # Sort by priority, then by area (larger elements preferred), then by confidence
        matches.sort(key=lambda x: (x['priority'], x['area'], x['confidence']), reverse=True)
        
        return matches
    
    def tap_element(self, element, human_like=True):
        """Execute tap with human-like behavior"""
        x, y = element['center']
        
        # Add human-like randomization
        if human_like:
            import hashlib
            text_hash = int(hashlib.md5(element['text'].encode()).hexdigest()[:8], 16)
            offset_x = (text_hash % 10) - 5  # ±5 pixel variance
            offset_y = ((text_hash >> 4) % 10) - 5
            x += offset_x
            y += offset_y
        
        print(f"👆 Tapping '{element['text']}' at ({x}, {y})")
        print(f"   📊 Confidence: {element['confidence']:.2f}, Type: {element['type']}")
        
        success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        
        if success:
            print("✅ Tap executed successfully")
            return True
        else:
            print(f"❌ Tap failed: {stderr}")
            return False
    
    def type_text(self, text):
        """Type text with proper escaping"""
        # Escape special characters for ADB
        escaped_text = text.replace(' ', '%s').replace('"', '\\"').replace("'", "\\'")
        print(f"⌨️ Typing: {text}")
        
        success, _, stderr = self.run_adb_command(f"shell input text '{escaped_text}'")
        
        if success:
            print("✅ Text typed successfully")
            return True
        else:
            print(f"❌ Text input failed: {stderr}")
            return False
    
    def press_key(self, key):
        """Press system keys"""
        key_codes = {
            'home': '3',
            'back': '4',
            'menu': '82',
            'enter': '66',
            'delete': '67',
            'search': '84',
            'clear': '28'  # Clear key
        }
        
        code = key_codes.get(key.lower(), key)
        print(f"🔘 Pressing {key} key")
        
        success, _, _ = self.run_adb_command(f"shell input keyevent {code}")
        return success
    
    async def clear_search_field(self):
        """Clear any active search field"""
        print("🧹 Clearing search field...")
        
        # Method 1: Select all and delete
        self.run_adb_command("shell input keyevent 29 1")  # Ctrl+A (select all)
        await asyncio.sleep(0.5)
        self.run_adb_command("shell input keyevent 67")    # Delete
        await asyncio.sleep(0.5)
        
        # Method 2: Multiple backspaces as fallback
        for _ in range(20):  # Clear up to 20 characters
            self.run_adb_command("shell input keyevent 67")  # Backspace
            await asyncio.sleep(0.1)
        
        print("✅ Search field cleared")
    
    async def reset_app_state(self, app_name="whatsapp"):
        """Reset app to clean state - minimal approach"""
        print(f"🔄 Ensuring {app_name} is ready...")
        
        # Just one back press to get to main screen if needed
        self.press_key('back')
        await asyncio.sleep(1)
        
        print(f"✅ {app_name} ready")
    
    def enhance_message_with_ai(self, original_message, contact_name=None, context="casual"):
        """Enhance message using Gemini AI"""
        if not self.gemini_model:
            print("⚠️ Gemini AI not available, using original message")
            return original_message
        
        try:
            print("🤖 Enhancing message with Gemini AI...")
            
            # Create a prompt for message enhancement
            prompt = f"""
            Please enhance this message to make it more natural, friendly, and well-written while keeping the original meaning intact.
            
            Original message: "{original_message}"
            Context: {context}
            {"Recipient: " + contact_name if contact_name else ""}
            
            Guidelines:
            - Keep it concise and natural
            - Maintain the original tone and intent
            - Fix any grammar or spelling issues
            - Make it sound more conversational
            - Don't add excessive formality unless context requires it
            - Maximum 2-3 sentences
            
            Enhanced message:
            """
            
            response = self.gemini_model.generate_content(prompt)
            enhanced_message = response.text.strip()
            
            # Remove any quotes that might be added
            enhanced_message = enhanced_message.strip('"').strip("'")
            
            print(f"📝 Original: {original_message}")
            print(f"✨ Enhanced: {enhanced_message}")
            
            return enhanced_message
            
        except Exception as e:
            print(f"❌ Message enhancement failed: {e}")
            print("   Using original message")
            return original_message
    
    async def whatsapp_send_message(self, contact_name, message):
        """Complete WhatsApp messaging with intelligent element detection"""
        print(f"💬 WhatsApp Automation: Sending '{message}' to {contact_name}")
        print("=" * 60)
        
        try:
            # Step 0: Enhance message with AI
            enhanced_message = self.enhance_message_with_ai(message, contact_name, "whatsapp")
            
            # Step 1: Open WhatsApp
            print("🚀 Opening WhatsApp...")
            await self.open_app("whatsapp")
            await asyncio.sleep(3)  # Wait for WhatsApp to fully load
            
            # Step 2: Capture and analyze current screen
            if not self.capture_screen():
                return False
            
            self.analyze_screen_with_ai()
            
            # Step 3: Find search functionality
            print("🔍 Looking for search functionality...")
            search_matches = self.smart_element_finder("search", "button")
            
            if search_matches:
                print(f"   ✅ Found search: '{search_matches[0]['text']}'")
                self.tap_element(search_matches[0])
                await asyncio.sleep(2)
            else:
                print("   ⚠️ No search found, looking for 'New Chat'...")
                new_chat_matches = self.smart_element_finder("new chat", "button")
                if new_chat_matches:
                    self.tap_element(new_chat_matches[0])
                    await asyncio.sleep(2)
                else:
                    print("❌ Cannot find search or new chat")
                    return False
            
            # Step 4: Type contact name directly
            print(f"⌨️ Searching for contact: {contact_name}")
            self.type_text(contact_name)
            await asyncio.sleep(3)  # Wait for search results
            
            # Step 5: Find and tap contact with enhanced filtering
            print("👤 Analyzing search results for contact...")
            self.capture_screen()
            self.analyze_screen_with_ai()
            
            # Debug: Show all detected elements
            print("🔍 DEBUG - All detected elements:")
            for i, elem in enumerate(self.detected_elements[:10], 1):
                print(f"   {i}. '{elem['text']}' - Type: {elem['type']}, Area: {elem['area']}, Conf: {elem['confidence']:.2f}")
            
            contact_matches = self.smart_element_finder(contact_name, "contact")
            
            if contact_matches:
                print(f"\n✅ Found {len(contact_matches)} potential contacts:")
                for i, match in enumerate(contact_matches[:3], 1):
                    print(f"   {i}. '{match['text']}' - {match['match_type']} match, Area: {match['area']}, Conf: {match['confidence']:.2f}")
                
                best_contact = contact_matches[0]
                
                # Enhanced validation criteria - stricter
                if (best_contact['area'] >= 3000 and 
                    best_contact['confidence'] > 0.7 and
                    len(best_contact['text'].strip()) >= 3 and
                    best_contact['text'][0].isupper()):
                    
                    print(f"👆 Tapping on validated contact: '{best_contact['text']}'")
                    self.tap_element(best_contact)
                    await asyncio.sleep(3)
                else:
                    print("❌ Contact doesn't meet strict validation criteria:")
                    print(f"   Area: {best_contact['area']} (need ≥3000)")
                    print(f"   Confidence: {best_contact['confidence']:.2f} (need >0.7)")
                    print(f"   Text length: {len(best_contact['text'].strip())} (need ≥3)")
                    print(f"   Starts with capital: {best_contact['text'][0].isupper()}")
                    return False
            else:
                print(f"❌ Contact '{contact_name}' not found after filtering")
                return False
            
            # Step 6: Type and send enhanced message
            print(f"💬 Composing enhanced message...")
            self.type_text(enhanced_message)
            await asyncio.sleep(1)
            
            # Step 7: Send message
            print("📤 Sending message...")
            
            # Look for send button
            self.capture_screen()
            self.analyze_screen_with_ai()
            
            send_matches = self.smart_element_finder("send", "button")
            if send_matches:
                self.tap_element(send_matches[0])
            else:
                # Fallback to enter key
                print("   📤 Using Enter key to send")
                self.press_key('enter')
            
            print(f"✅ Enhanced message sent to {contact_name}")
            print(f"   Original: '{message}'")
            print(f"   Enhanced: '{enhanced_message}'")
            return True
            
        except Exception as e:
            print(f"❌ WhatsApp automation error: {e}")
            return False
    
    async def gmail_compose_email(self, recipient, subject, body):
        """Gmail email composition automation"""
        print(f"📧 Gmail Automation: Composing email to {recipient}")
        print("=" * 50)
        
        try:
            # Step 1: Open Gmail first
            print("🚀 Opening Gmail...")
            if not await self.open_app("gmail"):
                print("❌ Failed to open Gmail")
                return False
            
            await asyncio.sleep(3)  # Wait for Gmail to fully load
            
            # Look for compose button
            self.capture_screen()
            self.analyze_screen_with_ai()
            
            compose_matches = self.smart_element_finder("compose", "button")
            if compose_matches:
                print(f"✅ Found compose button: '{compose_matches[0]['text']}'")
                self.tap_element(compose_matches[0])
                await asyncio.sleep(2)
            else:
                print("❌ Compose button not found")
                return False
            
            # Fill email fields
            await asyncio.sleep(2)
            
            # Type recipient
            print(f"📧 Adding recipient: {recipient}")
            self.type_text(recipient)
            await asyncio.sleep(1)
            
            # Move to subject (usually tab or tap)
            self.press_key('66')  # Tab key
            await asyncio.sleep(1)
            
            # Type subject
            print(f"📝 Adding subject: {subject}")
            self.type_text(subject)
            await asyncio.sleep(1)
            
            # Move to body
            self.press_key('66')  # Tab key
            await asyncio.sleep(1)
            
            # Type body
            print(f"✍️ Adding body: {body}")
            self.type_text(body)
            await asyncio.sleep(1)
            
            # Send email
            self.capture_screen()
            self.analyze_screen_with_ai()
            
            send_matches = self.smart_element_finder("send", "button")
            if send_matches:
                self.tap_element(send_matches[0])
                print(f"✅ Email sent to {recipient}")
                return True
            else:
                print("❌ Send button not found")
                return False
                
        except Exception as e:
            print(f"❌ Gmail automation error: {e}")
            return False
    
    async def open_app(self, app_name):
        """Open any app by name with multiple search strategies"""
        print(f"🚀 Opening {app_name}...")
        
        # Strategy 1: Try current screen first
        if not self.capture_screen():
            return False
        
        self.analyze_screen_with_ai()
        
        # Find app on current screen
        app_matches = self.smart_element_finder(app_name, "app")
        
        if app_matches:
            best_match = app_matches[0]
            print(f"   ✅ Found {app_name} on current screen: '{best_match['text']}'")
            self.tap_element(best_match)
            await asyncio.sleep(3)
            return True
        
        # Strategy 2: Go to home screen and try again
        print(f"   🏠 {app_name} not found, going to home screen...")
        self.press_key('home')
        await asyncio.sleep(2)
        
        if not self.capture_screen():
            return False
        
        self.analyze_screen_with_ai()
        app_matches = self.smart_element_finder(app_name, "app")
        
        if app_matches:
            best_match = app_matches[0]
            print(f"   ✅ Found {app_name} on home screen: '{best_match['text']}'")
            self.tap_element(best_match)
            await asyncio.sleep(3)
            return True
        
        # Strategy 3: Try different search terms
        alternative_names = {
            'whatsapp': ['whatsapp messenger', 'whatsapp business', 'messenger'],
            'gmail': ['mail', 'google mail', 'email'],
            'spotify': ['spotify music', 'music'],
            'maps': ['google maps', 'navigation'],
            'calendar': ['google calendar', 'cal']
        }
        
        if app_name.lower() in alternative_names:
            print(f"   🔄 Trying alternative names for {app_name}...")
            for alt_name in alternative_names[app_name.lower()]:
                alt_matches = self.smart_element_finder(alt_name, "app")
                if alt_matches:
                    best_match = alt_matches[0]
                    print(f"   ✅ Found {app_name} as '{best_match['text']}'")
                    self.tap_element(best_match)
                    await asyncio.sleep(3)
                    return True
        
        print(f"❌ {app_name} not found on device")
        return False
    
    def show_detected_elements(self, limit=15):
        """Display detected elements for debugging"""
        if not self.detected_elements:
            print("No elements detected")
            return
        
        print(f"\n📋 Detected Elements (showing top {limit}):")
        for i, element in enumerate(self.detected_elements[:limit], 1):
            print(f"   {i:2d}. {element['type']} '{element['text']}' (conf: {element['confidence']:.2f})")
    
    async def interactive_session(self):
        """Main interactive session"""
        print("\n🤖 AI MOBILE AGENTX - COMPLETE AUTOMATION SYSTEM")
        print("=" * 55)
        
        if not self.check_device_connection():
            return
        
        while True:
            print("\n🎯 WHAT WOULD YOU LIKE TO DO?")
            print("=" * 35)
            print("1. 💬 WhatsApp - Send AI-enhanced message")
            print("2. 📧 Gmail - Compose email")
            print("3. 🚀 Open any app")
            print("4. 👆 Tap on text")
            print("5. 📸 Analyze current screen")
            print("6. 🏠 Go to home screen")
            print("7. ⬅️ Go back")
            print("8. 🤖 Test AI message enhancement")
            print("0. 🚪 Exit")
            
            choice = input("\n👉 Enter choice (0-8): ").strip()
            
            try:
                if choice == "0":
                    print("👋 Thanks for using AI Mobile AgentX!")
                    break
                
                elif choice == "1":
                    contact = input("👤 Contact name: ").strip()
                    message = input("💬 Message: ").strip()
                    if contact and message:
                        await self.whatsapp_send_message(contact, message)
                    else:
                        print("❌ Contact name and message required")
                
                elif choice == "2":
                    recipient = input("📧 Recipient email: ").strip()
                    subject = input("📝 Subject: ").strip()
                    body = input("✍️ Message body: ").strip()
                    if recipient and subject and body:
                        await self.gmail_compose_email(recipient, subject, body)
                    else:
                        print("❌ All email fields required")
                
                elif choice == "3":
                    app_name = input("🚀 App name to open: ").strip()
                    if app_name:
                        await self.open_app(app_name)
                    else:
                        print("❌ App name required")
                
                elif choice == "4":
                    text_to_tap = input("👆 Text to tap on: ").strip()
                    if text_to_tap:
                        self.capture_screen()
                        self.analyze_screen_with_ai()
                        matches = self.smart_element_finder(text_to_tap)
                        if matches:
                            self.tap_element(matches[0])
                        else:
                            print(f"❌ '{text_to_tap}' not found")
                    else:
                        print("❌ Text required")
                
                elif choice == "5":
                    self.capture_screen()
                    self.analyze_screen_with_ai()
                    self.show_detected_elements()
                
                elif choice == "6":
                    self.press_key('home')
                    print("✅ Went to home screen")
                
                elif choice == "7":
                    self.press_key('back')
                    print("✅ Went back")
                
                elif choice == "8":
                    test_message = input("🤖 Enter message to enhance: ").strip()
                    if test_message:
                        enhanced = self.enhance_message_with_ai(test_message)
                        print(f"\n📝 Original: {test_message}")
                        print(f"✨ Enhanced: {enhanced}")
                    else:
                        print("❌ Message required")
                
                else:
                    print("❌ Invalid choice")
                
            except KeyboardInterrupt:
                print("\n⏸️ Action cancelled")
            except Exception as e:
                print(f"\n💥 Error: {e}")

async def main():
    """Initialize and run the complete system"""
    try:
        agent = CompleteMobileAgentX()
        await agent.interactive_session()
    except KeyboardInterrupt:
        print("\n👋 System shutdown by user")
    except Exception as e:
        print(f"\n💥 System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())