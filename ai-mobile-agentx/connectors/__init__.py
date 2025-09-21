"""
AI Mobile AgentX - App Connectors
OCR-driven automation connectors for various mobile applications
"""

from .gmail_connector import GmailConnector
from .whatsapp_connector import WhatsAppConnector
from .spotify_connector import SpotifyConnector
from .maps_connector import MapsConnector  
from .calendar_connector import CalendarConnector

__all__ = [
    'GmailConnector',
    'WhatsAppConnector',
    'SpotifyConnector',
    'MapsConnector',
    'CalendarConnector'
]