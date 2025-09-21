"""
AI Mobile AgentX - Maps Navigation Connector
OCR-driven automation for Maps navigation and location services
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..core import ScreenCaptureManager, OCRDetectionEngine, TapCoordinateEngine  
from ..core.automation_engine import SmartAutomationEngine, AutomationSequence, AutomationAction, ActionType
from ..intelligence import IntelligentPositionCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NavigationMode(Enum):
    """Navigation mode options"""
    DRIVING = "driving"
    WALKING = "walking"
    TRANSIT = "transit"
    CYCLING = "cycling"

@dataclass
class Location:
    """Represents a location with coordinates and metadata"""
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None  # restaurant, gas station, etc.
    rating: Optional[float] = None
    is_favorite: bool = False

@dataclass  
class NavigationRoute:
    """Represents a navigation route"""
    destination: Location
    mode: NavigationMode
    duration: Optional[str] = None
    distance: Optional[str] = None
    traffic_conditions: Optional[str] = None
    alternative_routes: List[Dict[str, Any]] = None

class MapsConnector:
    """
    Advanced Maps automation connector with OCR-driven navigation
    Provides intelligent location search, route planning, and navigation control
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
        
        # Maps-specific UI patterns and text recognition
        self.ui_patterns = {
            'app_icon': ['Maps', 'Google Maps', 'Navigation'],
            'search_elements': ['Search here', 'Search', 'Find', 'Where to?'],
            'navigation_modes': ['Driving', 'Walking', 'Transit', 'Cycling'],
            'route_options': ['Routes', 'Directions', 'Start', 'Go'],
            'map_controls': ['Zoom in', 'Zoom out', 'My location', 'Compass'],
            'traffic_info': ['Traffic', 'Incidents', 'Congestion', 'Road conditions'],
            'place_categories': ['Restaurants', 'Gas stations', 'Hotels', 'Parking', 'ATM'],
            'saved_places': ['Home', 'Work', 'Favorites', 'Saved', 'Recent']
        }
        
        # Maps text patterns for OCR matching
        self.text_patterns = {
            'search_icon': ['🔍', '🔎', 'Search', 'SEARCH'],
            'location_pin': ['📍', '📌', 'Pin', 'Location'],
            'navigation_arrow': ['➡', '⬆', '⬇', '⬅', 'Turn', 'Continue'],
            'traffic_colors': ['Green', 'Yellow', 'Red', 'Normal', 'Heavy'],
            'distance_time': ['min', 'hr', 'km', 'mi', 'minutes', 'hours'],
            'directions': ['Turn left', 'Turn right', 'Continue', 'Exit', 'Merge']
        }
        
        # Track current state
        self.current_location: Optional[Location] = None
        self.active_navigation: Optional[NavigationRoute] = None
        self.is_app_open = False
        self.map_view_mode = 'default'  # default, satellite, terrain
        
        logger.info("Maps connector initialized with OCR automation")
    
    async def open_maps(self) -> bool:
        """Open Maps app with smart detection"""
        try:
            logger.info("Opening Maps app...")
            
            # Create automation sequence for opening Maps
            actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Maps', 'alternatives': ['Google Maps', 'Navigation', 'Map']},
                    "Tap Maps app icon"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 3.0},
                    "Wait for Maps to load"
                ),
                AutomationAction(
                    ActionType.VERIFY,
                    {'text': 'Search', 'alternatives': ['Where to?', 'Find', 'Search here']},
                    "Verify Maps opened successfully"
                )
            ]
            
            sequence = AutomationSequence("open_maps", actions, timeout=15.0)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                self.is_app_open = True
                logger.info("✅ Maps opened successfully")
                
                # Try to detect current location
                await self._detect_current_location()
                
            else:
                logger.error("❌ Failed to open Maps")
            
            return result.success
            
        except Exception as e:
            logger.error(f"Maps opening failed: {e}")
            return False
    
    async def search_location(self, query: str, category: str = None) -> List[Location]:
        """
        Search for locations with OCR-based result parsing
        
        Args:
            query: Search query (address, business name, landmark, etc.)
            category: Optional category filter (restaurants, gas stations, etc.)
        """
        try:
            logger.info(f"Searching for location: '{query}'" + (f" (category: {category})" if category else ""))
            
            if not self.is_app_open:
                await self.open_maps()
            
            # Navigate to search and enter query
            search_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['Where to?', 'Find', 'Search here']},
                    "Tap search bar"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for search input"
                ),
                AutomationAction(
                    ActionType.TYPE,
                    {'text': query},
                    f"Type search query: {query}"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['Go', 'Find', '🔍']},
                    "Execute search"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 3.0},
                    "Wait for search results"
                )
            ]
            
            # Apply category filter if specified
            if category:
                search_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': category.title(), 'alternatives': [category.upper()]},
                        f"Filter by category: {category}"
                    ),
                    AutomationAction(
                        ActionType.WAIT,
                        {'duration': 2.0},
                        "Wait for filtered results"
                    )
                ])
            
            sequence = AutomationSequence("search_location", search_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Parse search results from screen
                locations = await self._parse_location_results()
                logger.info(f"✅ Found {len(locations)} location results")
                return locations
            else:
                logger.error("❌ Location search failed")
                return []
                
        except Exception as e:
            logger.error(f"Location search failed: {e}")
            return []
    
    async def navigate_to_location(self, destination: str, mode: NavigationMode = NavigationMode.DRIVING) -> bool:
        """
        Start navigation to a specific location
        
        Args:
            destination: Destination address or location name
            mode: Navigation mode (driving, walking, transit, cycling)
        """
        try:
            logger.info(f"Starting navigation to '{destination}' via {mode.value}")
            
            # First search for the destination
            locations = await self.search_location(destination)
            
            if not locations:
                logger.error("Destination not found")
                return False
            
            # Select first result and start navigation
            target_location = locations[0]
            
            navigation_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Directions', 'alternatives': ['Navigate', 'Route', 'Go']},
                    "Tap directions button"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for route options"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': mode.value.title(), 'alternatives': [mode.value.upper()]},
                    f"Select {mode.value} navigation mode"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for route calculation"
                ),
                AutomationAction(
                    ActionType.TAP,  
                    {'text': 'Start', 'alternatives': ['Go', 'Begin', 'START']},
                    "Start navigation"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for navigation to begin"
                )
            ]
            
            sequence = AutomationSequence("navigate_to_location", navigation_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Create navigation route object
                self.active_navigation = NavigationRoute(
                    destination=target_location,
                    mode=mode
                )
                
                # Try to extract route information
                await self._extract_route_info()
                
                logger.info(f"✅ Navigation started to {destination}")
                return True
            else:
                logger.error("❌ Failed to start navigation")
                return False
                
        except Exception as e:
            logger.error(f"Navigation start failed: {e}")
            return False
    
    async def get_current_navigation_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current navigation session"""
        try:
            logger.info("Getting current navigation information...")
            
            if not self.active_navigation:
                logger.info("No active navigation session")
                return None
            
            # Capture current navigation screen
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return None
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            # Parse navigation information
            nav_info = {
                'destination': self.active_navigation.destination.name,
                'mode': self.active_navigation.mode.value,
                'estimated_time': None,
                'remaining_distance': None,
                'next_instruction': None,
                'traffic_conditions': None
            }
            
            for detection in detected_texts:
                text = detection['text'].strip()
                
                # Look for time patterns (e.g., "15 min", "1 hr 30 min")
                if self._is_time_pattern(text):
                    nav_info['estimated_time'] = text
                
                # Look for distance patterns (e.g., "5.2 km", "3.1 mi")
                elif self._is_distance_pattern(text):
                    nav_info['remaining_distance'] = text
                
                # Look for navigation instructions
                elif self._is_navigation_instruction(text):
                    nav_info['next_instruction'] = text
                
                # Look for traffic information
                elif self._is_traffic_info(text):
                    nav_info['traffic_conditions'] = text
            
            logger.info("✅ Navigation info retrieved")
            return nav_info
            
        except Exception as e:
            logger.error(f"Navigation info retrieval failed: {e}")
            return None
    
    async def stop_navigation(self) -> bool:
        """Stop current navigation session"""
        try:
            logger.info("Stopping navigation...")
            
            if not self.active_navigation:
                logger.info("No active navigation to stop")
                return True
            
            stop_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Stop', 'alternatives': ['End', 'Cancel', 'Exit']},
                    "Stop navigation"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for navigation stop"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Stop', 'alternatives': ['Confirm', 'Yes', 'OK']},
                    "Confirm stop navigation"
                )
            ]
            
            sequence = AutomationSequence("stop_navigation", stop_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                self.active_navigation = None
                logger.info("✅ Navigation stopped")
                return True
            else:
                logger.error("❌ Failed to stop navigation")
                return False
                
        except Exception as e:
            logger.error(f"Navigation stop failed: {e}")
            return False
    
    async def find_nearby_places(self, category: str, radius: str = "nearby") -> List[Location]:
        """
        Find nearby places of a specific category
        
        Args:
            category: Place category (restaurants, gas stations, hotels, etc.)
            radius: Search radius ("nearby", "1 km", "5 mi", etc.)
        """
        try:
            logger.info(f"Finding nearby {category}...")
            
            if not self.is_app_open:
                await self.open_maps()
            
            # Search for nearby places
            search_query = f"{category} {radius}"
            
            nearby_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['Where to?', 'Find']},
                    "Open search"
                ),
                AutomationAction(
                    ActionType.TYPE,
                    {'text': search_query},
                    f"Search for nearby {category}"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['Go', '🔍']},
                    "Execute search"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 3.0},
                    "Wait for nearby results"
                )
            ]
            
            sequence = AutomationSequence("find_nearby", nearby_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Parse nearby places
                places = await self._parse_nearby_places(category)
                logger.info(f"✅ Found {len(places)} nearby {category}")
                return places
            else:
                logger.error(f"❌ Failed to find nearby {category}")
                return []
                
        except Exception as e:
            logger.error(f"Nearby places search failed: {e}")
            return []
    
    async def save_location(self, location_name: str, label: str = "Saved") -> bool:
        """
        Save a location to favorites/saved places
        
        Args:
            location_name: Name or address of location to save
            label: Label for saved location (Home, Work, Favorite, etc.)
        """
        try:
            logger.info(f"Saving location '{location_name}' as '{label}'")
            
            # First search for the location
            locations = await self.search_location(location_name)
            
            if not locations:
                logger.error("Location not found for saving")
                return False
            
            save_actions = [
                AutomationAction(
                    ActionType.LONG_PRESS,
                    {'text': locations[0].name},
                    "Long press location for menu"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for context menu"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Save', 'alternatives': ['Add to', 'Favorite', '⭐']},
                    "Tap save option"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for save dialog"
                )
            ]
            
            # Add label if not default
            if label != "Saved":
                save_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Label', 'alternatives': ['Name', 'Title']},
                        "Tap label field"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': label},
                        f"Enter label: {label}"
                    )
                ])
            
            save_actions.extend([
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Save', 'alternatives': ['Done', 'OK']},
                    "Confirm save"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for save confirmation"
                )
            ])
            
            sequence = AutomationSequence("save_location", save_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                logger.info(f"✅ Location saved as '{label}'")
                return True
            else:
                logger.error("❌ Failed to save location")
                return False
                
        except Exception as e:
            logger.error(f"Location saving failed: {e}")
            return False
    
    async def get_traffic_conditions(self, route: str = None) -> Dict[str, Any]:
        """
        Get current traffic conditions for a route or general area
        
        Args:
            route: Optional specific route to check (origin to destination)
        """
        try:
            logger.info("Getting traffic conditions...")
            
            traffic_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Traffic', 'alternatives': ['Layers', 'Options']},
                    "Open traffic view"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for traffic overlay"
                )
            ]
            
            if route:
                # Get traffic for specific route
                traffic_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Directions', 'alternatives': ['Route']},
                        "Open route planning"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': route},
                        f"Enter route: {route}"
                    ),
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Go', 'alternatives': ['Search']},
                        "Get route traffic"
                    ),
                    AutomationAction(
                        ActionType.WAIT,
                        {'duration': 3.0},
                        "Wait for route traffic analysis"
                    )
                ])
            
            sequence = AutomationSequence("get_traffic", traffic_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Parse traffic information from screen
                traffic_info = await self._parse_traffic_conditions()
                logger.info("✅ Traffic conditions retrieved")
                return traffic_info
            else:
                logger.error("❌ Failed to get traffic conditions")
                return {}
                
        except Exception as e:
            logger.error(f"Traffic conditions retrieval failed: {e}")
            return {}
    
    async def change_map_view(self, view_type: str) -> bool:
        """
        Change map view type (default, satellite, terrain)
        
        Args:
            view_type: Map view type ('default', 'satellite', 'terrain')
        """
        try:
            logger.info(f"Changing map view to {view_type}")
            
            view_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Layers', 'alternatives': ['View', 'Options', 'Menu']},
                    "Open map layers menu"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for layers menu"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': view_type.title(), 'alternatives': [view_type.upper()]},
                    f"Select {view_type} view"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for view change"
                )
            ]
            
            sequence = AutomationSequence("change_map_view", view_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                self.map_view_mode = view_type
                logger.info(f"✅ Map view changed to {view_type}")
                return True
            else:
                logger.error(f"❌ Failed to change map view to {view_type}")
                return False
                
        except Exception as e:
            logger.error(f"Map view change failed: {e}")
            return False
    
    # Helper methods for internal operations
    
    async def _detect_current_location(self):
        """Try to detect and store current location"""
        try:
            # Look for current location indicators on screen
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            # Look for location-related text
            for detection in detected_texts:
                text = detection['text'].strip()
                
                # Check if text looks like a location/address
                if self._looks_like_address(text):
                    self.current_location = Location(
                        name="Current Location",
                        address=text
                    )
                    logger.debug(f"Detected current location: {text}")
                    break
                    
        except Exception as e:
            logger.error(f"Current location detection failed: {e}")
    
    async def _parse_location_results(self) -> List[Location]:
        """Parse location search results from screen"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return []
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            locations = []
            current_location = {}
            
            for detection in detected_texts:
                text = detection['text'].strip()
                y_pos = detection['bbox'][1]
                
                # Skip UI elements
                if text.lower() in ['search', 'directions', 'save', 'share', 'call']:
                    continue
                
                # Business names are usually prominently displayed
                if self._looks_like_business_name(text):
                    if current_location:
                        locations.append(Location(**current_location))
                    current_location = {'name': text}
                
                # Addresses usually follow business names
                elif self._looks_like_address(text) and current_location:
                    current_location['address'] = text
                
                # Ratings (e.g., "4.5", "★★★★☆")
                elif self._looks_like_rating(text) and current_location:
                    current_location['rating'] = self._parse_rating(text)
                
                # Categories (e.g., "Restaurant", "Gas Station")
                elif self._looks_like_category(text) and current_location:
                    current_location['category'] = text
            
            # Add final location
            if current_location:
                locations.append(Location(**current_location))
            
            logger.debug(f"Parsed {len(locations)} location results")
            return locations
            
        except Exception as e:
            logger.error(f"Location results parsing failed: {e}")
            return []
    
    async def _parse_nearby_places(self, category: str) -> List[Location]:
        """Parse nearby places results for specific category"""
        # Similar to _parse_location_results but with category-specific logic
        return await self._parse_location_results()
    
    async def _extract_route_info(self):
        """Extract route information from navigation screen"""
        try:
            if not self.active_navigation:
                return
                
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            for detection in detected_texts:
                text = detection['text'].strip()
                
                # Look for duration (e.g., "25 min", "1 hr 15 min")
                if self._is_time_pattern(text):
                    self.active_navigation.duration = text
                
                # Look for distance (e.g., "15.2 km", "9.4 mi")
                elif self._is_distance_pattern(text):
                    self.active_navigation.distance = text
                
                # Look for traffic conditions
                elif self._is_traffic_info(text):
                    self.active_navigation.traffic_conditions = text
            
            logger.debug("Route information extracted")
            
        except Exception as e:
            logger.error(f"Route info extraction failed: {e}")
    
    async def _parse_traffic_conditions(self) -> Dict[str, Any]:
        """Parse traffic conditions from traffic overlay"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return {}
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            traffic_info = {
                'overall_conditions': 'unknown',
                'incidents': [],
                'delay_info': None,
                'alternative_routes': []
            }
            
            for detection in detected_texts:
                text = detection['text'].strip()
                
                # Traffic condition indicators
                if text.lower() in ['heavy traffic', 'congestion', 'slow']:
                    traffic_info['overall_conditions'] = 'heavy'
                elif text.lower() in ['light traffic', 'clear', 'normal']:
                    traffic_info['overall_conditions'] = 'light'
                elif text.lower() in ['moderate traffic', 'busy']:
                    traffic_info['overall_conditions'] = 'moderate'
                
                # Incident information
                elif any(word in text.lower() for word in ['accident', 'construction', 'road work', 'closure']):
                    traffic_info['incidents'].append(text)
                
                # Delay information
                elif 'delay' in text.lower() or 'slower' in text.lower():
                    traffic_info['delay_info'] = text
            
            return traffic_info
            
        except Exception as e:
            logger.error(f"Traffic conditions parsing failed: {e}")
            return {}
    
    # Text pattern recognition helpers
    
    def _looks_like_address(self, text: str) -> bool:
        """Check if text looks like an address"""
        address_indicators = ['st', 'street', 'ave', 'avenue', 'rd', 'road', 'blvd', 'boulevard', 'dr', 'drive']
        text_lower = text.lower()
        
        # Has numbers and address keywords
        has_numbers = any(c.isdigit() for c in text)
        has_address_word = any(indicator in text_lower for indicator in address_indicators)
        
        return has_numbers and (has_address_word or len(text.split()) >= 3)
    
    def _looks_like_business_name(self, text: str) -> bool:
        """Check if text looks like a business name"""
        # Skip very short or very long text
        if len(text) < 3 or len(text) > 50:
            return False
        
        # Skip common UI elements
        ui_elements = ['search', 'directions', 'save', 'call', 'website', 'reviews']
        if text.lower() in ui_elements:
            return False
        
        # Skip pure numbers or time formats
        if text.isdigit() or ':' in text:
            return False
        
        return True
    
    def _looks_like_rating(self, text: str) -> bool:
        """Check if text looks like a rating"""
        # Star symbols
        if any(star in text for star in ['★', '⭐', '✯']):
            return True
        
        # Decimal numbers that could be ratings (1.0-5.0)
        try:
            rating = float(text)
            return 1.0 <= rating <= 5.0
        except:
            return False
    
    def _parse_rating(self, text: str) -> Optional[float]:
        """Parse rating from text"""
        try:
            # Extract number from text
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            if numbers:
                return float(numbers[0])
        except:
            pass
        return None
    
    def _looks_like_category(self, text: str) -> bool:
        """Check if text looks like a place category"""
        categories = [
            'restaurant', 'hotel', 'gas station', 'pharmacy', 'hospital', 
            'bank', 'atm', 'parking', 'shopping', 'grocery', 'coffee',
            'fast food', 'retail', 'service', 'automotive'
        ]
        return text.lower() in categories
    
    def _is_time_pattern(self, text: str) -> bool:
        """Check if text represents time duration"""
        time_keywords = ['min', 'hr', 'hour', 'minute', 'mins', 'hours', 'minutes']
        return any(keyword in text.lower() for keyword in time_keywords) and any(c.isdigit() for c in text)
    
    def _is_distance_pattern(self, text: str) -> bool:
        """Check if text represents distance"""
        distance_keywords = ['km', 'mi', 'mile', 'meter', 'm', 'miles', 'kilometers']
        return any(keyword in text.lower() for keyword in distance_keywords) and any(c.isdigit() for c in text)
    
    def _is_navigation_instruction(self, text: str) -> bool:
        """Check if text is a navigation instruction"""
        nav_keywords = [
            'turn left', 'turn right', 'continue', 'exit', 'merge', 'keep left', 
            'keep right', 'roundabout', 'straight', 'follow', 'take'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in nav_keywords)
    
    def _is_traffic_info(self, text: str) -> bool:
        """Check if text contains traffic information"""
        traffic_keywords = [
            'traffic', 'congestion', 'heavy', 'light', 'moderate', 'clear',
            'slow', 'fast', 'normal', 'delay', 'incident', 'accident'
        ]
        return any(keyword in text.lower() for keyword in traffic_keywords)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection and status information"""
        return {
            'app_open': self.is_app_open,
            'current_location': {
                'name': self.current_location.name if self.current_location else None,
                'address': self.current_location.address if self.current_location else None
            } if self.current_location else None,
            'active_navigation': {
                'destination': self.active_navigation.destination.name if self.active_navigation else None,
                'mode': self.active_navigation.mode.value if self.active_navigation else None,
                'duration': self.active_navigation.duration if self.active_navigation else None,
                'distance': self.active_navigation.distance if self.active_navigation else None
            } if self.active_navigation else None,
            'map_view_mode': self.map_view_mode,
            'capabilities': {
                'location_search': True,
                'navigation': True,
                'nearby_places': True,
                'traffic_info': True,
                'save_locations': True,
                'route_planning': True
            }
        }


# Example usage
async def demo_maps_automation():
    """Demonstrate Maps automation capabilities"""
    try:
        print("🗺️ Maps Automation Demo")
        print("=" * 40)
        
        # Initialize connector
        maps = MapsConnector()
        
        # Open Maps
        print("1. Opening Maps...")
        success = await maps.open_maps()
        if not success:
            print("❌ Failed to open Maps")
            return
        
        # Search for location
        print("\n2. Searching for Starbucks...")
        locations = await maps.search_location("Starbucks", "coffee")
        print(f"Found {len(locations)} coffee shops")
        
        if locations:
            first_location = locations[0]
            print(f"   📍 {first_location.name}")
            if first_location.address:
                print(f"       {first_location.address}")
        
        # Find nearby gas stations
        print("\n3. Finding nearby gas stations...")
        gas_stations = await maps.find_nearby_places("gas stations")
        print(f"Found {len(gas_stations)} nearby gas stations")
        
        # Start navigation demo
        if locations:
            print(f"\n4. Starting navigation to {first_location.name}...")
            success = await maps.navigate_to_location(first_location.name, NavigationMode.DRIVING)
            if success:
                print("✅ Navigation started")
                
                # Get navigation info
                await asyncio.sleep(2)
                nav_info = await maps.get_current_navigation_info()
                if nav_info:
                    print(f"   🕒 ETA: {nav_info.get('estimated_time', 'Unknown')}")
                    print(f"   📏 Distance: {nav_info.get('remaining_distance', 'Unknown')}")
                    if nav_info.get('next_instruction'):
                        print(f"   ➡️ Next: {nav_info['next_instruction']}")
                
                # Stop navigation
                print("\n5. Stopping navigation...")
                await maps.stop_navigation()
                print("✅ Navigation stopped")
        
        # Check traffic conditions
        print("\n6. Checking traffic conditions...")
        traffic = await maps.get_traffic_conditions()
        if traffic:
            print(f"   🚦 Conditions: {traffic.get('overall_conditions', 'Unknown')}")
            if traffic.get('incidents'):
                print(f"   ⚠️ Incidents: {len(traffic['incidents'])}")
        
        # Change map view
        print("\n7. Changing to satellite view...")
        await maps.change_map_view("satellite")
        print("✅ Map view changed")
        
        print("\n🗺️ Maps automation demo completed!")
        
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(demo_maps_automation())