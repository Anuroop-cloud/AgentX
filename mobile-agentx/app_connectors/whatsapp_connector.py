"""
WhatsApp Connector for Mobile AgentX

Handles WhatsApp Business API integration for mobile automation workflows.
Supports sending messages, reading conversations, and managing contacts.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WhatsAppMessage:
    """Structured WhatsApp message representation"""
    id: str
    contact: str
    contact_name: str
    message: str
    timestamp: datetime
    is_from_me: bool = False
    message_type: str = "text"  # text, image, audio, document


class WhatsAppConnector:
    """WhatsApp Business API connector for mobile automation"""
    
    def __init__(self, api_key: Optional[str] = None, phone_number_id: Optional[str] = None, mock_mode: bool = True):
        """
        Initialize WhatsApp connector
        
        Args:
            api_key: WhatsApp Business API key
            phone_number_id: WhatsApp Business phone number ID
            mock_mode: Use mock responses for hackathon demo
        """
        self.api_key = api_key or os.getenv("WHATSAPP_API_KEY")
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.mock_mode = mock_mode
        self.app_name = "WhatsApp"
        
    def send_message(self, to: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Send a WhatsApp message"""
        if self.mock_mode:
            return {
                "status": "sent",
                "message_id": f"wamid.mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "to": to,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "type": message_type
            }
        
        # Real WhatsApp Business API implementation would go here
        return {"status": "error", "message": "Real WhatsApp API not implemented yet"}
    
    def read_messages(self, contact: Optional[str] = None, max_results: int = 10, unread_only: bool = False) -> List[WhatsAppMessage]:
        """Read WhatsApp messages with optional filtering"""
        if self.mock_mode:
            mock_messages = [
                WhatsAppMessage(
                    id="wamid_mock_1",
                    contact="+1234567890",
                    contact_name="John Doe",
                    message="Hey! Are we still on for the meeting at 3 PM?",
                    timestamp=datetime.now(),
                    is_from_me=False
                ),
                WhatsAppMessage(
                    id="wamid_mock_2",
                    contact="+1234567891", 
                    contact_name="Sarah Johnson",
                    message="Thanks for the proposal! Looks great, let's discuss next steps.",
                    timestamp=datetime.now(),
                    is_from_me=False
                ),
                WhatsAppMessage(
                    id="wamid_mock_3",
                    contact="+1234567892",
                    contact_name="Team Group",
                    message="Reminder: Sprint planning meeting tomorrow at 10 AM",
                    timestamp=datetime.now(),
                    is_from_me=True
                )
            ]
            
            if contact:
                mock_messages = [msg for msg in mock_messages if msg.contact == contact]
            
            return mock_messages[:max_results]
        
        # Real WhatsApp API implementation would go here
        return []
    
    def send_template_message(self, to: str, template_name: str, parameters: List[str]) -> Dict[str, Any]:
        """Send a WhatsApp template message"""
        if self.mock_mode:
            return {
                "status": "sent",
                "message_id": f"wamid.template_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "to": to,
                "template": template_name,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
        
        # Real WhatsApp Business API implementation would go here
        return {"status": "error", "message": "Real WhatsApp API not implemented yet"}
    
    def get_contacts(self) -> List[Dict[str, Any]]:
        """Get WhatsApp contacts"""
        if self.mock_mode:
            return [
                {"phone": "+1234567890", "name": "John Doe", "status": "active"},
                {"phone": "+1234567891", "name": "Sarah Johnson", "status": "active"},
                {"phone": "+1234567892", "name": "Team Group", "status": "group"},
                {"phone": "+1234567893", "name": "Family", "status": "group"}
            ]
        
        # Real WhatsApp API implementation would go here
        return []
    
    def send_location(self, to: str, latitude: float, longitude: float, name: str = "", address: str = "") -> Dict[str, Any]:
        """Send location message"""
        if self.mock_mode:
            return {
                "status": "sent",
                "message_id": f"wamid.location_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "to": to,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": name,
                    "address": address
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Real WhatsApp API implementation would go here
        return {"status": "error", "message": "Real WhatsApp API not implemented yet"}
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Check WhatsApp connection status"""
        return {
            "app_name": self.app_name,
            "connected": True if self.mock_mode else bool(self.api_key and self.phone_number_id),
            "mock_mode": self.mock_mode,
            "capabilities": [
                "send_message",
                "read_messages",
                "send_template_message", 
                "get_contacts",
                "send_location"
            ]
        }