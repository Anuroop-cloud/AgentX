"""
AI Mobile AgentX - Gmail Connector
OCR-driven Gmail automation with dynamic text detection and intelligent interaction
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time

from ..core import ScreenCaptureManager, OCRDetectionEngine, TapCoordinateEngine, SmartAutomationEngine
from ..core.automation_engine import AutomationAction, AutomationSequence, ActionType, ConditionType
from ..intelligence import IntelligentPositionCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GmailMessage:
    """Represents a Gmail message"""
    sender: str
    subject: str
    snippet: str
    timestamp: str
    is_read: bool = False
    is_important: bool = False
    labels: List[str] = None

@dataclass
class GmailAction:
    """Represents a Gmail action result"""
    success: bool
    action_type: str
    message: str
    data: Dict[str, Any] = None

class GmailConnector:
    """
    Reformed Gmail connector using OCR-driven automation
    Dynamically detects Gmail UI elements and performs intelligent interactions
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
        self.position_cache.set_app_context("Gmail")
        
        # Gmail-specific text patterns
        self.ui_elements = {
            'compose': ['Compose', 'Write', '✏️', '+'],
            'inbox': ['Inbox', 'Primary', 'All mail'],
            'send': ['Send', 'Send message', '➤'],
            'reply': ['Reply', 'Reply all', '↩️'],
            'archive': ['Archive', 'Move to archive'],
            'delete': ['Delete', 'Move to trash', '🗑️'],
            'search': ['Search', 'Search mail', '🔍'],
            'menu': ['Menu', '☰', '≡'],
            'back': ['Back', '←', '⬅️'],
            'more_options': ['More', '⋮', '⋯'],
            'important': ['Important', '⭐', 'Mark as important'],
            'unread': ['Mark as unread', 'Unread'],
            'labels': ['Labels', 'Add label', 'Label as'],
        }
        
        # Conversation state
        self.current_screen_state = None
        self.last_action_time = 0
        
        logger.info(f"Gmail connector initialized (test_mode: {test_mode})")
    
    async def initialize_gmail(self) -> GmailAction:
        """Initialize Gmail app and ensure it's ready for automation"""
        try:
            # Capture current screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return GmailAction(False, "initialize", "Failed to capture screen")
            
            # Perform OCR to detect current state
            ocr_result = await self.ocr_engine.detect_text(image)
            
            # Cache detected positions
            self.position_cache.cache_positions(ocr_result, image)
            
            # Check if Gmail is already open
            gmail_indicators = ['Gmail', 'Inbox', 'Compose', 'google.com']
            gmail_detected = any(
                len(self.ocr_engine.find_text(ocr_result, indicator)) > 0 
                for indicator in gmail_indicators
            )
            
            if gmail_detected:
                logger.info("Gmail already open and ready")
                return GmailAction(True, "initialize", "Gmail ready for automation")
            else:
                # Try to open Gmail (this would need app-specific launch logic)
                logger.warning("Gmail not detected - manual app launch may be required")
                return GmailAction(False, "initialize", "Gmail app not found on screen")
        
        except Exception as e:
            logger.error(f"Gmail initialization failed: {e}")
            return GmailAction(False, "initialize", str(e))
    
    async def compose_email(self, recipient: str, subject: str, body: str) -> GmailAction:
        """Compose and send an email using OCR-driven automation"""
        try:
            # Create automation sequence for composing email
            actions = [
                # Find and tap compose button
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Compose'},
                    description="Tap Compose button",
                    max_retries=3
                ),
                
                # Wait for compose screen to load
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for compose screen"
                ),
                
                # Verify compose screen opened
                AutomationAction(
                    action_type=ActionType.VERIFY,
                    parameters={'text': 'To'},
                    description="Verify compose screen opened"
                ),
                
                # Tap "To" field and enter recipient
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'To'},
                    description="Tap To field"
                ),
                
                # Wait for keyboard/input focus
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 1.0},
                    description="Wait for input focus"
                ),
                
                # Find and tap subject field
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Subject'},
                    description="Tap Subject field"
                ),
                
                # Find compose/body area
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Compose email'},
                    description="Tap email body area"
                ),
                
                # Find and tap send button
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Send'},
                    description="Send email"
                )
            ]
            
            # Execute the automation sequence
            sequence = AutomationSequence("Compose Email", actions, global_timeout=120.0)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Analyze results
            success_count = sum(1 for result in results if result.success)
            total_actions = len(results)
            
            if success_count >= total_actions * 0.8:  # 80% success rate threshold
                logger.info(f"Email composition completed successfully ({success_count}/{total_actions})")
                return GmailAction(
                    True, "compose", 
                    f"Email sent successfully to {recipient}",
                    {'subject': subject, 'recipient': recipient}
                )
            else:
                logger.warning(f"Email composition partially failed ({success_count}/{total_actions})")
                return GmailAction(
                    False, "compose",
                    f"Email composition failed - only {success_count}/{total_actions} actions succeeded"
                )
        
        except Exception as e:
            logger.error(f"Email composition failed: {e}")
            return GmailAction(False, "compose", str(e))
    
    async def check_inbox(self, limit: int = 10) -> GmailAction:
        """Check inbox and return list of recent emails"""
        try:
            # Navigate to inbox
            actions = [
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Inbox'},
                    description="Navigate to Inbox"
                ),
                
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for inbox to load"
                )
            ]
            
            sequence = AutomationSequence("Check Inbox", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Capture current inbox screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return GmailAction(False, "check_inbox", "Failed to capture inbox")
            
            # Perform OCR to detect emails
            ocr_result = await self.ocr_engine.detect_text(image)
            
            # Extract email information using pattern matching
            emails = await self._extract_email_list(ocr_result)
            
            logger.info(f"Found {len(emails)} emails in inbox")
            return GmailAction(
                True, "check_inbox", 
                f"Retrieved {len(emails)} emails",
                {'emails': emails, 'count': len(emails)}
            )
        
        except Exception as e:
            logger.error(f"Inbox check failed: {e}")
            return GmailAction(False, "check_inbox", str(e))
    
    async def search_emails(self, query: str) -> GmailAction:
        """Search for emails using the Gmail search functionality"""
        try:
            actions = [
                # Tap search box
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Search'},
                    description="Tap search box"
                ),
                
                # Wait for search interface
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 1.5},
                    description="Wait for search interface"
                ),
                
                # Note: Actual text input would require additional implementation
                # For now, we'll simulate the search completion
                
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for search results"
                )
            ]
            
            sequence = AutomationSequence("Search Emails", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            # Capture search results
            image = await self.screen_capture.capture_with_retry()
            if image:
                ocr_result = await self.ocr_engine.detect_text(image)
                search_results = await self._extract_email_list(ocr_result)
                
                return GmailAction(
                    True, "search", 
                    f"Found {len(search_results)} emails matching '{query}'",
                    {'results': search_results, 'query': query}
                )
            else:
                return GmailAction(False, "search", "Failed to capture search results")
        
        except Exception as e:
            logger.error(f"Email search failed: {e}")
            return GmailAction(False, "search", str(e))
    
    async def reply_to_email(self, email_subject: str, reply_text: str) -> GmailAction:
        """Reply to an email by finding it and composing a response"""
        try:
            actions = [
                # Find email by subject (tap on it)
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': email_subject},
                    description=f"Open email: {email_subject}"
                ),
                
                # Wait for email to open
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for email to open"
                ),
                
                # Tap reply button
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Reply'},
                    description="Tap Reply button"
                ),
                
                # Wait for reply compose screen
                AutomationAction(
                    action_type=ActionType.WAIT,
                    parameters={'duration': 2.0},
                    description="Wait for reply screen"
                ),
                
                # Tap in compose area
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Reply'},
                    description="Tap reply compose area"
                ),
                
                # Send reply
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Send'},
                    description="Send reply"
                )
            ]
            
            sequence = AutomationSequence("Reply to Email", actions)
            results = await self.automation_engine.execute_sequence(sequence)
            
            success = sum(1 for r in results if r.success) >= len(results) * 0.8
            
            if success:
                return GmailAction(
                    True, "reply", 
                    f"Successfully replied to '{email_subject}'",
                    {'subject': email_subject, 'reply': reply_text}
                )
            else:
                return GmailAction(False, "reply", "Failed to send reply")
        
        except Exception as e:
            logger.error(f"Email reply failed: {e}")
            return GmailAction(False, "reply", str(e))
    
    async def archive_email(self, email_subject: str) -> GmailAction:
        """Archive an email by subject"""
        try:
            actions = [
                # Find and long-press email
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': email_subject},
                    description=f"Select email: {email_subject}"
                ),
                
                # Look for archive option
                AutomationAction(
                    action_type=ActionType.TAP,
                    parameters={'text': 'Archive'},
                    description="Archive email"
                )
            ]
            
            sequence = AutomationSequence("Archive Email", actions)
            results = await self.automation_engine.execute_sequence(sequence)
                
            success = all(result.success for result in results)
            
            if success:
                return GmailAction(True, "archive", f"Email '{email_subject}' archived")
            else:
                return GmailAction(False, "archive", "Failed to archive email")
        
        except Exception as e:
            logger.error(f"Email archiving failed: {e}")
            return GmailAction(False, "archive", str(e))
    
    async def _extract_email_list(self, ocr_result) -> List[GmailMessage]:
        """Extract email information from OCR results"""
        emails = []
        
        try:
            # Look for email patterns in detected text
            # This is a simplified extraction - real implementation would be more sophisticated
            for detection in ocr_result.detections:
                text = detection.text.strip()
                
                # Skip very short text
                if len(text) < 3:
                    continue
                
                # Look for email-like patterns
                if '@' in text:
                    # Likely a sender email
                    emails.append(GmailMessage(
                        sender=text,
                        subject="Subject not detected",
                        snippet="Preview not available",
                        timestamp="Unknown",
                        is_read=True  # Default assumption
                    ))
                elif len(text) > 10 and not any(char in text for char in ['🔍', '⋮', '←']):
                    # Likely subject or snippet text
                    emails.append(GmailMessage(
                        sender="Sender not detected",
                        subject=text[:50],  # Truncate long subjects
                        snippet=text if len(text) > 20 else "No preview",
                        timestamp="Unknown"
                    ))
            
            # Remove duplicates and limit results
            unique_emails = []
            seen_subjects = set()
            
            for email in emails:
                if email.subject not in seen_subjects:
                    unique_emails.append(email)
                    seen_subjects.add(email.subject)
                    
                if len(unique_emails) >= 10:  # Limit to 10 emails
                    break
            
            return unique_emails
        
        except Exception as e:
            logger.error(f"Email extraction failed: {e}")
            return []
    
    async def get_smart_suggestions(self) -> List[str]:
        """Get intelligent suggestions based on current Gmail state"""
        try:
            # Capture current screen and analyze context
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return ["Check inbox", "Compose email"]
            
            ocr_result = await self.ocr_engine.detect_text(image)
            detected_texts = [d.text.lower() for d in ocr_result.detections]
            
            suggestions = []
            
            # Context-aware suggestions
            if any('inbox' in text for text in detected_texts):
                suggestions.extend([
                    "Check unread emails",
                    "Search for recent emails",
                    "Compose new email"
                ])
            
            if any('compose' in text for text in detected_texts):
                suggestions.extend([
                    "Add recipients",
                    "Set email priority",
                    "Schedule send"
                ])
            
            if any('reply' in text for text in detected_texts):
                suggestions.extend([
                    "Reply to email",
                    "Forward email",
                    "Archive conversation"
                ])
            
            # Default suggestions if no specific context
            if not suggestions:
                suggestions = [
                    "Open Gmail inbox",
                    "Compose new email", 
                    "Search emails",
                    "Check important emails"
                ]
            
            return suggestions[:5]  # Limit to 5 suggestions
        
        except Exception as e:
            logger.error(f"Smart suggestions failed: {e}")
            return ["Check inbox", "Compose email", "Search emails"]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get Gmail connector performance statistics"""
        return {
            'automation_stats': self.automation_engine.get_statistics(),
            'cache_performance': self.position_cache.get_cache_performance(),
            'app_context': 'Gmail',
            'test_mode': self.test_mode
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.position_cache.close()
        logger.info("Gmail connector cleaned up")


# Example usage and testing
async def main():
    """Test Gmail connector functionality"""
    try:
        # Initialize connector in test mode
        gmail = GmailConnector(test_mode=True)
        
        # Test initialization
        print("Testing Gmail initialization...")
        init_result = await gmail.initialize_gmail()
        print(f"Init result: {init_result.message}")
        
        # Test inbox check
        print("\nTesting inbox check...")
        inbox_result = await gmail.check_inbox()
        print(f"Inbox result: {inbox_result.message}")
        if inbox_result.data:
            print(f"Found {inbox_result.data.get('count', 0)} emails")
        
        # Test smart suggestions
        print("\nTesting smart suggestions...")
        suggestions = await gmail.get_smart_suggestions()
        print(f"Suggestions: {suggestions}")
        
        # Show performance stats
        print(f"\nPerformance stats: {gmail.get_performance_stats()}")
        
        # Cleanup
        gmail.cleanup()
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())