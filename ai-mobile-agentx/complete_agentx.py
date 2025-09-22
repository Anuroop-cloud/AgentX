"""
AI Mobile AgentX - Complete Integrated System
All automation features combined with AI intelligence
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)es with intelligent element detection and fixes
"""

import subprocess
import asyncio
import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import cv2
import numpy as np
import json
import requests

# Optional dependencies with better error handling
EASYOCR_AVAILABLE = False
GEMINI_AVAILABLE = False
OCR_IMPORT_ERROR = None
GEMINI_IMPORT_ERROR = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError as e:
    OCR_IMPORT_ERROR = str(e)
    print(f"⚠️ easyocr import failed: {e}")
    print("💡 To enable OCR features, install easyocr: pip install easyocr")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_IMPORT_ERROR = str(e)
    print(f"⚠️ google-generativeai import failed: {e}")
    print("💡 To enable AI features, install google-generativeai: pip install google-generativeai")

class CompleteMobileAgentX:
    def __init__(self):
        # OS-agnostic ADB path detection
        self.adb_path = self._get_adb_path()
        self.device_connected = False
        self.current_screenshot = None
        self.detected_elements = []
        self.gemini_model = None

    def _get_adb_path(self):
        """Get ADB path in an OS-agnostic way"""
        # Common ADB paths for different operating systems
        paths = {
            'linux': [
                '/usr/bin/adb',  # Standard Linux path
                '/usr/local/bin/adb',  # Local install
                os.path.expanduser('~/Android/Sdk/platform-tools/adb'),  # User's home Android SDK
                '/opt/android-sdk/platform-tools/adb'  # Optional Android SDK location
            ],
            'darwin': [
                '/usr/local/bin/adb',
                os.path.expanduser('~/Library/Android/sdk/platform-tools/adb')
            ],
            'win32': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Android', 'Sdk', 'platform-tools', 'adb.exe'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'Android', 'android-sdk', 'platform-tools', 'adb.exe'),
                'C:\\android-tools\\platform-tools\\adb.exe'
            ]
        }

        # Get current OS
        current_os = sys.platform

        # Check all possible paths for current OS
        if current_os in paths:
            for path in paths[current_os]:
                if os.path.isfile(path):
                    print(f"✅ Found ADB at: {path}")
                    return path

        # If ADB is in system PATH
        import shutil
        adb_in_path = shutil.which('adb')
        if adb_in_path:
            print(f"✅ Found ADB in PATH: {adb_in_path}")
            return adb_in_path

        print("⚠️ ADB not found in common locations. Please ensure Android SDK platform-tools are installed.")
        return 'adb'  # Fallback to just 'adb', assuming it might be in PATH
        
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
                # Use provided API key
                api_key = "AIzaSyBJEa2zvaScpco-WQ7z9NSv__-shLIkekU"
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini AI ready - Message enhancement active")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.gemini_model = None
        else:
            print("⚠️ Gemini not available - install google-generativeai for AI enhancement")
            self.gemini_model = None
    
    def run_adb_command(self, command):
        """Execute ADB command with error handling"""
        try:
            # Use instance adb_path which is already OS-agnostic
            full_command = f"{self.adb_path} {command}"
            
            if sys.platform == 'win32':
                # On Windows, we need to split the command differently
                import shlex
                cmd_parts = shlex.split(full_command, posix=False)
            else:
                # On Unix-like systems, regular split works fine
                cmd_parts = full_command.split()
            
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_device_connection(self):
        """Check and establish device connection"""
        print("📱 Checking device connection...")

        # First, check if ADB server is running
        success, stdout, stderr = self.run_adb_command("start-server")
        if not success:
            print(f"❌ Failed to start ADB server: {stderr}")
            if sys.platform == 'linux':
                print("\n🔧 Linux Setup Tips:")
                print("   1. Ensure adb is installed: sudo dnf install android-tools (Fedora)")
                print("   2. Add udev rules for Android devices:")
                print("      sudo wget https://raw.githubusercontent.com/M0Rf30/android-udev-rules/master/51-android.rules -O /etc/udev/rules.d/51-android.rules")
                print("      sudo udevadm control --reload-rules")
                print("   3. Add your user to plugdev group: sudo usermod -aG plugdev $USER")
                print("   4. Restart udev: sudo service udev restart")
            return False

        # Check connected devices
        success, stdout, stderr = self.run_adb_command("devices")
        if not success:
            print(f"❌ ADB error: {stderr}")
            return False
        
        lines = stdout.strip().split('\n')[1:]
        connected_devices = [line for line in lines if line.strip() and 'device' in line]
        
        if not connected_devices:
            print("❌ No devices connected")
            print("\n🔧 General Setup Instructions:")
            print("   1. Enable Developer Options: Settings → About Phone → Tap 'Build Number' 7 times")
            print("   2. Enable USB Debugging: Settings → Developer Options → USB Debugging")
            print("   3. Connect device via USB and allow debugging")
            
            # Linux-specific USB debugging tips
            if sys.platform == 'linux':
                print("\n🐧 Linux-specific tips:")
                print("   • Run 'lsusb' to verify device is detected")
                print("   • Check 'dmesg' for USB connection issues")
                print("   • Try different USB ports and cables")
                print("   • Ensure device is in File Transfer (MTP) mode")
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
    
    def find_green_send_button(self):
        """Find green send button (#00FF00) using color detection"""
        if not self.current_screenshot:
            print("❌ No screenshot available for color detection")
            return None
        
        try:
            # Convert PIL image to OpenCV format
            img_array = np.array(self.current_screenshot)
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
            
            # Define green color ranges for WhatsApp send button (multiple shades)
            # WhatsApp uses different greens: #25D366 (WhatsApp green), #00FF00 (bright green)
            
            # Range 1: WhatsApp green (#25D366) - Hue around 140-160 in HSV
            lower_green1 = np.array([40, 100, 50])    # WhatsApp green range
            upper_green1 = np.array([80, 255, 255])
            
            # Range 2: Bright green (#00FF00) - Pure green
            lower_green2 = np.array([50, 200, 200])   # Bright green
            upper_green2 = np.array([70, 255, 255])
            
            # Create masks for both green ranges
            green_mask1 = cv2.inRange(img_hsv, lower_green1, upper_green1)
            green_mask2 = cv2.inRange(img_hsv, lower_green2, upper_green2)
            green_mask = cv2.bitwise_or(green_mask1, green_mask2)
            
            # Find contours of green regions
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                print("🔍 No green regions found")
                return None
            
            # Filter contours by size (button should be reasonably sized)
            min_area = 100  # Minimum button area
            max_area = 5000  # Maximum button area
            
            button_candidates = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area <= area <= max_area:
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check if it's roughly button-shaped (not too thin/tall)
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.5 <= aspect_ratio <= 3.0:
                        # Calculate center point
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        # Prefer buttons in the bottom half of screen (where send buttons usually are)
                        screen_height = self.current_screenshot.size[1]
                        if center_y > screen_height * 0.6:  # Bottom 40% of screen
                            button_candidates.append((center_x, center_y, area))
            
            if not button_candidates:
                print("🔍 No suitable green button candidates found")
                return None
            
            # Sort by area (largest first) and prefer rightmost position
            button_candidates.sort(key=lambda x: (x[2], x[0]), reverse=True)
            
            best_button = button_candidates[0]
            print(f"🟢 Found green send button at ({best_button[0]}, {best_button[1]}) with area {best_button[2]}")
            
            return (best_button[0], best_button[1])
            
        except Exception as e:
            print(f"❌ Green button detection failed: {e}")
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
        """Intelligently find elements with context awareness and improved contact selection"""
        if not self.detected_elements:
            return []
        
        target_lower = target.lower()
        matches = []
        exact_matches = []
        fuzzy_matches = []
        
        # Get screen dimensions for area filtering
        screen_height = self.current_screenshot.height if self.current_screenshot else 2400
        screen_width = self.current_screenshot.width if self.current_screenshot else 1080
        
        # Define search bar exclusion zone (top 15% of screen)
        search_bar_zone = screen_height * 0.15
        
        # Define contact list area (main content area)
        contact_list_start = screen_height * 0.25  # Below search bar
        contact_list_end = screen_height * 0.85    # Above bottom navigation
        
        for element in self.detected_elements:
            text_lower = element['text'].lower()
            
            # PRIORITY 1: EXACT MATCH FILTERING
            if target_lower == text_lower:
                # For exact matches, apply strict contact filtering
                if element_type_filter == 'contact':
                    # Must be in contact list area (not in search bar region)
                    if element['center'][1] <= search_bar_zone:
                        print(f"❌ Exact match '{element['text']}' rejected - in search bar zone")
                        continue
                    
                    # Must be in main contact list area
                    if not (contact_list_start <= element['center'][1] <= contact_list_end):
                        print(f"❌ Exact match '{element['text']}' rejected - outside contact list area")
                        continue
                    
                    # Must have reasonable area for a contact (not tiny UI elements)
                    if element['area'] < 2000:
                        print(f"❌ Exact match '{element['text']}' rejected - area too small ({element['area']})")
                        continue
                    
                    print(f"✅ EXACT MATCH found: '{element['text']}' at {element['center']}")
                    element['match_type'] = 'exact'
                    element['priority'] = 100  # Highest priority for exact matches
                    exact_matches.append(element)
                else:
                    element['match_type'] = 'exact'
                    element['priority'] = 10
                    exact_matches.append(element)
                continue
            
            # PRIORITY 2: FUZZY MATCH FILTERING (only if no exact matches)
            # Skip fuzzy matching for contacts if we already have exact matches
            if element_type_filter == 'contact' and exact_matches:
                continue
            
            # Enhanced exclusion for fuzzy matches
            if element_type_filter == 'contact':
                # Strict position filtering - exclude search bar zone
                if element['center'][1] <= search_bar_zone:
                    continue
                
                # Must be in contact list area
                if not (contact_list_start <= element['center'][1] <= contact_list_end):
                    continue
                
                # Must be substantial text
                if len(element['text'].strip()) < 3:
                    continue
                
                # Must have reasonable area
                if element['area'] < 3000:
                    continue
                
                # Exclude obvious UI elements
                ui_patterns = [
                    'search', 'find', 'type', 'tap', 'enter', 'message', 'chat', 'call',
                    'video', 'voice', 'status', 'new', 'contact', 'group', 'file', 'manager',
                    'telegram', 'instagram', 'brave', 'calendar', 'discord', 'whatsapp'
                ]
                if any(pattern in text_lower for pattern in ui_patterns):
                    continue
                
                # Must look like a proper name
                import re
                if not re.match(r"^[A-Z][a-zA-Z\s'.-]*$", element['text']):
                    continue
            
            # Fuzzy matching logic
            if target_lower in text_lower:
                element['match_type'] = 'contains'
                element['priority'] = 5
                fuzzy_matches.append(element)
            elif text_lower in target_lower and len(text_lower) > 2:
                element['match_type'] = 'partial'
                element['priority'] = 2
                fuzzy_matches.append(element)
        
        # Combine results: Exact matches first, then fuzzy matches
        all_matches = exact_matches + fuzzy_matches
        
        # Sort by priority (exact matches will naturally be first due to higher priority)
        all_matches.sort(key=lambda x: (x['priority'], x['area'], x['confidence']), reverse=True)
        
        # Debug logging
        if element_type_filter == 'contact':
            print(f"🔍 Contact Search Results for '{target}':")
            print(f"   Exact matches: {len(exact_matches)}")
            print(f"   Fuzzy matches: {len(fuzzy_matches)}")
            print(f"   Search bar zone: y < {search_bar_zone}")
            print(f"   Contact list area: {contact_list_start} < y < {contact_list_end}")
        
        return all_matches
    
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
        # Clean the text first - remove newlines and extra formatting
        clean_text = text.replace('\n', ' ').replace('\r', '').strip()
        # If it contains "Or:" suggestions, use only the first part
        if "Or:" in clean_text:
            clean_text = clean_text.split("Or:")[0].strip()
        
        # Escape special characters for ADB shell
        escaped_text = clean_text.replace(' ', '%s').replace('"', '\\"').replace("'", "\\'").replace('!', '\\!')
        print(f"⌨️ Typing: {clean_text}")
        
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
            Enhance this message to make it more natural and friendly while keeping the original meaning. Provide ONLY ONE improved message, no alternatives or options.
            
            Original: "{original_message}"
            Context: {context}
            {"Recipient: " + contact_name if contact_name else ""}
            
            Requirements:
            - Return only the enhanced message, no explanations
            - Keep it concise (1-2 sentences max)
            - Make it natural and conversational
            - Fix grammar/spelling if needed
            - Don't provide multiple options or use "Or:"
            - Don't add quotes around the response
            
            Enhanced message:
            """
            
            response = self.gemini_model.generate_content(prompt)
            enhanced_message = response.text.strip()
            
            # Clean the response thoroughly
            enhanced_message = enhanced_message.strip('"').strip("'")
            
            # Remove any unwanted prefixes/suffixes
            prefixes_to_remove = ["Enhanced message:", "Here's the enhanced message:", "Enhanced:", "Message:"]
            for prefix in prefixes_to_remove:
                if enhanced_message.startswith(prefix):
                    enhanced_message = enhanced_message[len(prefix):].strip()
            
            # If there are multiple lines or "Or:" alternatives, take only the first line
            if "\n" in enhanced_message or "Or:" in enhanced_message:
                enhanced_message = enhanced_message.split("\n")[0].split("Or:")[0].strip()
            
            # Final cleanup
            enhanced_message = enhanced_message.strip()
            
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
            
            # SIMPLE SOLUTION: Click in the contact area below search
            print("🎯 SMART CONTACT SELECTION: Using area-based clicking")
            
            # Find the first contact that appears in search results (simple approach)
            screen_height = self.current_screenshot.height if self.current_screenshot else 2400
            screen_width = self.current_screenshot.width if self.current_screenshot else 1080
            
            # Define contact area (below search bar, in main content)
            contact_area_start_y = int(screen_height * 0.3)  # Start at 30% down
            contact_area_end_y = int(screen_height * 0.7)    # End at 70% down
            center_x = screen_width // 2                      # Click in center horizontally
            
            # Try clicking at different heights in the contact area
            click_positions = [
                (center_x, contact_area_start_y),              # Top of contact area
                (center_x, contact_area_start_y + 100),        # Slightly lower
                (center_x, contact_area_start_y + 200),        # Even lower
            ]
            
            contact_opened = False
            
            for attempt, (x, y) in enumerate(click_positions, 1):
                print(f"\n🎯 Attempt {attempt}: Clicking in contact area at ({x}, {y})")
                
                # Direct tap in contact area
                success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
                
                if success:
                    print("✅ Tap executed in contact area")
                    await asyncio.sleep(3)  # Wait for chat to open
                    
                    # Check if chat opened
                    print("🔍 Checking if chat screen opened...")
                    self.capture_screen()
                    self.analyze_screen_with_ai()
                    
                    # Show all detected text for debugging
                    print("📱 Current screen text detected:")
                    for element in self.detected_elements[:10]:  # Show first 10 elements
                        print(f"   📝 '{element['text'][:50]}...' (conf: {element['confidence']:.2f})")
                    
                    # Look for message input field (indicates chat screen) - expanded phrases
                    message_input_found = False
                    input_phrases = [
                        'type a message', 'message', 'type here', 'type your message',
                        'write a message', 'enter message', 'text message', 'send message',
                        'compose', 'write here', 'start typing', 'type something'
                    ]
                    
                    for element in self.detected_elements:
                        text_lower = element['text'].lower()
                        if any(phrase in text_lower for phrase in input_phrases):
                            message_input_found = True
                            print(f"✅ Found input indicator: '{element['text']}'")
                            break
                    
                    # Additional check: Look for chat-specific elements and conversation content
                    if not message_input_found:
                        # Method 1: Look for UI elements
                        chat_indicators = ['attach', 'emoji', 'camera', 'mic', 'send', 'voice']
                        chat_elements_found = 0
                        for element in self.detected_elements:
                            text_lower = element['text'].lower()
                            if any(indicator in text_lower for indicator in chat_indicators):
                                chat_elements_found += 1
                        
                        # Method 2: Look for conversation patterns (messages, times)
                        conversation_indicators = 0
                        time_pattern_found = False
                        message_content_found = False
                        
                        for element in self.detected_elements:
                            text = element['text'].strip()
                            text_lower = text.lower()
                            
                            # Check for time patterns (like "52 secs", "Thursday", "Monday")
                            if any(time_word in text_lower for time_word in ['sec', 'min', 'hour', 'day', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'yesterday', 'today']):
                                time_pattern_found = True
                                conversation_indicators += 1
                            
                            # Check for message-like content (short phrases, not UI elements)
                            if len(text) > 2 and len(text) < 50 and text_lower not in ['chats', 'calls', 'status', 'search', 'back']:
                                if any(char.isalpha() for char in text):  # Contains letters
                                    message_content_found = True
                                    conversation_indicators += 1
                        
                        # If we have chat elements OR conversation indicators, consider it a chat screen
                        if chat_elements_found >= 1 or conversation_indicators >= 3:
                            message_input_found = True
                            if chat_elements_found >= 1:
                                print(f"✅ Chat screen detected via UI elements ({chat_elements_found} indicators)")
                            else:
                                print(f"✅ Chat screen detected via conversation content ({conversation_indicators} indicators)")
                    
                    if message_input_found:
                        print(f"✅ SUCCESS! Chat opened after clicking at ({x}, {y})")
                        contact_opened = True
                        break
                    else:
                        print(f"❌ Attempt {attempt} - no chat screen detected")
                else:
                    print(f"❌ Tap failed: {stderr}")
                
                if attempt < len(click_positions):
                    print("🔄 Trying next position...")
            
            if not contact_opened:
                print("❌ Failed to open any chat by clicking in contact area")
                return False
            
            # Step 6: Click below chats (simplified approach)
            print("� Using simplified approach: clicking in message input area...")
            
            # Get screen dimensions
            screen_width = 1080   # Common Android width
            screen_height = 2340  # Common Android height
            
            # Click in the bottom area where message input is typically located
            # This is more reliable than trying to OCR the input field
            input_x = screen_width // 2       # Center horizontally
            input_y = int(screen_height * 0.9) # 90% down the screen (bottom area)
            
            success, _, stderr = self.run_adb_command(f"shell input tap {input_x} {input_y}")
            if success:
                print(f"✅ Tapped message input area at ({input_x}, {input_y})")
                await asyncio.sleep(1)
            else:
                print(f"❌ Failed to tap input area: {stderr}")
                # Try a slightly different position
                input_y = int(screen_height * 0.85)
                success, _, stderr = self.run_adb_command(f"shell input tap {input_x} {input_y}")
                if success:
                    print(f"✅ Fallback tap successful at ({input_x}, {input_y})")
                    await asyncio.sleep(1)
                else:
                    print(f"❌ Fallback tap also failed: {stderr}")
            
            # Step 7: Type enhanced message
            print(f"💬 Composing enhanced message...")
            self.type_text(enhanced_message)
            await asyncio.sleep(1)
            
            # Step 8: Send message using send button only
            print("📤 Sending message...")
            
            # Look for send button with improved detection
            self.capture_screen()
            self.analyze_screen_with_ai()
            
            # Try multiple approaches to find send button
            send_button_found = False
            
            # Method 1: Look for "send" text
            send_matches = self.smart_element_finder("send", "button")
            if send_matches:
                print(f"✅ Found send button via text search")
                self.tap_element(send_matches[0])
                send_button_found = True
            
            # Method 2: Look for arrow/plane icon (common send icons) with better filtering
            if not send_button_found:
                screen_height = self.current_screenshot.size[1]
                screen_width = self.current_screenshot.size[0]
                
                for element in self.detected_elements:
                    try:
                        if 'coordinates' not in element:
                            continue
                        text_lower = element['text'].lower()
                        x, y = element['coordinates']
                        
                        # Only consider elements in the bottom-right quadrant for send buttons
                        if x > screen_width * 0.6 and y > screen_height * 0.7:
                            if any(icon in text_lower for icon in ['→', '➤', '▶', '>', 'arrow', 'plane', 'send']):
                                print(f"✅ Found send button via icon: '{element['text']}' at ({x}, {y})")
                                success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
                                if success:
                                    send_button_found = True
                                    print(f"✅ Send button tapped successfully")
                                    break
                                else:
                                    print(f"⚠️ Icon tap failed, trying next: {stderr}")
                    except Exception as e:
                        print(f"⚠️ Error processing icon element: {e}")
                        continue
            
            # Method 3: Look for green send button (#00FF00)
            if not send_button_found:
                print("🟢 Looking for green send button (#00FF00)...")
                green_button_coords = self.find_green_send_button()
                if green_button_coords:
                    x, y = green_button_coords
                    success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
                    if success:
                        print(f"✅ Green send button tapped at ({x}, {y})")
                        send_button_found = True
                    else:
                        print(f"❌ Failed to tap green button: {stderr}")
            
            # Method 4: Improved send button detection using text analysis
            if not send_button_found:
                print("🔍 Advanced send button detection...")
                
                # Look for any elements that might be send-related
                send_candidates = []
                for element in self.detected_elements:
                    try:
                        if 'coordinates' not in element:
                            continue
                        x, y = element['coordinates']
                        text = element['text'].lower()
                        screen_height = self.current_screenshot.size[1]
                        
                        # Check if element is in bottom area and could be send button
                        if y > screen_height * 0.7:  # Bottom 30% of screen
                            # Look for send indicators (including icons, arrows, etc.)
                            if any(indicator in text for indicator in ['send', '>', '→', '▶', 'submit', 'ok']):
                                send_candidates.append((x, y, element['text'], 'text_match'))
                            # Also consider very small/minimal text that could be icons
                            elif len(text.strip()) <= 2 and text.strip() != '':
                                send_candidates.append((x, y, element['text'], 'possible_icon'))
                    except Exception as e:
                        print(f"⚠️ Error processing element: {e}")
                        continue
                
                # Sort candidates by position (rightmost in bottom area preferred)
                if send_candidates:
                    send_candidates.sort(key=lambda c: (c[1], c[0]), reverse=True)  # Bottom-most, then rightmost
                    
                    for candidate in send_candidates[:3]:  # Try top 3 candidates
                        x, y, text, reason = candidate
                        print(f"🎯 Trying send candidate: '{text}' at ({x}, {y}) - {reason}")
                        
                        success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
                        if success:
                            print(f"✅ Send button tapped at ({x}, {y})")
                            send_button_found = True
                            break
                        else:
                            print(f"❌ Tap failed: {stderr}")
            
            # Method 5: More precise positional fallback (avoid backspace area)
            if not send_button_found:
                print("🔄 Using precise positional fallback...")
                screen_width = 1080
                screen_height = 2340
                
                # Try multiple positions in the send button area (avoid far right where backspace might be)
                send_positions = [
                    (int(screen_width * 0.85), int(screen_height * 0.88)),  # Slightly left and up from previous
                    (int(screen_width * 0.82), int(screen_height * 0.90)),  # More to the left
                    (int(screen_width * 0.88), int(screen_height * 0.85)),  # Higher up
                ]
                
                for i, (send_x, send_y) in enumerate(send_positions):
                    print(f"   🎯 Trying position {i+1}: ({send_x}, {send_y})")
                    success, _, stderr = self.run_adb_command(f"shell input tap {send_x} {send_y}")
                    if success:
                        print(f"✅ Fallback send tap executed at ({send_x}, {send_y})")
                        send_button_found = True
                        break
                    else:
                        print(f"❌ Position {i+1} failed: {stderr}")
                        await asyncio.sleep(0.5)  # Brief pause between attempts
            
            if not send_button_found:
                print("❌ Could not find or tap send button")
            
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
        """Direct WhatsApp message sending without menu"""
        print("\n🤖 AI MOBILE AGENTX - DIRECT WHATSAPP AUTOMATION")
        print("=" * 50)
        
        if not self.check_device_connection():
            return
        
        try:
            contact = input("👤 Contact name: ").strip()
            message = input("💬 Message: ").strip()
            
            if contact and message:
                await self.whatsapp_send_message(contact, message)
            else:
                print("❌ Contact name and message required")
                
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