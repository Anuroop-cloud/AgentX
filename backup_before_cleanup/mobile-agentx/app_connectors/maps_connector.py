"""
Maps Connector for Mobile AgentX

Handles Google Maps API integration for mobile automation workflows.
Supports location search, directions, traffic info, and place details.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Location:
    """Structured location representation"""
    name: str
    address: str
    latitude: float
    longitude: float
    place_id: Optional[str] = None
    rating: Optional[float] = None
    phone: Optional[str] = None


@dataclass 
class RouteInfo:
    """Structured route information"""
    distance: str
    duration: str
    duration_in_traffic: str
    start_address: str
    end_address: str
    steps: List[str]
    traffic_status: str = "normal"  # light, moderate, heavy


class MapsConnector:
    """Google Maps API connector for mobile automation"""
    
    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = True):
        """
        Initialize Maps connector
        
        Args:
            api_key: Google Maps API key
            mock_mode: Use mock responses for hackathon demo
        """
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.mock_mode = mock_mode
        self.app_name = "Google Maps"
        
    def search_places(self, query: str, location: Optional[Tuple[float, float]] = None, 
                     radius: int = 5000) -> List[Location]:
        """Search for places using text query"""
        if self.mock_mode:
            mock_places = [
                Location(
                    name="TechCorp Office Building",
                    address="123 Innovation Drive, San Francisco, CA 94105",
                    latitude=37.7749,
                    longitude=-122.4194,
                    place_id="ChIJmock123",
                    rating=4.2,
                    phone="+1-555-0123"
                ),
                Location(
                    name="Downtown Coffee House",
                    address="456 Market Street, San Francisco, CA 94102", 
                    latitude=37.7849,
                    longitude=-122.4094,
                    place_id="ChIJmock456",
                    rating=4.5,
                    phone="+1-555-0456"
                ),
                Location(
                    name="City Gym Fitness Center",
                    address="789 Fitness Way, San Francisco, CA 94103",
                    latitude=37.7649,
                    longitude=-122.4294,
                    place_id="ChIJmock789",
                    rating=4.1,
                    phone="+1-555-0789"
                )
            ]
            
            # Simple mock filtering based on query
            query_lower = query.lower()
            filtered_places = [
                place for place in mock_places 
                if query_lower in place.name.lower() or query_lower in place.address.lower()
            ]
            
            if not filtered_places:
                # Return all if no matches (for demo purposes)
                filtered_places = mock_places
                
            return filtered_places[:5]
        
        # Real Google Maps Places API implementation would go here
        return []
    
    def get_directions(self, origin: str, destination: str, mode: str = "driving") -> RouteInfo:
        """Get directions between two locations"""
        if self.mock_mode:
            # Mock route based on common locations
            if "office" in destination.lower() or "techcorp" in destination.lower():
                return RouteInfo(
                    distance="12.3 miles",
                    duration="28 minutes",
                    duration_in_traffic="35 minutes",
                    start_address=origin,
                    end_address="TechCorp Office Building, 123 Innovation Drive, San Francisco, CA",
                    steps=[
                        "Head north on Main St toward 1st Ave",
                        "Turn right onto Highway 101 N",
                        "Take exit 42B for Innovation Drive",
                        "Turn left onto Innovation Drive",
                        "Destination will be on the right"
                    ],
                    traffic_status="moderate"
                )
            else:
                return RouteInfo(
                    distance="8.7 miles",
                    duration="18 minutes", 
                    duration_in_traffic="22 minutes",
                    start_address=origin,
                    end_address=destination,
                    steps=[
                        "Head south on current street",
                        "Turn right onto Market Street",
                        "Continue straight for 5 miles",
                        "Turn left at destination street",
                        "Destination will be on the left"
                    ],
                    traffic_status="light"
                )
        
        # Real Google Maps Directions API implementation would go here
        return RouteInfo("", "", "", "", "", [], "unknown")
    
    def get_current_traffic(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get current traffic conditions for a route"""
        if self.mock_mode:
            route_info = self.get_directions(origin, destination)
            return {
                "status": "success",
                "traffic_status": route_info.traffic_status,
                "duration_normal": route_info.duration,
                "duration_with_traffic": route_info.duration_in_traffic,
                "delay_minutes": 7 if route_info.traffic_status == "moderate" else 0,
                "alternative_routes_available": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Real implementation would use Google Maps Traffic API
        return {"status": "error", "message": "Real Maps API not implemented yet"}
    
    def find_nearby(self, location: Tuple[float, float], place_type: str = "restaurant", 
                   radius: int = 1000) -> List[Location]:
        """Find nearby places of specific type"""
        if self.mock_mode:
            mock_nearby = {
                "restaurant": [
                    Location("Italian Bistro", "234 Food St, San Francisco, CA", 37.7750, -122.4180, rating=4.3),
                    Location("Sushi Place", "567 Dine Ave, San Francisco, CA", 37.7760, -122.4170, rating=4.6)
                ],
                "gas_station": [
                    Location("Shell Station", "890 Gas Rd, San Francisco, CA", 37.7740, -122.4200, rating=3.8),
                    Location("Chevron", "321 Fuel St, San Francisco, CA", 37.7730, -122.4210, rating=3.9)
                ],
                "hospital": [
                    Location("City General Hospital", "111 Health Blvd, San Francisco, CA", 37.7720, -122.4220, rating=4.0)
                ]
            }
            
            return mock_nearby.get(place_type, [])
        
        # Real Google Maps Nearby Search API implementation would go here
        return []
    
    def geocode_address(self, address: str) -> Optional[Location]:
        """Convert address to coordinates"""
        if self.mock_mode:
            # Mock geocoding for common addresses
            if "techcorp" in address.lower() or "123" in address:
                return Location(
                    name="TechCorp Office",
                    address="123 Innovation Drive, San Francisco, CA 94105",
                    latitude=37.7749,
                    longitude=-122.4194
                )
            else:
                # Generic San Francisco location
                return Location(
                    name="Generic Location",
                    address=address,
                    latitude=37.7749,
                    longitude=-122.4194
                )
        
        # Real Google Maps Geocoding API implementation would go here
        return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert coordinates to address"""
        if self.mock_mode:
            return f"Mock Address for coordinates ({latitude}, {longitude}), San Francisco, CA"
        
        # Real Google Maps Reverse Geocoding API implementation would go here
        return None
    
    def get_place_details(self, place_id: str) -> Optional[Location]:
        """Get detailed information about a place"""
        if self.mock_mode:
            mock_details = {
                "ChIJmock123": Location(
                    name="TechCorp Office Building",
                    address="123 Innovation Drive, San Francisco, CA 94105",
                    latitude=37.7749,
                    longitude=-122.4194,
                    place_id="ChIJmock123",
                    rating=4.2,
                    phone="+1-555-0123"
                )
            }
            return mock_details.get(place_id)
        
        # Real Google Maps Place Details API implementation would go here
        return None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Check Maps connection status"""
        return {
            "app_name": self.app_name,
            "connected": True if self.mock_mode else bool(self.api_key),
            "mock_mode": self.mock_mode,
            "capabilities": [
                "search_places",
                "get_directions", 
                "get_current_traffic",
                "find_nearby",
                "geocode_address",
                "reverse_geocode",
                "get_place_details"
            ]
        }