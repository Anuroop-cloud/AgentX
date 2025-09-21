"""
Mobile WhatsApp Agent for AgentX

Handles WhatsApp automation for mobile workflows including messaging,
contact management, and group communication.
"""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional, List
from ..app_connectors.whatsapp_connector import WhatsAppConnector


# --- Define Mobile WhatsApp Action Schema ---
class WhatsAppAction(BaseModel):
    action_type: str = Field(
        description="Type of WhatsApp action: 'send', 'read', 'send_location', 'get_contacts'",
        enum=["send", "read", "send_location", "get_contacts"]
    )
    contact: Optional[str] = Field(
        description="Contact phone number or name for messaging actions",
        default=None
    )
    message: Optional[str] = Field(
        description="Message content to send",
        default=None
    )
    latitude: Optional[float] = Field(
        description="Latitude for location sharing",
        default=None
    )
    longitude: Optional[float] = Field(
        description="Longitude for location sharing", 
        default=None
    )
    location_name: Optional[str] = Field(
        description="Name/description of location being shared",
        default=""
    )
    max_results: Optional[int] = Field(
        description="Maximum number of messages to retrieve",
        default=10
    )


# --- Custom WhatsApp Tool Function ---
def whatsapp_tool(action: WhatsAppAction) -> dict:
    """Execute WhatsApp actions using the connector"""
    connector = WhatsAppConnector(mock_mode=True)
    
    if action.action_type == "send":
        return connector.send_message(
            to=action.contact,
            message=action.message
        )
    elif action.action_type == "read":
        messages = connector.read_messages(
            contact=action.contact,
            max_results=action.max_results
        )
        return {
            "status": "messages_retrieved",
            "count": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "contact": msg.contact,
                    "contact_name": msg.contact_name,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "is_from_me": msg.is_from_me
                }
                for msg in messages
            ]
        }
    elif action.action_type == "send_location":
        return connector.send_location(
            to=action.contact,
            latitude=action.latitude,
            longitude=action.longitude,
            name=action.location_name
        )
    elif action.action_type == "get_contacts":
        contacts = connector.get_contacts()
        return {
            "status": "contacts_retrieved",
            "count": len(contacts),
            "contacts": contacts
        }
    else:
        return {"status": "error", "message": f"Unknown action type: {action.action_type}"}


# --- Create Mobile WhatsApp Agent ---
mobile_whatsapp_agent = LlmAgent(
    name="mobile_whatsapp_agent",
    model="gemini-2.0-flash",
    instruction="""
        You are a Mobile WhatsApp Assistant specialized in messaging automation for smartphones.
        Your task is to handle WhatsApp actions based on user requests in mobile workflows.

        CAPABILITIES:
        - Send text messages to contacts and groups
        - Read and summarize recent conversations
        - Share location information
        - Manage contact lists
        - Handle group messaging efficiently

        MOBILE CONTEXT AWARENESS:
        - Keep messages concise and mobile-appropriate
        - Use casual, friendly tone for personal messages
        - Professional tone for business contacts
        - Consider recipient context and relationship
        - Handle location sharing for meetups and navigation

        GUIDELINES:
        - Determine the appropriate action_type based on user request
        - For messaging, adapt tone to relationship (personal/professional)
        - For reading messages, summarize key points for quick mobile review
        - For location sharing, include helpful context
        - Handle contact identification intelligently (name or phone number)

        RESPONSE FORMAT:
        Your response MUST be a valid WhatsAppAction object with:
        - action_type: The WhatsApp action to perform
        - All relevant parameters filled based on the user's request
        - Mobile-optimized messaging and context

        Examples:
        - "Send John a message about the meeting" → action_type: "send"
        - "Check my recent WhatsApp messages" → action_type: "read"
        - "Share my location with Sarah" → action_type: "send_location"
        - "Show me my WhatsApp contacts" → action_type: "get_contacts"
    """,
    description="Mobile WhatsApp agent for messaging automation in smartphone workflows",
    output_schema=WhatsAppAction,
    output_key="whatsapp_action",
    tools=[whatsapp_tool]
)