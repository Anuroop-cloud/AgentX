"""
AI Mobile AgentX - Calendar Management Connector  
OCR-driven automation for calendar and event management
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from ..core import ScreenCaptureManager, OCRDetectionEngine, TapCoordinateEngine
from ..core.automation_engine import SmartAutomationEngine, AutomationSequence, AutomationAction, ActionType
from ..intelligence import IntelligentPositionCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event type categories"""
    MEETING = "meeting"
    APPOINTMENT = "appointment"
    REMINDER = "reminder"
    BIRTHDAY = "birthday"
    HOLIDAY = "holiday"
    PERSONAL = "personal"
    WORK = "work"

class RecurrenceType(Enum):
    """Recurrence pattern options"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKDAYS = "weekdays"
    CUSTOM = "custom"

@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)
    event_type: EventType = EventType.PERSONAL
    recurrence: RecurrenceType = RecurrenceType.NONE
    reminder_minutes: Optional[int] = None
    is_all_day: bool = False
    calendar_name: Optional[str] = None

@dataclass
class CalendarView:
    """Represents current calendar view state"""
    view_type: str  # day, week, month, agenda
    current_date: datetime
    visible_events: List[CalendarEvent] = field(default_factory=list)

class CalendarConnector:
    """
    Advanced Calendar automation connector with OCR-driven interaction
    Provides intelligent event management, scheduling, and calendar navigation
    """
    
    def __init__(self, screen_capture: ScreenCaptureManager = None,
                 ocr_engine: OCRDetectionEngine = None,
                 tap_engine: TapCoordinateEngine = None,
                 automation_engine: SmartAutomationEngine = None,
                 position_cache: IntelligentPositionCache = None):
        
        # Initialize core components
        self.screen_capture = screen_capture or ScreenCaptureManager()
        self.ocr_engine = ocr_engine or OCRDetectionEngine()
        self.tap_engine = tap_engine or TapCoordinateEngine()
        self.automation_engine = automation_engine or SmartAutomationEngine(
            self.screen_capture, self.ocr_engine, self.tap_engine
        )
        self.position_cache = position_cache or IntelligentPositionCache()
        
        # Calendar-specific UI patterns and text recognition
        self.ui_patterns = {
            'app_icon': ['Calendar', 'Google Calendar', 'Outlook', 'Events'],
            'view_modes': ['Day', 'Week', 'Month', 'Agenda', 'Year'],
            'navigation': ['Today', 'Previous', 'Next', 'Go to date'],
            'event_creation': ['Add', 'Create', 'New event', '+', 'Add event'],
            'event_details': ['Title', 'Time', 'Location', 'Description', 'Guests'],
            'recurrence_options': ['Repeat', 'Daily', 'Weekly', 'Monthly', 'Yearly'],
            'reminder_options': ['Reminder', 'Alert', '15 minutes', '1 hour', '1 day'],
            'calendar_management': ['Calendars', 'Settings', 'Share', 'Export']
        }
        
        # Calendar text patterns for OCR matching
        self.text_patterns = {
            'time_formats': ['AM', 'PM', ':', 'am', 'pm'],
            'date_indicators': ['Today', 'Tomorrow', 'Yesterday', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'month_names': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'event_indicators': ['Meeting', 'Appointment', 'Call', 'Lunch', 'Conference'],
            'duration_patterns': ['minutes', 'hour', 'hours', 'all day', 'min', 'hr'],
            'notification_icons': ['🔔', '⏰', '📅', '📆', '🕐']
        }
        
        # Track current state
        self.current_view: Optional[CalendarView] = None
        self.is_app_open = False
        self.selected_calendar = "default"
        self.cached_events: List[CalendarEvent] = []
        
        logger.info("Calendar connector initialized with OCR automation")
    
    async def open_calendar(self) -> bool:
        """Open Calendar app with smart detection"""
        try:
            logger.info("Opening Calendar app...")
            
            # Create automation sequence for opening Calendar
            actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Calendar', 'alternatives': ['Google Calendar', 'Outlook', 'Events']},
                    "Tap Calendar app icon"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 3.0},
                    "Wait for Calendar to load"
                ),
                AutomationAction(
                    ActionType.VERIFY,
                    {'text': 'Today', 'alternatives': ['Month', 'Week', 'Day', 'Add']},
                    "Verify Calendar opened successfully"
                )
            ]
            
            sequence = AutomationSequence("open_calendar", actions, timeout=15.0)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                self.is_app_open = True
                logger.info("✅ Calendar opened successfully")
                
                # Initialize current view
                await self._detect_current_view()
                
            else:
                logger.error("❌ Failed to open Calendar")
            
            return result.success
            
        except Exception as e:
            logger.error(f"Calendar opening failed: {e}")
            return False
    
    async def create_event(self, event: CalendarEvent) -> bool:
        """
        Create a new calendar event with comprehensive details
        
        Args:
            event: CalendarEvent object with event details
        """
        try:
            logger.info(f"Creating event: '{event.title}'")
            
            if not self.is_app_open:
                await self.open_calendar()
            
            # Start event creation
            creation_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Add', 'alternatives': ['+', 'Create', 'New event', 'Add event']},
                    "Tap add event button"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for event creation screen"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Title', 'alternatives': ['Event title', 'Name']},
                    "Tap title field"
                ),
                AutomationAction(
                    ActionType.TYPE,
                    {'text': event.title},
                    f"Enter event title: {event.title}"
                )
            ]
            
            # Set start time
            creation_actions.extend([
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Start time', 'alternatives': ['Starts', 'From']},
                    "Tap start time"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for time picker"
                )
            ])
            
            # Set time using OCR-based time picker interaction
            start_time_str = event.start_time.strftime("%I:%M %p")
            creation_actions.append(
                AutomationAction(
                    ActionType.CUSTOM,
                    {'action': 'set_time', 'time': start_time_str},
                    f"Set start time to {start_time_str}"
                )
            )
            
            # Set end time
            creation_actions.extend([
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'End time', 'alternatives': ['Ends', 'To', 'Until']},
                    "Tap end time"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for end time picker"
                )
            ])
            
            end_time_str = event.end_time.strftime("%I:%M %p")
            creation_actions.append(
                AutomationAction(
                    ActionType.CUSTOM,
                    {'action': 'set_time', 'time': end_time_str},
                    f"Set end time to {end_time_str}"
                )
            )
            
            # Add description if provided
            if event.description:
                creation_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Description', 'alternatives': ['Notes', 'Details']},
                        "Tap description field"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': event.description},
                        f"Enter description: {event.description}"
                    )
                ])
            
            # Add location if provided
            if event.location:
                creation_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Location', 'alternatives': ['Where', 'Place']},
                        "Tap location field"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': event.location},
                        f"Enter location: {event.location}"
                    )
                ])
            
            # Set recurrence if specified
            if event.recurrence != RecurrenceType.NONE:
                creation_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Repeat', 'alternatives': ['Recurrence', 'Recurring']},
                        "Open recurrence options"
                    ),
                    AutomationAction(
                        ActionType.TAP,
                        {'text': event.recurrence.value.title()},
                        f"Set recurrence to {event.recurrence.value}"
                    )
                ])
            
            # Set reminder if specified
            if event.reminder_minutes:
                reminder_text = self._format_reminder_time(event.reminder_minutes)
                creation_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Reminder', 'alternatives': ['Alert', 'Notification']},
                        "Open reminder options"
                    ),
                    AutomationAction(
                        ActionType.TAP,
                        {'text': reminder_text, 'alternatives': [f'{event.reminder_minutes} minutes']},
                        f"Set reminder to {reminder_text}"
                    )
                ])
            
            # Add attendees if specified
            if event.attendees:
                creation_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Guests', 'alternatives': ['Attendees', 'Invite', 'Add people']},
                        "Open guest list"
                    )
                ])
                
                for attendee in event.attendees:
                    creation_actions.extend([
                        AutomationAction(
                            ActionType.TYPE,
                            {'text': attendee},
                            f"Add attendee: {attendee}"
                        ),
                        AutomationAction(
                            ActionType.TAP,
                            {'text': 'Add', 'alternatives': ['Done', 'OK']},
                            "Confirm attendee"
                        )
                    ])
            
            # Save the event
            creation_actions.extend([
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Save', 'alternatives': ['Done', 'Create', 'Add']},
                    "Save event"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for event creation confirmation"
                )
            ])
            
            sequence = AutomationSequence("create_event", creation_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Add to cached events
                self.cached_events.append(event)
                logger.info(f"✅ Event '{event.title}' created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create event '{event.title}'")
                return False
                
        except Exception as e:
            logger.error(f"Event creation failed: {e}")
            return False
    
    async def find_events(self, search_query: str = None, date_range: Tuple[datetime, datetime] = None) -> List[CalendarEvent]:
        """
        Find events using search or date range filtering
        
        Args:
            search_query: Search term for event titles/descriptions
            date_range: Tuple of (start_date, end_date) for filtering
        """
        try:
            logger.info(f"Finding events" + (f" matching '{search_query}'" if search_query else "") + 
                       (f" in date range {date_range[0].date()} to {date_range[1].date()}" if date_range else ""))
            
            if not self.is_app_open:
                await self.open_calendar()
            
            events = []
            
            if search_query:
                # Use calendar search functionality
                search_actions = [
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Search', 'alternatives': ['🔍', 'Find']},
                        "Open search"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': search_query},
                        f"Search for: {search_query}"
                    ),
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Search', 'alternatives': ['Go', 'Find']},
                        "Execute search"
                    ),
                    AutomationAction(
                        ActionType.WAIT,
                        {'duration': 2.0},
                        "Wait for search results"
                    )
                ]
                
                sequence = AutomationSequence("search_events", search_actions)
                result = await self.automation_engine.execute_sequence(sequence)
                
                if result.success:
                    events = await self._parse_search_results()
            
            elif date_range:
                # Navigate to specific date range and parse events
                events = await self._get_events_in_range(date_range[0], date_range[1])
            
            else:
                # Get all visible events in current view
                events = await self._parse_current_view_events()
            
            logger.info(f"✅ Found {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Event search failed: {e}")
            return []
    
    async def update_event(self, event_identifier: str, updated_event: CalendarEvent) -> bool:
        """
        Update an existing event
        
        Args:
            event_identifier: Title or unique identifier of event to update
            updated_event: CalendarEvent with updated information
        """
        try:
            logger.info(f"Updating event: '{event_identifier}'")
            
            # First find and select the event
            events = await self.find_events(event_identifier)
            
            if not events:
                logger.error("Event not found for update")
                return False
            
            # Tap on the first matching event
            update_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': events[0].title},
                    "Select event to edit"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for event details"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Edit', 'alternatives': ['Modify', 'Change', '✏️']},
                    "Enter edit mode"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for edit screen"
                )
            ]
            
            # Update title if different
            if updated_event.title != events[0].title:
                update_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Title', 'alternatives': ['Event title']},
                        "Select title field"
                    ),
                    AutomationAction(
                        ActionType.CLEAR_TEXT,
                        {},
                        "Clear existing title"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': updated_event.title},
                        f"Update title to: {updated_event.title}"
                    )
                ])
            
            # Update time if different
            if updated_event.start_time != events[0].start_time:
                start_time_str = updated_event.start_time.strftime("%I:%M %p")
                update_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Start time', 'alternatives': ['Starts']},
                        "Select start time"
                    ),
                    AutomationAction(
                        ActionType.CUSTOM,
                        {'action': 'set_time', 'time': start_time_str},
                        f"Update start time to {start_time_str}"
                    )
                ])
            
            # Update other fields as needed...
            if updated_event.description and updated_event.description != events[0].description:
                update_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Description', 'alternatives': ['Notes']},
                        "Select description field"
                    ),
                    AutomationAction(
                        ActionType.CLEAR_TEXT,
                        {},
                        "Clear existing description"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': updated_event.description},
                        f"Update description"
                    )
                ])
            
            # Save changes
            update_actions.extend([
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Save', 'alternatives': ['Done', 'Update']},
                    "Save changes"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for update confirmation"
                )
            ])
            
            sequence = AutomationSequence("update_event", update_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                logger.info(f"✅ Event '{event_identifier}' updated successfully")
                return True
            else:
                logger.error(f"❌ Failed to update event '{event_identifier}'")
                return False
                
        except Exception as e:
            logger.error(f"Event update failed: {e}")
            return False
    
    async def delete_event(self, event_identifier: str) -> bool:
        """
        Delete an event from the calendar
        
        Args:
            event_identifier: Title or unique identifier of event to delete
        """
        try:
            logger.info(f"Deleting event: '{event_identifier}'")
            
            # Find and select the event
            events = await self.find_events(event_identifier)
            
            if not events:
                logger.error("Event not found for deletion")
                return False
            
            delete_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': events[0].title},
                    "Select event to delete"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for event details"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Delete', 'alternatives': ['Remove', '🗑️', 'Trash']},
                    "Tap delete button"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for confirmation dialog"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Delete', 'alternatives': ['Confirm', 'Yes', 'OK']},
                    "Confirm deletion"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for deletion confirmation"
                )
            ]
            
            sequence = AutomationSequence("delete_event", delete_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Remove from cached events
                self.cached_events = [e for e in self.cached_events if e.title != event_identifier]
                logger.info(f"✅ Event '{event_identifier}' deleted successfully")
                return True
            else:
                logger.error(f"❌ Failed to delete event '{event_identifier}'")
                return False
                
        except Exception as e:
            logger.error(f"Event deletion failed: {e}")
            return False
    
    async def change_view(self, view_type: str) -> bool:
        """
        Change calendar view (day, week, month, agenda)
        
        Args:
            view_type: Target view type ('day', 'week', 'month', 'agenda')
        """
        try:
            logger.info(f"Changing calendar view to {view_type}")
            
            view_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': view_type.title(), 'alternatives': [view_type.upper()]},
                    f"Switch to {view_type} view"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for view change"
                )
            ]
            
            sequence = AutomationSequence("change_view", view_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Update current view state
                await self._detect_current_view()
                logger.info(f"✅ Calendar view changed to {view_type}")
                return True
            else:
                logger.error(f"❌ Failed to change view to {view_type}")
                return False
                
        except Exception as e:
            logger.error(f"View change failed: {e}")
            return False
    
    async def navigate_to_date(self, target_date: datetime) -> bool:
        """
        Navigate to a specific date in the calendar
        
        Args:
            target_date: Target date to navigate to
        """
        try:
            logger.info(f"Navigating to date: {target_date.date()}")
            
            # Format date for input
            date_str = target_date.strftime("%m/%d/%Y")
            
            navigation_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Go to date', 'alternatives': ['Jump to', 'Select date', '📅']},
                    "Open date selection"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for date picker"
                ),
                AutomationAction(
                    ActionType.CUSTOM,
                    {'action': 'set_date', 'date': date_str},
                    f"Set date to {date_str}"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'OK', 'alternatives': ['Done', 'Go']},
                    "Confirm date navigation"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for navigation"
                )
            ]
            
            sequence = AutomationSequence("navigate_to_date", navigation_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Update current view with new date
                if self.current_view:
                    self.current_view.current_date = target_date
                logger.info(f"✅ Navigated to {target_date.date()}")
                return True
            else:
                logger.error(f"❌ Failed to navigate to {target_date.date()}")
                return False
                
        except Exception as e:
            logger.error(f"Date navigation failed: {e}")
            return False
    
    async def get_today_events(self) -> List[CalendarEvent]:
        """Get all events for today"""
        try:
            logger.info("Getting today's events...")
            
            # Navigate to today and get events
            today_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Today', 'alternatives': ['Today view', 'T']},
                    "Navigate to today"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for today view"
                )
            ]
            
            sequence = AutomationSequence("get_today", today_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                events = await self._parse_current_view_events()
                logger.info(f"✅ Found {len(events)} events today")
                return events
            else:
                logger.error("❌ Failed to get today's events")
                return []
                
        except Exception as e:
            logger.error(f"Today's events retrieval failed: {e}")
            return []
    
    async def get_upcoming_events(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """
        Get upcoming events within specified days
        
        Args:
            days_ahead: Number of days to look ahead (default: 7)
        """
        try:
            logger.info(f"Getting upcoming events for next {days_ahead} days...")
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            return await self._get_events_in_range(start_date, end_date)
            
        except Exception as e:
            logger.error(f"Upcoming events retrieval failed: {e}")
            return []
    
    # Helper methods for internal operations
    
    async def _detect_current_view(self):
        """Detect and update current calendar view state"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            # Determine view type based on visible elements
            view_type = "month"  # default
            current_date = datetime.now()
            
            for detection in detected_texts:
                text = detection['text'].strip().lower()
                
                # Detect view type
                if 'day' in text and any(word in text for word in ['view', 'today']):
                    view_type = "day"
                elif 'week' in text:
                    view_type = "week"
                elif 'agenda' in text or 'list' in text:
                    view_type = "agenda"
                
                # Try to detect current date being displayed
                if self._looks_like_date(text):
                    parsed_date = self._parse_date_text(text)
                    if parsed_date:
                        current_date = parsed_date
            
            self.current_view = CalendarView(
                view_type=view_type,
                current_date=current_date
            )
            
            logger.debug(f"Detected view: {view_type}, date: {current_date.date()}")
            
        except Exception as e:
            logger.error(f"View detection failed: {e}")
    
    async def _parse_current_view_events(self) -> List[CalendarEvent]:
        """Parse events visible in current calendar view"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return []
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            events = []
            current_event = {}
            
            for detection in detected_texts:
                text = detection['text'].strip()
                y_pos = detection['bbox'][1]
                
                # Skip UI elements
                if text.lower() in ['today', 'day', 'week', 'month', 'add', 'settings']:
                    continue
                
                # Look for event titles
                if self._looks_like_event_title(text):
                    if current_event:
                        events.append(self._create_event_from_parsed_data(current_event))
                    current_event = {'title': text}
                
                # Look for time information
                elif self._looks_like_time(text) and current_event:
                    current_event['time'] = text
                
                # Look for location information
                elif self._looks_like_location(text) and current_event:
                    current_event['location'] = text
            
            # Add final event
            if current_event:
                events.append(self._create_event_from_parsed_data(current_event))
            
            # Update current view with parsed events
            if self.current_view:
                self.current_view.visible_events = events
            
            logger.debug(f"Parsed {len(events)} events from current view")
            return events
            
        except Exception as e:
            logger.error(f"Event parsing failed: {e}")
            return []
    
    async def _parse_search_results(self) -> List[CalendarEvent]:
        """Parse events from search results"""
        # Similar logic to _parse_current_view_events but focused on search results
        return await self._parse_current_view_events()
    
    async def _get_events_in_range(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events within a specific date range"""
        try:
            events = []
            current_date = start_date
            
            while current_date <= end_date:
                # Navigate to each date and collect events
                await self.navigate_to_date(current_date)
                await asyncio.sleep(1)  # Brief pause for navigation
                
                daily_events = await self._parse_current_view_events()
                events.extend(daily_events)
                
                current_date += timedelta(days=1)
            
            return events
            
        except Exception as e:
            logger.error(f"Date range events retrieval failed: {e}")
            return []
    
    def _create_event_from_parsed_data(self, event_data: Dict[str, Any]) -> CalendarEvent:
        """Create CalendarEvent object from parsed data"""
        try:
            title = event_data.get('title', 'Untitled Event')
            
            # Parse time information
            time_str = event_data.get('time', '')
            start_time, end_time = self._parse_event_time(time_str)
            
            return CalendarEvent(
                title=title,
                start_time=start_time,
                end_time=end_time,
                location=event_data.get('location'),
                description=event_data.get('description')
            )
            
        except Exception as e:
            logger.error(f"Event creation from parsed data failed: {e}")
            # Return a basic event with current time
            return CalendarEvent(
                title=event_data.get('title', 'Untitled Event'),
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1)
            )
    
    def _parse_event_time(self, time_str: str) -> Tuple[datetime, datetime]:
        """Parse event time string into start and end datetime objects"""
        try:
            # Handle various time formats
            if '-' in time_str:
                # Format: "2:00 PM - 3:00 PM"
                parts = time_str.split('-')
                start_str = parts[0].strip()
                end_str = parts[1].strip()
            elif 'to' in time_str.lower():
                # Format: "2:00 PM to 3:00 PM"
                parts = time_str.lower().split('to')
                start_str = parts[0].strip()
                end_str = parts[1].strip()
            else:
                # Single time, assume 1 hour duration
                start_str = time_str.strip()
                end_str = None
            
            # Parse start time
            start_time = self._parse_time_string(start_str)
            
            # Parse or calculate end time
            if end_str:
                end_time = self._parse_time_string(end_str)
            else:
                end_time = start_time + timedelta(hours=1)
            
            return start_time, end_time
            
        except Exception as e:
            logger.error(f"Time parsing failed: {e}")
            # Return current time as fallback
            now = datetime.now()
            return now, now + timedelta(hours=1)
    
    def _parse_time_string(self, time_str: str) -> datetime:
        """Parse individual time string to datetime"""
        try:
            # Clean up the time string
            time_str = time_str.strip().upper()
            
            # Handle AM/PM formats
            if 'PM' in time_str or 'AM' in time_str:
                time_part = time_str.replace('PM', '').replace('AM', '').strip()
                is_pm = 'PM' in time_str
                
                # Parse hour and minute
                if ':' in time_part:
                    hour_str, minute_str = time_part.split(':')
                    hour = int(hour_str)
                    minute = int(minute_str)
                else:
                    hour = int(time_part)
                    minute = 0
                
                # Convert to 24-hour format
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
                
                # Create datetime with today's date
                today = datetime.now().date()
                return datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            else:
                # Assume 24-hour format
                if ':' in time_str:
                    hour_str, minute_str = time_str.split(':')
                    hour = int(hour_str)
                    minute = int(minute_str)
                else:
                    hour = int(time_str)
                    minute = 0
                
                today = datetime.now().date()
                return datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                
        except Exception as e:
            logger.error(f"Individual time parsing failed: {e}")
            return datetime.now()
    
    # Text pattern recognition helpers
    
    def _looks_like_event_title(self, text: str) -> bool:
        """Check if text looks like an event title"""
        # Skip very short or very long text
        if len(text) < 3 or len(text) > 100:
            return False
        
        # Skip common UI elements
        ui_elements = ['today', 'week', 'month', 'day', 'add', 'search', 'settings']
        if text.lower() in ui_elements:
            return False
        
        # Skip pure time or date formats
        if self._looks_like_time(text) or self._looks_like_date(text):
            return False
        
        return True
    
    def _looks_like_time(self, text: str) -> bool:
        """Check if text represents time"""
        time_indicators = [':', 'AM', 'PM', 'am', 'pm']
        return any(indicator in text for indicator in time_indicators) and any(c.isdigit() for c in text)
    
    def _looks_like_date(self, text: str) -> bool:
        """Check if text represents a date"""
        date_indicators = ['/', '-', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return any(indicator in text for indicator in date_indicators)
    
    def _looks_like_location(self, text: str) -> bool:
        """Check if text looks like a location"""
        location_indicators = ['room', 'building', 'street', 'avenue', 'road', 'conference', 'office']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in location_indicators)
    
    def _parse_date_text(self, text: str) -> Optional[datetime]:
        """Parse date text into datetime object"""
        try:
            # This would need more sophisticated date parsing
            # For now, return None to indicate parsing failed
            return None
        except:
            return None
    
    def _format_reminder_time(self, minutes: int) -> str:
        """Format reminder time in minutes to human-readable string"""
        if minutes < 60:
            return f"{minutes} minutes"
        elif minutes == 60:
            return "1 hour"
        elif minutes < 1440:  # Less than a day
            hours = minutes // 60
            return f"{hours} hours"
        else:
            days = minutes // 1440
            return f"{days} days"
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection and status information"""
        return {
            'app_open': self.is_app_open,
            'current_view': {
                'type': self.current_view.view_type if self.current_view else None,
                'date': self.current_view.current_date.isoformat() if self.current_view else None,
                'visible_events_count': len(self.current_view.visible_events) if self.current_view else 0
            } if self.current_view else None,
            'selected_calendar': self.selected_calendar,
            'cached_events_count': len(self.cached_events),
            'capabilities': {
                'create_events': True,
                'search_events': True,
                'update_events': True,
                'delete_events': True,
                'view_navigation': True,
                'date_navigation': True,
                'recurring_events': True,
                'reminders': True,
                'attendee_management': True
            }
        }


# Example usage
async def demo_calendar_automation():
    """Demonstrate Calendar automation capabilities"""
    try:
        print("📅 Calendar Automation Demo")
        print("=" * 40)
        
        # Initialize connector
        calendar = CalendarConnector()
        
        # Open Calendar
        print("1. Opening Calendar...")
        success = await calendar.open_calendar()
        if not success:
            print("❌ Failed to open Calendar")
            return
        
        # Create a new event
        print("\n2. Creating new event...")
        new_event = CalendarEvent(
            title="AI Demo Meeting",
            start_time=datetime.now() + timedelta(hours=2),
            end_time=datetime.now() + timedelta(hours=3),
            description="Demonstration of AI-driven calendar automation",
            location="Conference Room A",
            attendees=["colleague@example.com"],
            reminder_minutes=30
        )
        
        success = await calendar.create_event(new_event)
        if success:
            print("✅ Event created successfully")
        
        # Get today's events
        print("\n3. Getting today's events...")
        today_events = await calendar.get_today_events()
        print(f"Found {len(today_events)} events today:")
        for event in today_events[:3]:  # Show first 3
            print(f"   📅 {event.title} at {event.start_time.strftime('%I:%M %p')}")
        
        # Search for events
        print("\n4. Searching for 'meeting' events...")
        meeting_events = await calendar.find_events("meeting")
        print(f"Found {len(meeting_events)} meeting events")
        
        # Change view to week
        print("\n5. Changing to week view...")
        await calendar.change_view("week")
        print("✅ Switched to week view")
        
        # Get upcoming events
        print("\n6. Getting upcoming events (next 7 days)...")
        upcoming = await calendar.get_upcoming_events(7)
        print(f"Found {len(upcoming)} upcoming events")
        
        # Navigate to specific date
        target_date = datetime.now() + timedelta(days=3)
        print(f"\n7. Navigating to {target_date.date()}...")
        await calendar.navigate_to_date(target_date)
        print("✅ Date navigation completed")
        
        print("\n📅 Calendar automation demo completed!")
        
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(demo_calendar_automation())