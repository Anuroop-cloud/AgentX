"""
AI Mobile AgentX - Spotify Music App Connector
OCR-driven automation for Spotify music streaming
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from ..core import ScreenCaptureManager, OCRDetectionEngine, TapCoordinateEngine
from ..core.automation_engine import SmartAutomationEngine, AutomationSequence, AutomationAction, ActionType
from ..intelligence import IntelligentPositionCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SpotifyTrack:
    """Represents a Spotify track"""
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[str] = None
    is_playing: bool = False

@dataclass
class SpotifyPlaylist:
    """Represents a Spotify playlist"""
    name: str
    track_count: Optional[int] = None
    creator: Optional[str] = None
    description: Optional[str] = None

class SpotifyConnector:
    """
    Advanced Spotify automation connector with OCR-driven interaction
    Provides intelligent music control, playlist management, and discovery
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
        
        # Spotify-specific UI patterns and text patterns
        self.ui_patterns = {
            'app_icon': ['Spotify', 'Music'],
            'main_navigation': ['Home', 'Search', 'Your Library', 'Premium'],
            'playback_controls': ['Play', 'Pause', 'Next', 'Previous', 'Shuffle', 'Repeat'],
            'search_elements': ['Search', 'Artists', 'Songs', 'Albums', 'Playlists', 'Podcasts'],
            'library_elements': ['Recently played', 'Made for you', 'Liked Songs', 'Downloaded'],
            'player_elements': ['Now playing', 'Queue', 'Devices', 'Volume'],
            'playlist_actions': ['Create playlist', 'Add to playlist', 'Remove', 'Download'],
            'premium_features': ['Premium', 'Upgrade', 'Ad-free', 'Skip', 'Offline']
        }
        
        # Spotify text patterns for better OCR matching
        self.text_patterns = {
            'play_button': ['▶', 'Play', 'PLAY'],
            'pause_button': ['⏸', 'Pause', 'PAUSE', '||'],
            'next_track': ['⏭', 'Next', 'NEXT', '>|'],
            'previous_track': ['⏮', 'Previous', 'PREVIOUS', '|<'],
            'shuffle': ['🔀', 'Shuffle', 'SHUFFLE'],
            'repeat': ['🔁', 'Repeat', 'REPEAT'],
            'heart_like': ['♥', '❤', 'Like', 'LIKE'],
            'search_icon': ['🔍', 'Search', 'SEARCH'],
            'volume': ['🔊', 'Volume', 'VOLUME'],
            'add_playlist': ['+', 'Add', 'CREATE', 'New playlist']
        }
        
        # Track current state
        self.current_track: Optional[SpotifyTrack] = None
        self.is_app_open = False
        self.playback_state = 'unknown'  # playing, paused, stopped
        
        logger.info("Spotify connector initialized with OCR automation")
    
    async def open_spotify(self) -> bool:
        """Open Spotify app with smart detection"""
        try:
            logger.info("Opening Spotify app...")
            
            # Create automation sequence for opening Spotify
            actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Spotify', 'alternatives': ['Music', 'Spotify Music']},
                    "Tap Spotify app icon"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 3.0},
                    "Wait for Spotify to load"
                ),
                AutomationAction(
                    ActionType.VERIFY,
                    {'text': 'Home', 'alternatives': ['Search', 'Your Library']},
                    "Verify Spotify opened successfully"
                )
            ]
            
            sequence = AutomationSequence("open_spotify", actions, timeout=15.0)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                self.is_app_open = True
                logger.info("✅ Spotify opened successfully")
            else:
                logger.error("❌ Failed to open Spotify")
            
            return result.success
            
        except Exception as e:
            logger.error(f"Spotify opening failed: {e}")
            return False
    
    async def search_music(self, query: str, search_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Search for music content with OCR-based result parsing
        
        Args:
            query: Search query (song, artist, album, etc.)
            search_type: Type of search ('all', 'songs', 'artists', 'albums', 'playlists')
        """
        try:
            logger.info(f"Searching Spotify for: '{query}' (type: {search_type})")
            
            if not self.is_app_open:
                await self.open_spotify()
            
            # Navigate to search
            search_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['🔍', 'SEARCH']},
                    "Navigate to search"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for search screen"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['What do you want to listen to?', 'Search songs']},
                    "Tap search bar"
                ),
                AutomationAction(
                    ActionType.TYPE,
                    {'text': query},
                    f"Type search query: {query}"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Search', 'alternatives': ['Go', 'Enter', '🔍']},
                    "Execute search"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for search results"
                )
            ]
            
            # Filter by type if specified
            if search_type != 'all':
                search_actions.append(
                    AutomationAction(
                        ActionType.TAP,
                        {'text': search_type.title(), 'alternatives': [search_type.upper()]},
                        f"Filter by {search_type}"
                    )
                )
                search_actions.append(
                    AutomationAction(
                        ActionType.WAIT,
                        {'duration': 1.0},
                        "Wait for filtered results"
                    )
                )
            
            sequence = AutomationSequence("search_music", search_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Parse search results from screen
                search_results = await self._parse_search_results()
                logger.info(f"✅ Found {len(search_results)} search results")
                return search_results
            else:
                logger.error("❌ Search execution failed")
                return []
                
        except Exception as e:
            logger.error(f"Music search failed: {e}")
            return []
    
    async def play_track(self, track_identifier: str, method: str = 'search') -> bool:
        """
        Play a specific track using various methods
        
        Args:
            track_identifier: Track name, artist, or search query
            method: How to find track ('search', 'library', 'recent')
        """
        try:
            logger.info(f"Playing track: '{track_identifier}' via {method}")
            
            if method == 'search':
                # Search and play first result
                search_results = await self.search_music(track_identifier, 'songs')
                
                if search_results:
                    # Try to play first result
                    play_actions = [
                        AutomationAction(
                            ActionType.TAP,
                            {'text': 'Play', 'alternatives': ['▶', 'PLAY']},
                            "Play first search result"
                        ),
                        AutomationAction(
                            ActionType.WAIT,
                            {'duration': 2.0},
                            "Wait for playback to start"
                        )
                    ]
                    
                    sequence = AutomationSequence("play_search_result", play_actions)
                    result = await self.automation_engine.execute_sequence(sequence)
                    
                    if result.success:
                        self.playback_state = 'playing'
                        # Try to detect current track info
                        await self._update_current_track_info()
                        logger.info("✅ Track playback started")
                        return True
                    
            elif method == 'library':
                # Navigate to library and find track
                library_actions = [
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Your Library', 'alternatives': ['Library', 'MY LIBRARY']},
                        "Navigate to library"
                    ),
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Liked Songs', 'alternatives': ['Favorites', 'LIKED SONGS']},
                        "Open liked songs"
                    ),
                    AutomationAction(
                        ActionType.WAIT,
                        {'duration': 2.0},
                        "Wait for library to load"
                    )
                ]
                
                sequence = AutomationSequence("play_from_library", library_actions)
                result = await self.automation_engine.execute_sequence(sequence)
                
                if result.success:
                    # Look for specific track in library
                    found_track = await self._find_track_in_list(track_identifier)
                    if found_track:
                        return await self._tap_play_on_track(found_track)
            
            logger.error("❌ Failed to play track")
            return False
            
        except Exception as e:
            logger.error(f"Track playback failed: {e}")
            return False
    
    async def control_playback(self, action: str) -> bool:
        """
        Control music playback (play, pause, next, previous, shuffle, repeat)
        
        Args:
            action: Playback action ('play', 'pause', 'next', 'previous', 'shuffle', 'repeat')
        """
        try:
            logger.info(f"Controlling playback: {action}")
            
            # Map actions to UI patterns
            action_patterns = {
                'play': self.text_patterns['play_button'],
                'pause': self.text_patterns['pause_button'],
                'next': self.text_patterns['next_track'],
                'previous': self.text_patterns['previous_track'],
                'shuffle': self.text_patterns['shuffle'],
                'repeat': self.text_patterns['repeat']
            }
            
            if action not in action_patterns:
                logger.error(f"Unknown playback action: {action}")
                return False
            
            # Try to find and tap control button
            control_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': action_patterns[action][0], 'alternatives': action_patterns[action][1:]},
                    f"Execute {action} control"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 0.5},
                    "Wait for control response"
                )
            ]
            
            sequence = AutomationSequence(f"playback_{action}", control_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Update playback state
                if action == 'play':
                    self.playback_state = 'playing'
                elif action == 'pause':
                    self.playback_state = 'paused'
                elif action in ['next', 'previous']:
                    await self._update_current_track_info()
                
                logger.info(f"✅ Playback control '{action}' executed")
                return True
            else:
                logger.error(f"❌ Playback control '{action}' failed")
                return False
                
        except Exception as e:
            logger.error(f"Playback control failed: {e}")
            return False
    
    async def create_playlist(self, playlist_name: str, description: str = "") -> bool:
        """Create a new playlist with OCR-driven navigation"""
        try:
            logger.info(f"Creating playlist: '{playlist_name}'")
            
            # Navigate to library and create playlist
            create_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Your Library', 'alternatives': ['Library', 'MY LIBRARY']},
                    "Navigate to library"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for library screen"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Create playlist', 'alternatives': ['+', 'Add', 'NEW PLAYLIST']},
                    "Tap create playlist"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for create dialog"
                ),
                AutomationAction(
                    ActionType.TYPE,
                    {'text': playlist_name},
                    f"Enter playlist name: {playlist_name}"
                )
            ]
            
            # Add description if provided
            if description:
                create_actions.extend([
                    AutomationAction(
                        ActionType.TAP,
                        {'text': 'Description', 'alternatives': ['Add description']},
                        "Tap description field"
                    ),
                    AutomationAction(
                        ActionType.TYPE,
                        {'text': description},
                        f"Enter description: {description}"
                    )
                ])
            
            create_actions.extend([
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Create', 'alternatives': ['Done', 'Save', 'CREATE']},
                    "Confirm playlist creation"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 2.0},
                    "Wait for playlist creation"
                )
            ])
            
            sequence = AutomationSequence("create_playlist", create_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                logger.info(f"✅ Playlist '{playlist_name}' created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create playlist '{playlist_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Playlist creation failed: {e}")
            return False
    
    async def add_to_playlist(self, track_identifier: str, playlist_name: str) -> bool:
        """Add a track to a specific playlist"""
        try:
            logger.info(f"Adding '{track_identifier}' to playlist '{playlist_name}'")
            
            # First find the track
            search_results = await self.search_music(track_identifier, 'songs')
            
            if not search_results:
                logger.error("Track not found for playlist addition")
                return False
            
            # Long press or tap menu on first result
            add_actions = [
                AutomationAction(
                    ActionType.LONG_PRESS,
                    {'text': search_results[0].get('title', track_identifier)},
                    "Long press track for menu"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for context menu"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Add to playlist', 'alternatives': ['Add to', 'PLAYLIST']},
                    "Select add to playlist"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for playlist selection"
                ),
                AutomationAction(
                    ActionType.TAP,
                    {'text': playlist_name},
                    f"Select playlist: {playlist_name}"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for addition confirmation"
                )
            ]
            
            sequence = AutomationSequence("add_to_playlist", add_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                logger.info(f"✅ Track added to playlist '{playlist_name}'")
                return True
            else:
                logger.error(f"❌ Failed to add track to playlist")
                return False
                
        except Exception as e:
            logger.error(f"Add to playlist failed: {e}")
            return False
    
    async def get_now_playing(self) -> Optional[SpotifyTrack]:
        """Get information about currently playing track"""
        try:
            logger.info("Getting now playing information...")
            
            # Try to navigate to now playing screen
            now_playing_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': 'Now playing', 'alternatives': ['Now Playing', 'Player']},
                    "Open now playing screen"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 1.0},
                    "Wait for player screen"
                )
            ]
            
            sequence = AutomationSequence("get_now_playing", now_playing_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                # Parse track information from player screen
                await self._update_current_track_info()
                return self.current_track
            else:
                # Try alternative method - check mini player
                return await self._get_mini_player_info()
                
        except Exception as e:
            logger.error(f"Get now playing failed: {e}")
            return None
    
    async def toggle_like_track(self) -> bool:
        """Toggle like/unlike for current track"""
        try:
            logger.info("Toggling track like status...")
            
            like_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': '♥', 'alternatives': ['❤', 'Like', 'Heart', '🤍']},
                    "Toggle track like status"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 0.5},
                    "Wait for like response"
                )
            ]
            
            sequence = AutomationSequence("toggle_like", like_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                logger.info("✅ Track like status toggled")
                return True
            else:
                logger.error("❌ Failed to toggle like status")
                return False
                
        except Exception as e:
            logger.error(f"Toggle like failed: {e}")
            return False
    
    async def adjust_volume(self, direction: str) -> bool:
        """
        Adjust volume up or down
        
        Args:
            direction: 'up' or 'down'
        """
        try:
            logger.info(f"Adjusting volume {direction}")
            
            # Try to find volume control
            volume_actions = [
                AutomationAction(
                    ActionType.TAP,
                    {'text': '🔊', 'alternatives': ['Volume', 'VOLUME', 'Speaker']},
                    "Open volume control"
                ),
                AutomationAction(
                    ActionType.WAIT,
                    {'duration': 0.5},
                    "Wait for volume slider"
                )
            ]
            
            # Add swipe action for volume adjustment
            if direction == 'up':
                volume_actions.append(
                    AutomationAction(
                        ActionType.SWIPE,
                        {'direction': 'right', 'element': 'volume_slider'},
                        "Swipe volume slider up"
                    )
                )
            else:
                volume_actions.append(
                    AutomationAction(
                        ActionType.SWIPE,
                        {'direction': 'left', 'element': 'volume_slider'},
                        "Swipe volume slider down"
                    )
                )
            
            sequence = AutomationSequence("adjust_volume", volume_actions)
            result = await self.automation_engine.execute_sequence(sequence)
            
            if result.success:
                logger.info(f"✅ Volume adjusted {direction}")
                return True
            else:
                # Try hardware volume buttons as fallback
                return await self._use_hardware_volume(direction)
                
        except Exception as e:
            logger.error(f"Volume adjustment failed: {e}")
            return False
    
    # Helper methods for internal operations
    
    async def _parse_search_results(self) -> List[Dict[str, Any]]:
        """Parse search results from current screen using OCR"""
        try:
            # Capture current screen
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return []
            
            # Detect all text on screen
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            # Parse music-related content
            results = []
            current_item = {}
            
            for detection in detected_texts:
                text = detection['text'].strip()
                
                # Skip UI elements and controls
                if text.lower() in ['play', 'pause', 'next', 'previous', 'search', 'home', 'library']:
                    continue
                
                # Try to identify tracks, artists, albums
                if self._looks_like_track_title(text):
                    if current_item:
                        results.append(current_item)
                    current_item = {'title': text, 'type': 'track'}
                
                elif self._looks_like_artist_name(text) and current_item:
                    current_item['artist'] = text
                
                elif self._looks_like_album_name(text) and current_item:
                    current_item['album'] = text
            
            # Add final item
            if current_item:
                results.append(current_item)
            
            logger.debug(f"Parsed {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Search results parsing failed: {e}")
            return []
    
    async def _update_current_track_info(self):
        """Update current track information from screen"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            # Look for track information in typical player locations
            track_info = {}
            
            for detection in detected_texts:
                text = detection['text'].strip()
                y_pos = detection['bbox'][1]
                
                # Title is usually in the middle area
                if 200 < y_pos < 800 and self._looks_like_track_title(text):
                    track_info['title'] = text
                
                # Artist name is usually below title
                elif 250 < y_pos < 850 and self._looks_like_artist_name(text):
                    track_info['artist'] = text
            
            if track_info:
                self.current_track = SpotifyTrack(
                    title=track_info.get('title', 'Unknown'),
                    artist=track_info.get('artist', 'Unknown'),
                    is_playing=(self.playback_state == 'playing')
                )
                logger.debug(f"Updated track info: {self.current_track.title} by {self.current_track.artist}")
            
        except Exception as e:
            logger.error(f"Track info update failed: {e}")
    
    def _looks_like_track_title(self, text: str) -> bool:
        """Heuristic to identify track titles"""
        # Skip very short or very long texts
        if len(text) < 2 or len(text) > 100:
            return False
        
        # Skip pure numbers or common UI text
        if text.isdigit() or text.lower() in ['home', 'search', 'library', 'premium']:
            return False
        
        # Skip time formats
        if ':' in text and any(c.isdigit() for c in text):
            return False
        
        return True
    
    def _looks_like_artist_name(self, text: str) -> bool:
        """Heuristic to identify artist names"""
        # Similar to track title but may include different patterns
        return self._looks_like_track_title(text)
    
    def _looks_like_album_name(self, text: str) -> bool:
        """Heuristic to identify album names"""
        return self._looks_like_track_title(text)
    
    async def _find_track_in_list(self, track_identifier: str) -> Optional[Dict[str, Any]]:
        """Find a specific track in the current list view"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return None
            
            detected_texts = await self.ocr_engine.detect_text_regions(screenshot)
            
            # Look for matching track
            for detection in detected_texts:
                text = detection['text'].strip()
                if track_identifier.lower() in text.lower():
                    return {
                        'text': text,
                        'position': detection['bbox'],
                        'confidence': detection['confidence']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Track finding failed: {e}")
            return None
    
    async def _tap_play_on_track(self, track_data: Dict[str, Any]) -> bool:
        """Tap play button for a specific track"""
        try:
            # Try to tap on the track or nearby play button
            x, y, w, h = track_data['position']
            
            # Look for play button near the track
            play_position = await self.tap_engine.find_relative_position(
                (x, y, w, h), 'Play', search_radius=100
            )
            
            if play_position:
                success = await self.tap_engine.tap_position(play_position[0], play_position[1])
                if success:
                    self.playback_state = 'playing'
                    return True
            
            # Fallback: tap on track itself
            center_x = x + w // 2
            center_y = y + h // 2
            return await self.tap_engine.tap_position(center_x, center_y)
            
        except Exception as e:
            logger.error(f"Track play tap failed: {e}")
            return False
    
    async def _get_mini_player_info(self) -> Optional[SpotifyTrack]:
        """Get track info from mini player at bottom of screen"""
        try:
            screenshot = await self.screen_capture.capture_screen()
            if not screenshot:
                return None
            
            height = screenshot.height
            
            # Focus on bottom portion where mini player usually is
            bottom_region = screenshot.crop((0, height - 200, screenshot.width, height))
            
            detected_texts = await self.ocr_engine.detect_text_regions(bottom_region)
            
            # Parse mini player info
            track_info = {}
            for detection in detected_texts:
                text = detection['text'].strip()
                
                if self._looks_like_track_title(text) and 'title' not in track_info:
                    track_info['title'] = text
                elif self._looks_like_artist_name(text) and 'artist' not in track_info:
                    track_info['artist'] = text
            
            if track_info:
                return SpotifyTrack(
                    title=track_info.get('title', 'Unknown'),
                    artist=track_info.get('artist', 'Unknown'),
                    is_playing=True  # Assume playing if mini player visible
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Mini player info failed: {e}")
            return None
    
    async def _use_hardware_volume(self, direction: str) -> bool:
        """Use hardware volume buttons as fallback"""
        try:
            # This would require system-level access
            # For now, just log the attempt
            logger.info(f"Would use hardware volume {direction} (not implemented)")
            return False
            
        except Exception as e:
            logger.error(f"Hardware volume failed: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection and status information"""
        return {
            'app_open': self.is_app_open,
            'playback_state': self.playback_state,
            'current_track': {
                'title': self.current_track.title if self.current_track else None,
                'artist': self.current_track.artist if self.current_track else None,
                'is_playing': self.current_track.is_playing if self.current_track else False
            } if self.current_track else None,
            'capabilities': {
                'search': True,
                'playback_control': True,
                'playlist_management': True,
                'volume_control': True,
                'track_info': True
            }
        }


# Example usage
async def demo_spotify_automation():
    """Demonstrate Spotify automation capabilities"""
    try:
        print("🎵 Spotify Automation Demo")
        print("=" * 40)
        
        # Initialize connector
        spotify = SpotifyConnector()
        
        # Open Spotify
        print("1. Opening Spotify...")
        success = await spotify.open_spotify()
        if not success:
            print("❌ Failed to open Spotify")
            return
        
        # Search for music
        print("\n2. Searching for music...")
        results = await spotify.search_music("The Beatles", "artists")
        print(f"Found {len(results)} results")
        
        # Play a track
        print("\n3. Playing track...")
        success = await spotify.play_track("Hey Jude", method='search')
        if success:
            print("✅ Track started playing")
        
        # Get now playing info
        print("\n4. Getting now playing info...")
        track = await spotify.get_now_playing()
        if track:
            print(f"🎵 Now playing: {track.title} by {track.artist}")
        
        # Test playback controls
        print("\n5. Testing playback controls...")
        await asyncio.sleep(2)
        await spotify.control_playback('pause')
        print("⏸ Paused")
        
        await asyncio.sleep(1)
        await spotify.control_playback('play')
        print("▶ Resumed")
        
        # Create playlist demo
        print("\n6. Creating playlist...")
        success = await spotify.create_playlist("AI Demo Playlist", "Created by AI automation")
        if success:
            print("✅ Playlist created")
        
        print("\n🎵 Spotify automation demo completed!")
        
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(demo_spotify_automation())