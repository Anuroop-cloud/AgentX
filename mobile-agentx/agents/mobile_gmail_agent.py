"""
Mobile Gmail Agent for AgentX

Adapts the email_agent pattern for mobile Gmail automation.
Handles email actions with structured outputs optimized for mobile workflows.
"""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional, List
from ..app_connectors.gmail_connector import GmailConnector


# --- Define Mobile Gmail Action Schema ---
class GmailAction(BaseModel):
    action_type: str = Field(
        description="Type of Gmail action: 'send', 'read', 'search', 'draft', 'mark_read'",
        enum=["send", "read", "search", "draft", "mark_read"]
    )
    recipient: Optional[str] = Field(
        description="Email recipient for send/draft actions", 
        default=None
    )
    subject: Optional[str] = Field(
        description="Email subject for send/draft actions",
        default=None
    )
    body: Optional[str] = Field(
        description="Email body content for send/draft actions",
        default=None
    )
    search_query: Optional[str] = Field(
        description="Search query for search actions",
        default=None
    )
    max_results: Optional[int] = Field(
        description="Maximum number of results for read/search actions",
        default=10
    )
    unread_only: Optional[bool] = Field(
        description="Filter for unread emails only",
        default=False
    )


# --- Custom Gmail Tool Function ---
def gmail_tool(action: GmailAction) -> dict:
    """Execute Gmail actions using the connector"""
    connector = GmailConnector(mock_mode=True)
    
    if action.action_type == "send":
        return connector.send_email(
            to=action.recipient,
            subject=action.subject,
            body=action.body
        )
    elif action.action_type == "read":
        emails = connector.read_emails(
            max_results=action.max_results,
            unread_only=action.unread_only
        )
        return {
            "status": "emails_retrieved", 
            "count": len(emails),
            "emails": [
                {
                    "id": email.id,
                    "subject": email.subject,
                    "sender": email.sender,
                    "body": email.body[:200] + "..." if len(email.body) > 200 else email.body,
                    "timestamp": email.timestamp.isoformat(),
                    "is_read": email.is_read
                }
                for email in emails
            ]
        }
    elif action.action_type == "search":
        emails = connector.search_emails(
            query=action.search_query,
            max_results=action.max_results
        )
        return {
            "status": "search_completed",
            "query": action.search_query,
            "count": len(emails),
            "emails": [
                {
                    "id": email.id,
                    "subject": email.subject,
                    "sender": email.sender,
                    "body": email.body[:200] + "..." if len(email.body) > 200 else email.body,
                    "timestamp": email.timestamp.isoformat()
                }
                for email in emails
            ]
        }
    elif action.action_type == "draft":
        return connector.create_draft(
            to=action.recipient,
            subject=action.subject,
            body=action.body
        )
    else:
        return {"status": "error", "message": f"Unknown action type: {action.action_type}"}


# --- Create Mobile Gmail Agent ---
mobile_gmail_agent = LlmAgent(
    name="mobile_gmail_agent",
    model="gemini-2.0-flash",
    instruction="""
        You are a Mobile Gmail Assistant specialized in email automation for smartphones.
        Your task is to handle Gmail actions based on user requests in mobile workflows.

        CAPABILITIES:
        - Send emails with proper mobile-friendly formatting
        - Read and summarize emails for quick mobile viewing
        - Search emails using natural language queries
        - Create drafts for later sending
        - Mark emails as read/unread

        MOBILE CONTEXT AWARENESS:
        - Keep email summaries concise for mobile screens
        - Prioritize urgent/important emails first
        - Format responses for touch-friendly interaction
        - Consider mobile data usage in email handling

        GUIDELINES:
        - Always determine the appropriate action_type based on user request
        - For email composition, create professional but mobile-appropriate content
        - For email reading, provide concise summaries highlighting key information
        - For searches, use relevant keywords from user's natural language input
        - Handle multiple emails efficiently for mobile productivity

        RESPONSE FORMAT:
        Your response MUST be a valid GmailAction object with:
        - action_type: The Gmail action to perform
        - All relevant parameters filled based on the user's request
        - Mobile-optimized content and formatting

        Examples:
        - "Send email to john@company.com about meeting" → action_type: "send"
        - "Check my unread emails" → action_type: "read", unread_only: true
        - "Find emails about project X" → action_type: "search", search_query: "project X"
    """,
    description="Mobile Gmail agent for email automation in smartphone workflows",
    output_schema=GmailAction,
    output_key="gmail_action",
    tools=[gmail_tool]
)