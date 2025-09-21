"""
Debug Mobile AgentX - OCR + AI Message Summarization
Finds app → Search → Contact → Summarize message → Send
"""

import subprocess
import asyncio
import os
import time
from PIL import Image
from datetime import datetime
import numpy as np
import json

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("❌ EasyOCR not available - install with: pip install easyocr")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ Gemini not available - install with: pip install google-generativeai")

class DebugMobileAgentX:
    def __init__(self):
        self.adb_path = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
        self.device_connected = False
        self.current_screenshot = None
        self.detected_elements = []
        self.gemini_model = None
        
        print("🐛 DEBUG MOBILE AGENTX")
        print("OCR App Detection + AI Message Summarization")
        print("=" * 50)
        
        # Initialize OCR
        if EASYOCR_AVAILABLE:
            print("🔄 Initializing OCR...")
            self.ocr_reader = easyocr.Reader(['en'])
            print("✅ OCR ready")
        else:
            print("❌ OCR failed - exiting")
            exit(1)
        
        # Initialize Gemini
        if GEMINI_AVAILABLE:
            print("🔄 Initializing Gemini...")
            try:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                    print("✅ Gemini ready")
                else:
                    print("⚠️ GEMINI_API_KEY not found")
                    self.gemini_model = None
            except Exception as e:
                print(f"⚠️ Gemini error: {e}")
                self.gemini_model = None
        else:
            print("⚠️ Gemini not available")
            self.gemini_model = None
    
    def run_adb_command(self, command):
        """Execute ADB command"""
        try:
            full_command = [self.adb_path] + command.split()
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def check_device_connection(self):
        """Check device connection"""
        print("📱 Checking device...")
        success, stdout, stderr = self.run_adb_command("devices")
        
        if not success:
            print(f"❌ ADB error: {stderr}")
            return False
        
        lines = stdout.strip().split('\n')[1:]
        connected_devices = [line for line in lines if line.strip() and 'device' in line]
        
        if not connected_devices:
            print("❌ No device connected")
            return False
        
        device_id = connected_devices[0].split()[0]
        print(f"✅ Device: {device_id}")
        self.device_connected = True
        return True
    
    def capture_screen(self):
        """Capture screen"""
        if not self.device_connected:
            return None
        
        print("📸 Capturing screen...")
        temp_path = "/sdcard/debug_screenshot.png"
        
        # Take screenshot
        success, _, _ = self.run_adb_command(f"shell screencap -p {temp_path}")
        if not success:
            print("❌ Screenshot failed")
            return None
        
        # Pull to local
        local_temp = f"debug_screenshot_{datetime.now().strftime('%H%M%S')}.png"
        success, _, _ = self.run_adb_command(f"pull {temp_path} {local_temp}")
        if not success:
            print("❌ Pull failed")
            return None
        
        try:
            if os.path.exists(local_temp):
                image = Image.open(local_temp)
                self.current_screenshot = image.copy()
                image.close()
                
                # Cleanup
                os.remove(local_temp)
                self.run_adb_command(f"shell rm {temp_path}")
                
                print(f"✅ Screenshot captured: {self.current_screenshot.size}")
                return self.current_screenshot
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            
        return None
    
    def detect_text_with_ocr(self):
        """Detect text using OCR"""
        if not self.current_screenshot:
            print("❌ No screenshot to analyze")
            return []
        
        print("🔍 OCR analyzing...")
        
        try:
            image_array = np.array(self.current_screenshot)
            
            # Try both paragraph and word detection
            results = []
            
            try:
                # Paragraph detection for app names
                para_results = self.ocr_reader.readtext(image_array, paragraph=True)
                results.extend(para_results)
            except:
                pass
            
            try:
                # Word detection for individual elements
                word_results = self.ocr_reader.readtext(image_array, paragraph=False)
                results.extend(word_results)
            except:
                pass
            
            elements = []
            seen_positions = set()
            
            for item in results:
                try:
                    if len(item) >= 3:
                        bbox, text, confidence = item[0], item[1], item[2]
                    else:
                        continue
                    
                    if confidence > 0.4 and text.strip() and len(text.strip()) > 1:
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]
                        x1, y1 = int(min(x_coords)), int(min(y_coords))
                        x2, y2 = int(max(x_coords)), int(max(y_coords))
                        
                        center = ((x1 + x2) // 2, (y1 + y2) // 2)
                        
                        # Avoid duplicates
                        position_key = (center[0] // 30, center[1] // 30)
                        if position_key in seen_positions:
                            continue
                        seen_positions.add(position_key)
                        
                        elements.append({
                            'text': text.strip(),
                            'bbox': (x1, y1, x2, y2),
                            'center': center,
                            'confidence': confidence,
                            'area': (x2 - x1) * (y2 - y1)
                        })
                except:
                    continue
            
            # Sort by confidence and area
            self.detected_elements = sorted(elements, key=lambda x: (x['confidence'], x['area']), reverse=True)
            print(f"✅ OCR found {len(self.detected_elements)} text elements")
            
            # Debug: Show top elements
            for i, elem in enumerate(self.detected_elements[:5]):
                print(f"   {i+1}. '{elem['text']}' (conf: {elem['confidence']:.2f}, area: {elem['area']})")
            
            return self.detected_elements
            
        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return []
    
    def find_app_by_name(self, app_name):
        """Find app using OCR"""
        app_keywords = {
            'whatsapp': ['whatsapp', 'whats app', 'whats', 'wa'],
            'messages': ['messages', 'message', 'sms'],
            'gmail': ['gmail', 'mail', 'email'],
            'phone': ['phone', 'dialer', 'call']
        }
        
        app_name_lower = app_name.lower()
        search_terms = app_keywords.get(app_name_lower, [app_name_lower])
        
        print(f"🔍 Looking for {app_name}...")
        print(f"   Search terms: {search_terms}")
        
        if not self.capture_screen():
            return None
        
        elements = self.detect_text_with_ocr()
        
        # Find matches
        matches = []
        for element in elements:
            text_lower = element['text'].lower()
            
            for term in search_terms:
                if term in text_lower or text_lower in term:
                    score = (len(term) / len(text_lower)) * element['confidence'] * min(element['area'] / 1000, 2)
                    element['match_score'] = score
                    matches.append(element)
                    break
        
        if matches:
            best = max(matches, key=lambda x: x['match_score'])
            print(f"✅ Found {app_name}: '{best['text']}' at {best['center']}")
            return best
        
        print(f"❌ {app_name} not found")
        return None
    
    def find_text_element(self, target_text, min_area=500):
        """Find text element on current screen with flexible matching"""
        if not self.detected_elements:
            self.detect_text_with_ocr()
        
        target_lower = target_text.lower()
        matches = []
        
        print(f"🔍 Looking for '{target_text}' (min_area: {min_area})...")
        
        # Show what we have to work with
        print(f"   Available texts: {[elem['text'] for elem in self.detected_elements[:10]]}")
        
        for element in self.detected_elements:
            text_lower = element['text'].lower()
            
            # More flexible matching
            match_found = False
            match_type = ""
            
            # Exact match
            if target_lower == text_lower:
                match_found = True
                match_type = "exact"
            # Contains match
            elif target_lower in text_lower:
                match_found = True
                match_type = "contains"
            # Reverse contains
            elif text_lower in target_lower and len(text_lower) > 2:
                match_found = True
                match_type = "partial"
            # Fuzzy match for common OCR errors
            elif len(target_lower) > 3 and len(text_lower) > 3:
                common_chars = set(target_lower) & set(text_lower)
                if len(common_chars) >= min(3, len(target_lower) * 0.6):
                    match_found = True
                    match_type = "fuzzy"
            
            if match_found:
                # Score based on match type, confidence, and area
                type_multiplier = {'exact': 2.0, 'contains': 1.5, 'partial': 1.2, 'fuzzy': 0.8}
                area_score = max(1, element['area'] / 1000)
                score = element['confidence'] * area_score * type_multiplier.get(match_type, 1.0)
                
                # Bonus for reasonable size
                if element['area'] >= min_area:
                    score *= 1.5
                
                element['search_score'] = score
                element['match_type'] = match_type
                matches.append(element)
                
                print(f"   Match: '{element['text']}' ({match_type}, area: {element['area']}, score: {score:.1f})")
        
        if matches:
            # Sort by score
            matches.sort(key=lambda x: x['search_score'], reverse=True)
            best = matches[0]
            print(f"✅ Best match: '{best['text']}' ({best['match_type']}) at {best['center']}")
            return best
        
        print(f"❌ '{target_text}' not found")
        return None
    
    def tap_element(self, element):
        """Tap on element"""
        x, y = element['center']
        print(f"👆 Tapping '{element['text']}' at ({x}, {y})")
        
        success, _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        if success:
            print("✅ Tap executed")
            return True
        else:
            print(f"❌ Tap failed: {stderr}")
            return False
    
    def type_text(self, text):
        """Type text"""
        # Escape special characters for shell
        escaped_text = text.replace(' ', '%s').replace('"', '\\"').replace("'", "\\'")
        print(f"⌨️ Typing: {text}")
        
        success, _, stderr = self.run_adb_command(f"shell input text \"{escaped_text}\"")
        if success:
            print("✅ Text typed")
            return True
        else:
            print(f"❌ Text input failed: {stderr}")
            return False
    
    def press_enter(self):
        """Press enter key"""
        print("⏎ Pressing Enter")
        success, _, _ = self.run_adb_command("shell input keyevent 66")
        return success
    
    def find_contact_in_results(self, contact_name):
        """Find contact in search results with smart filtering"""
        if not self.detected_elements:
            self.detect_text_with_ocr()
        
        contact_lower = contact_name.lower()
        screen_height = self.current_screenshot.height if self.current_screenshot else 2400
        search_bar_threshold = screen_height * 0.15  # Top 15% is search bar area
        
        print(f"🔍 Smart contact search for '{contact_name}'")
        print(f"   Screen height: {screen_height}, Search bar threshold: {search_bar_threshold}")
        
        # Separate matches by type
        exact_matches = []
        partial_matches = []
        fuzzy_matches = []
        
        for element in self.detected_elements:
            text_lower = element['text'].lower()
            y_pos = element['center'][1]
            
            # Skip search bar area (top 15% of screen)
            if y_pos < search_bar_threshold:
                print(f"   Skipping search bar area: '{element['text']}' at y={y_pos}")
                continue
            
            # Skip elements that are clearly not contacts
            avoid_keywords = ['search', 'file manager', 'manager', 'browser', 'settings', 'menu', 'back', 'home']
            if any(keyword in text_lower for keyword in avoid_keywords):
                print(f"   Skipping non-contact element: '{element['text']}'")
                continue
            
            # Minimum area for contact entries (avoid tiny text)
            if element['area'] < 800:
                print(f"   Skipping small element: '{element['text']}' (area: {element['area']})")
                continue
            
            # Classify matches
            if contact_lower == text_lower:
                # Exact match - highest priority
                element['match_score'] = 100.0
                element['match_type'] = 'exact'
                exact_matches.append(element)
                print(f"   ✅ EXACT match: '{element['text']}' at {element['center']}")
            
            elif contact_lower in text_lower or text_lower in contact_lower:
                # Partial match - medium priority
                overlap = len(contact_lower) if contact_lower in text_lower else len(text_lower)
                score = (overlap / max(len(contact_lower), len(text_lower))) * 50
                element['match_score'] = score * element['confidence']
                element['match_type'] = 'partial'
                partial_matches.append(element)
                print(f"   🔶 PARTIAL match: '{element['text']}' (score: {element['match_score']:.1f})")
            
            elif len(contact_lower) > 3 and len(text_lower) > 3:
                # Fuzzy match - lowest priority
                common_chars = set(contact_lower) & set(text_lower)
                if len(common_chars) >= min(3, len(contact_lower) * 0.5):
                    score = (len(common_chars) / max(len(contact_lower), len(text_lower))) * 25
                    element['match_score'] = score * element['confidence']
                    element['match_type'] = 'fuzzy'
                    fuzzy_matches.append(element)
                    print(f"   🔸 FUZZY match: '{element['text']}' (score: {element['match_score']:.1f})")
        
        # Return best match with priority: exact > partial > fuzzy
        all_candidates = []
        
        if exact_matches:
            print(f"✅ Found {len(exact_matches)} exact matches")
            all_candidates.extend(sorted(exact_matches, key=lambda x: x['match_score'], reverse=True))
        
        if partial_matches:
            print(f"🔶 Found {len(partial_matches)} partial matches")
            all_candidates.extend(sorted(partial_matches, key=lambda x: x['match_score'], reverse=True))
        
        if fuzzy_matches:
            print(f"🔸 Found {len(fuzzy_matches)} fuzzy matches")
            all_candidates.extend(sorted(fuzzy_matches, key=lambda x: x['match_score'], reverse=True))
        
        if all_candidates:
            best = all_candidates[0]
            print(f"🎯 Best candidate: '{best['text']}' ({best['match_type']}) at {best['center']}")
            
            # Store alternatives for retry
            best['alternatives'] = all_candidates[1:4]  # Keep top 3 alternatives
            return best
        
        print(f"❌ No suitable contact matches found")
        return None
    
    async def tap_contact_with_retry(self, contact_name, primary_contact, max_retries=3):
        """Tap contact with retry mechanism if first tap fails"""
        candidates = [primary_contact] + primary_contact.get('alternatives', [])
        
        for attempt, candidate in enumerate(candidates[:max_retries], 1):
            print(f"\n👆 Attempt {attempt}: Tapping '{candidate['text']}' at {candidate['center']}")
            
            if not self.tap_element(candidate):
                continue
            
            await asyncio.sleep(3)  # Wait for screen to change
            
            # Verify we're in a chat screen by checking for chat indicators
            if self.capture_screen():
                chat_detected = self.verify_chat_screen(contact_name)
                if chat_detected:
                    print(f"✅ Successfully opened chat with {contact_name}")
                    return True
                else:
                    print(f"⚠️ Attempt {attempt} failed - not in chat screen")
                    if attempt < len(candidates):
                        print(f"🔄 Trying next candidate...")
                        # Go back to search results if needed
                        self.run_adb_command("shell input keyevent 4")  # Back button
                        await asyncio.sleep(2)
            else:
                print(f"❌ Could not capture screen after tap attempt {attempt}")
        
        print(f"❌ All {max_retries} attempts failed to open chat")
        return False
    
    def verify_chat_screen(self, contact_name):
        """Verify we're in a chat screen with the correct contact"""
        elements = self.detect_text_with_ocr()
        
        # Look for chat screen indicators
        chat_indicators = ['type a message', 'message', 'send', 'emoji', 'attach']
        contact_indicators = [contact_name.lower()]
        
        has_chat_ui = False
        has_contact_name = False
        
        for element in elements:
            text_lower = element['text'].lower()
            
            # Check for chat UI elements
            if any(indicator in text_lower for indicator in chat_indicators):
                has_chat_ui = True
                print(f"   Chat UI detected: '{element['text']}'")
            
            # Check for contact name in title area (top of screen)
            if (contact_name.lower() in text_lower and 
                element['center'][1] < self.current_screenshot.height * 0.2):
                has_contact_name = True
                print(f"   Contact name in title: '{element['text']}'")
        
        result = has_chat_ui or has_contact_name
        print(f"   Chat screen verification: {result} (UI: {has_chat_ui}, Name: {has_contact_name})")
        return result
    
    def summarize_message(self, message):
        """Summarize message using Gemini"""
        if not self.gemini_model:
            print("⚠️ AI not available, using original message")
            return message
        
        try:
            print("🤖 Summarizing message...")
            
            prompt = f"""
            Summarize this message to be clear, concise, and natural:
            
            Original: "{message}"
            
            Make it:
            - Clear and easy to understand
            - Concise (1-2 sentences max)
            - Natural and friendly tone
            - Keep the main meaning
            
            Return only the summarized message, no quotes or extra text.
            """
            
            response = self.gemini_model.generate_content(prompt)
            summary = response.text.strip().strip('"').strip("'")
            
            print(f"📝 Original: {message}")
            print(f"✨ Summary: {summary}")
            
            return summary
            
        except Exception as e:
            print(f"❌ Summarization failed: {e}")
            return message
    
    async def debug_whatsapp_workflow(self, contact_name, message):
        """Debug WhatsApp workflow step by step"""
        print(f"\n🐛 DEBUG WHATSAPP WORKFLOW")
        print(f"👤 Contact: {contact_name}")
        print(f"💬 Message: {message}")
        print("=" * 50)
        
        try:
            # Step 1: Summarize message first
            print("\n📝 STEP 1: Summarize Message")
            summarized_message = self.summarize_message(message)
            
            # Step 2: Find WhatsApp
            print(f"\n📱 STEP 2: Find WhatsApp App")
            whatsapp = self.find_app_by_name("whatsapp")
            if not whatsapp:
                print("❌ WhatsApp not found")
                return False
            
            # Step 3: Open WhatsApp
            print(f"\n👆 STEP 3: Open WhatsApp")
            if not self.tap_element(whatsapp):
                return False
            
            await asyncio.sleep(3)  # Wait for app to load
            
            # Step 4: Find Search
            print(f"\n🔍 STEP 4: Find Search")
            if not self.capture_screen():
                return False
            
            # Try multiple search approaches
            search_element = None
            
            # First try common search texts with lower area requirement
            search_terms = ["search", "new chat", "find", "chat", "contacts", "plus", "+"]
            for term in search_terms:
                print(f"🔍 Trying '{term}'...")
                search_element = self.find_text_element(term, min_area=500)
                if search_element:
                    break
            
            # If no text found, try tapping common search positions
            if not search_element:
                print("🔍 No search text found, trying common positions...")
                # Try common WhatsApp search positions (top-right area)
                common_positions = [
                    (950, 200),   # Top right
                    (900, 150),   # Search icon area
                    (1000, 180),  # Menu area
                    (540, 200),   # Center top
                ]
                
                for i, pos in enumerate(common_positions):
                    print(f"🎯 Trying position {i+1}: {pos}")
                    # Create a fake element for this position
                    search_element = {
                        'text': f'Position {i+1}',
                        'center': pos,
                        'confidence': 0.8,
                        'area': 1000
                    }
                    
                    # Test tap this position
                    if self.tap_element(search_element):
                        await asyncio.sleep(2)
                        # Check if search input appeared by capturing screen again
                        if self.capture_screen():
                            # Look for search input field or keyboard
                            keyboard_check = self.find_text_element("type", min_area=200)
                            search_check = self.find_text_element("search", min_area=200)
                            if keyboard_check or search_check:
                                print("✅ Search activated successfully!")
                                break
                    
                    search_element = None
            
            if not search_element:
                print("❌ Search not found - showing all detected elements")
                self.show_detected_elements()
                return False
            
            # Step 5: Tap Search
            print(f"\n👆 STEP 5: Activate Search")
            if not self.tap_element(search_element):
                return False
            
            await asyncio.sleep(2)
            
            # Step 6: Type Contact Name
            print(f"\n⌨️ STEP 6: Search for {contact_name}")
            if not self.type_text(contact_name):
                return False
            
            await asyncio.sleep(3)  # Wait for search results
            
            # Step 7: Find Contact in Results
            print(f"\n👤 STEP 7: Find Contact in Results")
            if not self.capture_screen():
                return False
            
            contact_element = self.find_contact_in_results(contact_name)
            if not contact_element:
                print(f"❌ Contact {contact_name} not found in results")
                return False
            
            # Step 8: Tap Contact with retry mechanism
            print(f"\n👆 STEP 8: Select Contact")
            success = await self.tap_contact_with_retry(contact_name, contact_element)
            if not success:
                return False
            
            # Step 9: Type Message
            print(f"\n💬 STEP 9: Type Summarized Message")
            if not self.type_text(summarized_message):
                return False
            
            await asyncio.sleep(1)
            
            # Step 10: Send Message
            print(f"\n📤 STEP 10: Send Message")
            if not self.press_enter():
                print("❌ Send failed")
                return False
            
            print(f"\n✅ SUCCESS!")
            print(f"   Contact: {contact_name}")
            print(f"   Original: {message}")
            print(f"   Sent: {summarized_message}")
            
            return True
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return False
    
    def show_detected_elements(self):
        """Show detected text for debugging"""
        if not self.capture_screen():
            return
        
        elements = self.detect_text_with_ocr()
        
        print(f"\n📋 DETECTED TEXT ELEMENTS:")
        print("=" * 60)
        print(f"Screen size: {self.current_screenshot.size}")
        print(f"Total elements: {len(elements)}")
        print("-" * 60)
        
        for i, elem in enumerate(elements[:25], 1):
            y_pos = elem['center'][1] 
            screen_section = "TOP" if y_pos < 400 else "MID" if y_pos < 1600 else "BOT"
            print(f"{i:2d}. '{elem['text']:<20}' | conf:{elem['confidence']:.2f} | area:{elem['area']:>4} | {screen_section} | {elem['center']}")
        
        # Group by screen sections
        print(f"\n📊 ELEMENTS BY SCREEN SECTION:")
        print("-" * 40)
        
        top_elements = [e for e in elements if e['center'][1] < 400]
        mid_elements = [e for e in elements if 400 <= e['center'][1] < 1600] 
        bot_elements = [e for e in elements if e['center'][1] >= 1600]
        
        print(f"TOP (0-400px): {len(top_elements)} elements")
        for elem in top_elements[:5]:
            print(f"  - '{elem['text']}' at {elem['center']}")
            
        print(f"MID (400-1600px): {len(mid_elements)} elements") 
        for elem in mid_elements[:5]:
            print(f"  - '{elem['text']}' at {elem['center']}")
            
        print(f"BOT (1600+px): {len(bot_elements)} elements")
        for elem in bot_elements[:5]:
            print(f"  - '{elem['text']}' at {elem['center']}")
    
    def analyze_whatsapp_screen(self):
        """Analyze current screen to understand WhatsApp state"""
        if not self.capture_screen():
            return None
            
        elements = self.detect_text_with_ocr()
        
        print(f"\n🔍 WHATSAPP SCREEN ANALYSIS:")
        print("=" * 40)
        
        # Check for WhatsApp indicators
        whatsapp_indicators = []
        search_indicators = []
        chat_indicators = []
        
        for elem in elements:
            text_lower = elem['text'].lower()
            
            if any(word in text_lower for word in ['whatsapp', 'chat', 'message']):
                whatsapp_indicators.append(elem)
            if any(word in text_lower for word in ['search', 'find', 'new', '+']):
                search_indicators.append(elem)
            if any(word in text_lower for word in ['type', 'message', 'send']):
                chat_indicators.append(elem)
        
        print(f"WhatsApp indicators: {len(whatsapp_indicators)}")
        for elem in whatsapp_indicators:
            print(f"  - '{elem['text']}' at {elem['center']}")
            
        print(f"Search indicators: {len(search_indicators)}")
        for elem in search_indicators:
            print(f"  - '{elem['text']}' at {elem['center']}")
            
        print(f"Chat indicators: {len(chat_indicators)}")
        for elem in chat_indicators:
            print(f"  - '{elem['text']}' at {elem['center']}")
        
        # Determine screen state
        if chat_indicators:
            return "CHAT_SCREEN"
        elif search_indicators:
            return "SEARCH_AVAILABLE"
        elif whatsapp_indicators:
            return "WHATSAPP_MAIN"
        else:
            return "UNKNOWN"
    
    async def interactive_debug(self):
        """Interactive debugging session"""
        print(f"\n🐛 DEBUG MOBILE AGENTX")
        print("=" * 30)
        
        if not self.check_device_connection():
            return
        
        while True:
            print(f"\n🎯 DEBUG OPTIONS")
            print("=" * 20)
            print("1. 💬 WhatsApp message (Full workflow)")
            print("2. 🔍 Find app")
            print("3. 📋 Show detected text")
            print("4. 🎨 Test message summarization")
            print("5. 📸 Capture screen")
            print("6. 🔍 Analyze WhatsApp screen state")
            print("7. 👤 Test contact finding")
            print("0. 🚪 Exit")
            
            choice = input("\n👉 Choice: ").strip()
            
            try:
                if choice == "0":
                    print("👋 Debug session ended")
                    break
                
                elif choice == "1":
                    contact = input("👤 Contact name: ").strip()
                    message = input("💬 Message: ").strip()
                    if contact and message:
                        await self.debug_whatsapp_workflow(contact, message)
                    else:
                        print("❌ Contact and message required")
                
                elif choice == "2":
                    app_name = input("📱 App name: ").strip()
                    if app_name:
                        result = self.find_app_by_name(app_name)
                        if result:
                            tap_choice = input("👆 Tap this app? (y/n): ").strip().lower()
                            if tap_choice == 'y':
                                self.tap_element(result)
                    else:
                        print("❌ App name required")
                
                elif choice == "3":
                    self.show_detected_elements()
                
                elif choice == "4":
                    test_message = input("💬 Message to summarize: ").strip()
                    if test_message:
                        summary = self.summarize_message(test_message)
                        print(f"Summary: {summary}")
                    else:
                        print("❌ Message required")
                
                elif choice == "5":
                    if self.capture_screen():
                        print("✅ Screen captured")
                    else:
                        print("❌ Capture failed")
                
                elif choice == "6":
                    screen_state = self.analyze_whatsapp_screen()
                    if screen_state:
                        print(f"📱 Screen state: {screen_state}")
                
                elif choice == "7":
                    contact_to_find = input("👤 Contact name to find: ").strip()
                    if contact_to_find:
                        if not self.capture_screen():
                            continue
                        contact = self.find_contact_in_results(contact_to_find)
                        if contact:
                            print(f"✅ Found contact: {contact}")
                            tap_choice = input("👆 Test tap with retry? (y/n): ").strip().lower()
                            if tap_choice == 'y':
                                success = await self.tap_contact_with_retry(contact_to_find, contact)
                                print(f"Result: {'✅ Success' if success else '❌ Failed'}")
                        else:
                            print(f"❌ Contact '{contact_to_find}' not found")
                    else:
                        print("❌ Contact name required")
                
                else:
                    print("❌ Invalid choice")
                
            except KeyboardInterrupt:
                print("\n⏸️ Action cancelled")
            except Exception as e:
                print(f"\n💥 Error: {e}")

async def main():
    """Main debug function"""
    try:
        agent = DebugMobileAgentX()
        await agent.interactive_debug() 
    except KeyboardInterrupt:
        print("\n👋 Debug ended by user")
    except Exception as e:
        print(f"\n💥 System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())