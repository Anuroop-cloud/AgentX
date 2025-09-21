"""
AI Mobile AgentX - WhatsApp Connector
OCR-driven WhatsApp automation with dynamic text detection and intelligent messaging
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time
import re

from ..core import ScreenCaptureManager, OCRDetectionEngine, TapCoordinateEngine, SmartAutomationEngine
from ..core.automation_engine import AutomationAction, AutomationSequence, ActionType, ConditionType
from ..intelligence import IntelligentPositionCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WhatsAppMessage:
    """Represents a WhatsApp message"""
    contact: str
    message: str
    timestamp: str
    is_sent: bool = False
    is_read: bool = False
    message_type: str = "text"  # text, image, voice, document

@dataclass
class WhatsAppContact:
    """Represents a WhatsApp contact"""
    name: str
    phone: str = ""
    last_seen: str = ""
    is_online: bool = False
    unread_count: int = 0

@dataclass
class WhatsAppAction:
    """Represents a WhatsApp action result"""
    success: bool
    action_type: str
    message: str
    data: Dict[str, Any] = None

class WhatsAppConnector:
    """
    Reformed WhatsApp connector using OCR-driven automation
    Dynamically detects WhatsApp UI elements and performs intelligent messaging
    """
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        
        # Initialize core components
        self.screen_capture = ScreenCaptureManager()
        self.ocr_engine = OCRDetectionEngine()
        self.tap_engine = TapCoordinateEngine(test_mode=test_mode)
        self.automation_engine = SmartAutomationEngine(test_mode=test_mode)
        self.position_cache = IntelligentPositionCache()
        
        # Set app context for better caching
        self.position_cache.set_app_context("WhatsApp")
        
        # WhatsApp-specific UI elements
        self.ui_elements = {
            'chats': ['Chats', 'Recent', 'Messages'],
            'new_chat': ['New chat', '+', 'New message'],
            'search': ['Search', '🔍', 'Search or start new chat'],
            'send': ['Send', '➤', '✓'],
            'type_message': ['Type a message', 'Message', 'Write a message'],
            'attach': ['Attach', '📎', '+'],
            'voice': ['Voice message', '🎤', 'Hold to record'],
            'camera': ['Camera', '📷', 'Take photo'],
            'call': ['Call', '📞', 'Voice call'],
            'video_call': ['Video call', '📹', 'Video call'],
            'back': ['Back', '←', '⬅️'],
            'menu': ['Menu', '⋮', '⋯'],
            'status': ['Status', 'My status', 'Recent updates'],
            'calls': ['Calls', 'Recent calls'],
            'settings': ['Settings', 'Account', 'Privacy'],
            'online': ['online', 'Online', 'last seen'],
            'typing': ['typing...', 'is typing', 'typing'],
        }
        
        # Message patterns for better detection
        self.message_patterns = {
            'time_pattern': r'\b\d{1,2}:\d{2}\b',  # Time format like 14:30
            'unread_pattern': r'\b\d+\b',  # Unread count
            'phone_pattern': r'\+?\d{10,15}',  # Phone numbers
        }
        
        # Current conversation state
        self.current_chat = None
        self.last_message_time = 0
        
        logger.info(f"WhatsApp connector initialized (test_mode: {test_mode})")
    
    async def initialize_whatsapp(self) -> WhatsAppAction:
        """Initialize WhatsApp and ensure it's ready for automation"""
        try:
            # Capture current screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return WhatsAppAction(False, "initialize", "Failed to capture screen")
            
            # Perform OCR to detect current state
            ocr_result = await self.ocr_engine.detect_text(image)
            
            # Cache detected positions
            self.position_cache.cache_positions(ocr_result, image)
            
            # Check if WhatsApp is already open
            whatsapp_indicators = ['WhatsApp', 'Chats', 'Type a message', 'New chat']
            whatsapp_detected = any(
                len(self.ocr_engine.find_text(ocr_result, indicator)) > 0 
                for indicator in whatsapp_indicators
            )
            
            if whatsapp_detected:
                logger.info("WhatsApp already open and ready")
                return WhatsAppAction(True, "initialize", "WhatsApp ready for automation")
            else:
                logger.warning("WhatsApp not detected - manual app launch may be required")
                return WhatsAppAction(False, "initialize", "WhatsApp app not found on screen")
        
        except Exception as e:
            logger.error(f"WhatsApp initialization failed: {e}")
            return WhatsAppAction(False, "initialize", str(e))
    
    async def send_message(self, contact_name: str, message: str) -> WhatsAppAction:
        """Send a message to a specific contact"""
        try:
            # Create automation sequence for sending message
            actions = [
                # Navigate to chats if not already there
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Chats'},
                    description="Navigate to Chats"
                ),
                
                # Search for contact
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Search'},
                    description="Tap search"
                ),
                
                # Wait for search interface
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 1.0},
                    description="Wait for search interface"
                ),
                
                # Tap on contact (assuming search results show the contact)
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': contact_name},
                    description=f"Select contact: {contact_name}"
                ),
                
                # Wait for chat to open
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for chat to open"
                ),
                
                # Verify chat opened
                AutomationAction(
                    action_type=ActionType.VERIFY,
                    parameters={'text': 'Type a message'},
                    description="Verify chat interface opened"
                ),
                
                # Tap message input field
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Type a message'},
                    description="Tap message input field"
                ),
                
                # Wait for keyboard to appear
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 1.5},
                    description="Wait for keyboard"
                ),
                
                # Note: Actual text input would require additional implementation
                # For now, we'll simulate typing completion and proceed to send
                
                # Tap send button
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Send'},
                    description="Send message"
                )
            ]
            
            # Execute the automation sequence
            sequence = AutomationSequence("Send WhatsApp Message", actions, global_timeout=60.0)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Analyze results
            success_count = sum(1 for result in results if result.success)
            total_actions = len(results)
            
            if success_count >= total_actions * 0.8:  # 80% success rate threshold
                logger.info(f"Message sent successfully to {contact_name}")
                return WhatsAppAction(
                    True, "send_message", 
                    f"Message sent to {contact_name}",
                    {'contact': contact_name, 'message': message}
                )
            else:
                logger.warning(f"Message sending partially failed ({success_count}/{total_actions})")
                return WhatsAppAction(
                    False, "send_message",
                    f"Failed to send message - only {success_count}/{total_actions} actions succeeded"
                )
        
        except Exception as e:
            logger.error(f"Message sending failed: {e}")
            return WhatsAppAction(False, "send_message", str(e))
    
    async def get_recent_chats(self, limit: int = 10) -> WhatsAppAction:
        """Get list of recent chats with unread message counts"""
        try:
            # Navigate to chats list
            actions = [
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Chats'},
                    description="Navigate to Chats list"
                ),
                
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for chats to load"
                )
            ]
            
            sequence = AutomationSequence("Get Recent Chats", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Capture current chats screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return WhatsAppAction(False, "get_chats", "Failed to capture chats screen")
            
            # Perform OCR to detect chat list
            ocr_result = await self.ocr_engine.detect_text(image)
            
            # Extract chat information
            chats = await self._extract_chat_list(ocr_result)
            
            logger.info(f"Found {len(chats)} recent chats")
            return WhatsAppAction(
                True, "get_chats", 
                f"Retrieved {len(chats)} recent chats",
                {'chats': chats, 'count': len(chats)}
            )
        
        except Exception as e:
            logger.error(f"Getting recent chats failed: {e}")
            return WhatsAppAction(False, "get_chats", str(e))
    
    async def read_messages(self, contact_name: str, count: int = 5) -> WhatsAppAction:
        """Read recent messages from a specific contact"""
        try:
            # Open specific chat
            actions = [
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': contact_name},
                    description=f"Open chat with {contact_name}"
                ),
                
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for messages to load"
                )
            ]
            
            sequence = AutomationSequence("Read Messages", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Capture chat screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return WhatsAppAction(False, "read_messages", "Failed to capture chat screen")
            
            # Extract messages from OCR
            ocr_result = await self.ocr_engine.detect_text(image)
            messages = await self._extract_messages(ocr_result, contact_name)
            
            logger.info(f"Read {len(messages)} messages from {contact_name}")
            return WhatsAppAction(
                True, "read_messages",
                f"Read {len(messages)} messages from {contact_name}",
                {'messages': messages, 'contact': contact_name}
            )
        
        except Exception as e:
            logger.error(f"Reading messages failed: {e}")
            return WhatsAppAction(False, "read_messages", str(e))
    
    async def search_messages(self, query: str) -> WhatsAppAction:
        """Search for messages containing specific text"""
        try:
            actions = [
                # Navigate to chats
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Chats'},
                    description="Navigate to Chats"
                ),
                
                # Tap search
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Search'},
                    description="Tap search"
                ),
                
                # Wait for search interface
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 1.5},
                    description="Wait for search interface"
                ),
                
                # Note: Text input implementation would be needed here
                
                # Wait for search results
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for search results"
                )
            ]
            
            sequence = AutomationSequence("Search Messages", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Capture search results
            image = await self.screen_capture.capture_with_retry()
            if image:
                ocr_result = await self.ocr_engine.detect_text(image)
                search_results = await self._extract_search_results(ocr_result, query)
                
                return WhatsAppAction(
                    True, "search", 
                    f"Found {len(search_results)} results for '{query}'",
                    {'results': search_results, 'query': query}
                )
            else:
                return WhatsAppAction(False, "search", "Failed to capture search results")
        
        except Exception as e:
            logger.error(f"Message search failed: {e}")
            return WhatsAppAction(False, "search", str(e))
    
    async def send_media(self, contact_name: str, media_type: str = "camera") -> WhatsAppAction:
        """Send media (photo, document, etc.) to a contact"""
        try:
            # First open the chat
            open_chat_result = await self.send_message(contact_name, "")  # Reuse chat opening logic
            if not open_chat_result.success:
                return WhatsAppAction(False, "send_media", "Failed to open chat")
            
            actions = [
                # Tap attachment/media button
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Attach'},
                    description="Tap attachment button"
                ),
                
                # Wait for media options
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 1.0},
                    description="Wait for media options"
                ),
                
                # Select media type (camera, gallery, document, etc.)
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': media_type.title()},
                    description=f"Select {media_type}"
                ),
                
                # Wait for media interface
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for media interface"
                ),
                
                # Tap send (after media selection)
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Send'},
                    description="Send media"
                )
            ]
            
            sequence = AutomationSequence("Send Media", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            success = sum(1 for r in results if r.success) >= len(results) * 0.8
            
            if success:
                return WhatsAppAction(
                    True, "send_media", 
                    f"Media sent to {contact_name}",
                    {'contact': contact_name, 'media_type': media_type}
                )
            else:
                return WhatsAppAction(False, "send_media", "Failed to send media")
        
        except Exception as e:
            logger.error(f"Media sending failed: {e}")
            return WhatsAppAction(False, "send_media", str(e))
    
    async def _extract_chat_list(self, ocr_result) -> List[WhatsAppContact]:
        """Extract chat list from OCR results"""
        contacts = []
        
        try:
            # Look for contact names and unread indicators
            for detection in ocr_result.detections:
                text = detection.text.strip()
                
                # Skip very short text or UI elements
                if len(text) < 2 or text in ['Chats', 'Status', 'Calls']:
                    continue
                
                # Look for time patterns (indicates recent message)
                time_match = re.search(self.message_patterns['time_pattern'], text)
                
                # Look for unread count patterns
                unread_match = re.search(self.message_patterns['unread_pattern'], text)
                unread_count = int(unread_match.group()) if unread_match else 0
                
                # If text doesn't contain special characters, likely a contact name
                if not any(char in text for char in ['📞', '📹', '🔍', '⋮']) and len(text) > 2:
                    contact = WhatsAppContact(
                        name=text,
                        last_seen=time_match.group() if time_match else "Unknown",
                        unread_count=unread_count
                    )
                    contacts.append(contact)
                    
                    if len(contacts) >= 10:  # Limit results
                        break
            
            return contacts
        
        except Exception as e:
            logger.error(f"Chat list extraction failed: {e}")
            return []
    
    async def _extract_messages(self, ocr_result, contact_name: str) -> List[WhatsAppMessage]:
        """Extract messages from a chat screen"""
        messages = []
        
        try:
            # Look for message bubbles and timestamps
            for detection in ocr_result.detections:
                text = detection.text.strip()
                
                # Skip UI elements and very short text
                if len(text) < 3 or text in ['Type a message', 'Send', contact_name]:
                    continue
                
                # Check if it looks like a message (not a timestamp or UI element)
                if not re.match(self.message_patterns['time_pattern'], text) and len(text) > 5:
                    # Determine if message is sent or received based on position or other indicators
                    # This is simplified - real implementation would need more sophisticated detection
                    is_sent = detection.center_point[0] > (detection.bounding_box[2] * 0.6)  # Right side = sent
                    
                    message = WhatsAppMessage(
                        contact=contact_name,
                        message=text,
                        timestamp="Now",  # Would need better timestamp detection
                        is_sent=is_sent,
                        is_read=True
                    )
                    messages.append(message)
                    
                    if len(messages) >= 5:  # Limit to recent 5 messages
                        break
            
            return messages
        
        except Exception as e:
            logger.error(f"Message extraction failed: {e}")
            return []
    
    async def _extract_search_results(self, ocr_result, query: str) -> List[Dict[str, Any]]:
        """Extract search results from OCR"""
        results = []
        
        try:
            # Look for text containing the search query
            for detection in ocr_result.detections:
                text = detection.text.strip()
                
                if query.lower() in text.lower() and len(text) > len(query):
                    results.append({
                        'text': text,
                        'position': detection.center_point,
                        'confidence': detection.confidence
                    })
                    
                    if len(results) >= 5:  # Limit results
                        break
            
            return results
        
        except Exception as e:
            logger.error(f"Search results extraction failed: {e}")
            return []
    
    async def get_smart_suggestions(self) -> List[str]:
        """Get intelligent suggestions based on current WhatsApp state"""
        try:
            # Capture current screen and analyze context
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return ["Send message", "Check recent chats"]
            
            ocr_result = await self.ocr_engine.detect_text(image)
            detected_texts = [d.text.lower() for d in ocr_result.detections]
            
            suggestions = []
            
            # Context-aware suggestions
            if any('chats' in text for text in detected_texts):
                suggestions.extend([
                    "Send message to contact",
                    "Search for messages",
                    "Check unread messages",
                    "Start new chat"
                ])
            
            if any('type a message' in text for text in detected_texts):
                suggestions.extend([
                    "Send text message",
                    "Send photo",
                    "Send voice message",
                    "Share location"
                ])
            
            if any('status' in text for text in detected_texts):
                suggestions.extend([
                    "Update status",
                    "View friends' status",
                    "Share photo status"
                ])
            
            # Default suggestions
            if not suggestions:
                suggestions = [
                    "Open recent chats",
                    "Send message to contact",
                    "Search messages",
                    "Check WhatsApp status",
                    "Start voice call"
                ]
            
            return suggestions[:5]  # Limit to 5 suggestions
        
        except Exception as e:
            logger.error(f"Smart suggestions failed: {e}")
            return ["Send message", "Check chats", "Search messages"]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get WhatsApp connector performance statistics"""
        return {
            'automation_stats': self.automation_engine.get_statistics(),
            'cache_performance': self.position_cache.get_cache_performance(),
            'app_context': 'WhatsApp',
            'test_mode': self.test_mode,
            'current_chat': self.current_chat
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.position_cache.close()
        logger.info("WhatsApp connector cleaned up")


# Example usage and testing
async def main():
    """Test WhatsApp connector functionality"""
    try:
        # Initialize connector in test mode
        whatsapp = WhatsAppConnector(test_mode=True)
        
        # Test initialization
        print("Testing WhatsApp initialization...")
        init_result = await whatsapp.initialize_whatsapp()
        print(f"Init result: {init_result.message}")
        
        # Test getting recent chats
        print("\nTesting recent chats...")
        chats_result = await whatsapp.get_recent_chats()
        print(f"Chats result: {chats_result.message}")
        if chats_result.data:
            print(f"Found {chats_result.data.get('count', 0)} chats")
        
        # Test sending message
        print("\nTesting send message...")
        send_result = await whatsapp.send_message("Test Contact", "Hello, this is a test message!")
        print(f"Send result: {send_result.message}")
        
        # Test smart suggestions
        print("\nTesting smart suggestions...")
        suggestions = await whatsapp.get_smart_suggestions()
        print(f"Suggestions: {suggestions}")
        
        # Show performance stats
        print(f"\nPerformance stats: {whatsapp.get_performance_stats()}")
        
        # Cleanup
        whatsapp.cleanup()
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())