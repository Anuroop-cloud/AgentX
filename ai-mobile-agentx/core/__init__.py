"""
AI Mobile AgentX - Core Package
Reformed automation engine with OCR-driven mobile interaction
"""

from .screen_capture import ScreenCaptureEngine, ScreenCaptureManager
from .ocr_engine import OCRDetectionEngine, TextDetection, OCRResult
from .tap_coordinator import TapCoordinateEngine, TapResult, TapCoordinate
from .automation_engine import SmartAutomationEngine, AutomationSequence, AutomationAction

__all__ = [
    'ScreenCaptureEngine', 'ScreenCaptureManager',
    'OCRDetectionEngine', 'TextDetection', 'OCRResult', 
    'TapCoordinateEngine', 'TapResult', 'TapCoordinate',
    'SmartAutomationEngine', 'AutomationSequence', 'AutomationAction'
]