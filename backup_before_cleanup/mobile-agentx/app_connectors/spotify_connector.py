"""
Spotify Connector for Mobile AgentX

Handles Spotify Web API integration for mobile automation workflows.
Supports playing music, managing playlists, and controlling playback.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Track:
    """Structured track representation"""
    id: str
    name: str
    artist: str
    album: str
    duration_ms: int
    preview_url: Optional[str] = None
    popularity: int = 0


@dataclass
class Playlist:
    """Structured playlist representation"""
    id: str
    name: str
    description: str
    track_count: int
    owner: str
    public: bool = False


class SpotifyConnector:
    """Spotify Web API connector for mobile automation"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 access_token: Optional[str] = None, mock_mode: bool = True):
        """
        Initialize Spotify connector
        
        Args:
            client_id: Spotify app client ID
            client_secret: Spotify app client secret
            access_token: User access token for API calls
            mock_mode: Use mock responses for hackathon demo
        """
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self.access_token = access_token or os.getenv("SPOTIFY_ACCESS_TOKEN") 
        self.mock_mode = mock_mode
        self.app_name = "Spotify"
        
    def play_music(self, query: str = "", playlist_id: str = "", device_id: str = "") -> Dict[str, Any]:
        """Play music based on search query or playlist"""
        if self.mock_mode:
            if query:
                return {
                    "status": "playing",
                    "action": "search_and_play",
                    "query": query,
                    "now_playing": {
                        "track": f"Mock Song for '{query}'",
                        "artist": "Mock Artist",
                        "album": "Mock Album"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            elif playlist_id:
                return {
                    "status": "playing",
                    "action": "playlist_play",
                    "playlist_id": playlist_id,
                    "now_playing": {
                        "track": "First Song in Playlist",
                        "artist": "Playlist Artist",
                        "album": "Playlist Album"
                    },
                    "timestamp": datetime.now().isoformat()
                }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def pause_music(self) -> Dict[str, Any]:
        """Pause current playback"""
        if self.mock_mode:
            return {
                "status": "paused",
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def resume_music(self) -> Dict[str, Any]:
        """Resume paused playback"""
        if self.mock_mode:
            return {
                "status": "playing",
                "action": "resumed",
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def skip_track(self, direction: str = "next") -> Dict[str, Any]:
        """Skip to next or previous track"""
        if self.mock_mode:
            return {
                "status": "skipped",
                "direction": direction,
                "now_playing": {
                    "track": f"{'Next' if direction == 'next' else 'Previous'} Mock Song",
                    "artist": "Mock Artist",
                    "album": "Mock Album"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Track]:
        """Search for tracks"""
        if self.mock_mode:
            mock_tracks = [
                Track(
                    id="mock_track_1",
                    name="Focus Flow",
                    artist="Ambient Collective",
                    album="Productivity Sounds",
                    duration_ms=240000,
                    popularity=75
                ),
                Track(
                    id="mock_track_2", 
                    name="Morning Energy",
                    artist="Upbeat Band",
                    album="Daily Motivation",
                    duration_ms=180000,
                    popularity=68
                ),
                Track(
                    id="mock_track_3",
                    name="Workout Pump",
                    artist="High Energy",
                    album="Gym Sessions",
                    duration_ms=200000,
                    popularity=82
                )
            ]
            
            # Simple mock filtering
            query_lower = query.lower()
            if query_lower:
                filtered_tracks = [
                    track for track in mock_tracks
                    if query_lower in track.name.lower() or query_lower in track.artist.lower()
                ]
                if not filtered_tracks:
                    filtered_tracks = mock_tracks  # Return all for demo
            else:
                filtered_tracks = mock_tracks
            
            return filtered_tracks[:limit]
        
        # Real Spotify Web API implementation would go here
        return []
    
    def get_playlists(self, user_id: str = "me") -> List[Playlist]:
        """Get user's playlists"""
        if self.mock_mode:
            return [
                Playlist(
                    id="mock_playlist_1",
                    name="Focus & Productivity",
                    description="Music for deep work and concentration",
                    track_count=45,
                    owner="user",
                    public=False
                ),
                Playlist(
                    id="mock_playlist_2",
                    name="Morning Motivation",
                    description="Energizing tracks to start your day",
                    track_count=32,
                    owner="user",
                    public=False
                ),
                Playlist(
                    id="mock_playlist_3",
                    name="Workout Hits",
                    description="High-energy music for exercise",
                    track_count=67,
                    owner="user",
                    public=True
                )
            ]
        
        # Real Spotify Web API implementation would go here
        return []
    
    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Dict[str, Any]:
        """Create a new playlist"""
        if self.mock_mode:
            playlist_id = f"mock_playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return {
                "status": "created",
                "playlist_id": playlist_id,
                "name": name,
                "description": description,
                "public": public,
                "url": f"https://open.spotify.com/playlist/{playlist_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> Dict[str, Any]:
        """Add tracks to a playlist"""
        if self.mock_mode:
            return {
                "status": "added",
                "playlist_id": playlist_id,
                "tracks_added": len(track_ids),
                "track_ids": track_ids,
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def get_current_playback(self) -> Dict[str, Any]:
        """Get current playback state"""
        if self.mock_mode:
            return {
                "is_playing": True,
                "device": {
                    "name": "Mobile Phone",
                    "type": "smartphone",
                    "volume_percent": 75
                },
                "track": {
                    "name": "Currently Playing Mock Song",
                    "artist": "Mock Artist",
                    "album": "Mock Album",
                    "duration_ms": 240000,
                    "progress_ms": 120000
                },
                "shuffle_state": False,
                "repeat_state": "off",
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def set_volume(self, volume_percent: int) -> Dict[str, Any]:
        """Set playback volume (0-100)"""
        volume_percent = max(0, min(100, volume_percent))
        
        if self.mock_mode:
            return {
                "status": "volume_set",
                "volume_percent": volume_percent,
                "timestamp": datetime.now().isoformat()
            }
        
        # Real Spotify Web API implementation would go here
        return {"status": "error", "message": "Real Spotify API not implemented yet"}
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Check Spotify connection status"""
        return {
            "app_name": self.app_name,
            "connected": True if self.mock_mode else bool(self.access_token),
            "mock_mode": self.mock_mode,
            "capabilities": [
                "play_music",
                "pause_music",
                "resume_music",
                "skip_track",
                "search_tracks",
                "get_playlists",
                "create_playlist",
                "add_tracks_to_playlist",
                "get_current_playback",
                "set_volume"
            ]
        }