"""
Mobile Calendar Agent for AgentX

Handles calendar automation for mobile workflows including event management,
scheduling, and calendar coordination.
"""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from ..app_connectors.calendar_connector import CalendarConnector


# --- Define Mobile Calendar Action Schema ---
class CalendarAction(BaseModel):
    action_type: str = Field(
        description="Type of calendar action: 'create_event', 'get_events', 'get_today', 'get_upcoming', 'find_free_time'",
        enum=["create_event", "get_events", "get_today", "get_upcoming", "find_free_time"]
    )
    event_title: Optional[str] = Field(
        description="Title for new event",
        default=None
    )
    event_description: Optional[str] = Field(
        description="Description for new event",
        default=""
    )
    start_time: Optional[str] = Field(
        description="Event start time in ISO format",
        default=None
    )
    end_time: Optional[str] = Field(
        description="Event end time in ISO format", 
        default=None
    )
    location: Optional[str] = Field(
        description="Event location",
        default=""
    )
    attendees: Optional[List[str]] = Field(
        description="List of attendee email addresses",
        default=None
    )
    hours_ahead: Optional[int] = Field(
        description="Hours ahead to look for upcoming events",
        default=24
    )
    duration_minutes: Optional[int] = Field(
        description="Duration in minutes for free time slots",
        default=60
    )


# --- Custom Calendar Tool Function ---
def calendar_tool(action: CalendarAction) -> dict:
    """Execute Calendar actions using the connector"""
    connector = CalendarConnector(mock_mode=True)
    
    if action.action_type == "create_event":
        start_dt = datetime.fromisoformat(action.start_time.replace('Z', '+00:00')) if action.start_time else datetime.now()
        end_dt = datetime.fromisoformat(action.end_time.replace('Z', '+00:00')) if action.end_time else start_dt + timedelta(hours=1)
        
        return connector.create_event(
            title=action.event_title,
            start_time=start_dt,
            end_time=end_dt,
            description=action.event_description,
            location=action.location,
            attendees=action.attendees or []
        )
    elif action.action_type == "get_events":
        events = connector.get_events()
        return {
            "status": "events_retrieved",
            "count": len(events),
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "location": event.location,
                    "attendees": event.attendees or [],
                    "is_all_day": event.is_all_day
                }
                for event in events
            ]
        }
    elif action.action_type == "get_today":
        events = connector.get_today_events()
        return {
            "status": "today_events_retrieved",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "count": len(events),
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.strftime("%H:%M"),
                    "end_time": event.end_time.strftime("%H:%M"),
                    "location": event.location,
                    "description": event.description
                }
                for event in events
            ]
        }
    elif action.action_type == "get_upcoming":
        events = connector.get_upcoming_events(hours_ahead=action.hours_ahead)
        return {
            "status": "upcoming_events_retrieved",
            "hours_ahead": action.hours_ahead,
            "count": len(events),
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "time_until": str(event.start_time - datetime.now()),
                    "location": event.location,
                    "attendees": event.attendees or []
                }
                for event in events
            ]
        }
    elif action.action_type == "find_free_time":
        free_slots = connector.find_free_time(duration_minutes=action.duration_minutes)
        return {
            "status": "free_time_found",
            "duration_minutes": action.duration_minutes,
            "count": len(free_slots),
            "free_slots": [
                {
                    "start": slot["start"].isoformat(),
                    "end": slot["end"].isoformat(),
                    "duration": f"{action.duration_minutes} minutes"
                }
                for slot in free_slots
            ]
        }
    else:
        return {"status": "error", "message": f"Unknown action type: {action.action_type}"}


# --- Create Mobile Calendar Agent ---
mobile_calendar_agent = LlmAgent(
    name="mobile_calendar_agent",
    model="gemini-2.0-flash",
    instruction="""
        You are a Mobile Calendar Assistant specialized in calendar automation for smartphones.
        Your task is to handle calendar actions based on user requests in mobile workflows.

        CAPABILITIES:
        - Create calendar events with smart scheduling
        - View today's schedule optimized for mobile
        - Check upcoming events and deadlines
        - Find free time slots for new meetings
        - Manage event details and attendee lists

        MOBILE CONTEXT AWARENESS:
        - Provide concise event summaries for mobile screens
        - Consider travel time between locations
        - Prioritize immediate and urgent events
        - Format times in user-friendly mobile format
        - Handle quick scheduling requests efficiently

        TIME INTELLIGENCE:
        - Parse natural language time expressions ("tomorrow at 3", "next Friday")
        - Suggest appropriate meeting durations
        - Consider business hours and time zones
        - Avoid scheduling conflicts automatically
        - Provide smart default times

        GUIDELINES:
        - Determine the appropriate action_type based on user request
        - For event creation, include all relevant details (title, time, location, attendees)
        - For schedule viewing, prioritize upcoming and important events
        - For free time finding, suggest realistic durations and times
        - Use ISO format for datetime fields when creating events

        RESPONSE FORMAT:
        Your response MUST be a valid CalendarAction object with:
        - action_type: The calendar action to perform
        - All relevant parameters filled based on the user's request
        - Proper datetime formatting for time-based fields

        Examples:
        - "Schedule a meeting with John tomorrow at 2 PM" → action_type: "create_event"
        - "What's on my calendar today?" → action_type: "get_today"
        - "Check my upcoming meetings" → action_type: "get_upcoming"
        - "When am I free for a 1-hour meeting?" → action_type: "find_free_time"
    """,
    description="Mobile Calendar agent for scheduling automation in smartphone workflows",
    output_schema=CalendarAction,
    output_key="calendar_action",
    tools=[calendar_tool]
)