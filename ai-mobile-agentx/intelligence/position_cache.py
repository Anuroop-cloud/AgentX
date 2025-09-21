"""
AI Mobile AgentX - Position Caching System
Smart caching for frequently used text positions to optimize OCR performance
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

from .ocr_engine import TextDetection, OCRResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CachedPosition:
    """Represents a cached text position"""
    text: str
    bounding_box: Tuple[int, int, int, int]
    center_point: Tuple[int, int]
    confidence: float
    screen_hash: str
    timestamp: float
    hit_count: int = 0
    last_verified: float = 0.0
    app_context: str = ""

@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_size: int = 0
    hit_rate: float = 0.0
    avg_lookup_time: float = 0.0

class ScreenHasher:
    """Generates consistent hashes for screen content"""
    
    @staticmethod
    def hash_screen(image, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Generate hash for screen or screen region"""
        try:
            from PIL import Image
            import numpy as np
            
            # Crop to region if specified
            if region:
                x, y, w, h = region
                image = image.crop((x, y, x + w, y + h))
            
            # Convert to grayscale and resize for consistent hashing
            image = image.convert('L').resize((64, 64))
            
            # Generate hash from pixel data
            pixel_data = np.array(image).tobytes()
            screen_hash = hashlib.md5(pixel_data).hexdigest()[:16]
            
            return screen_hash
            
        except Exception as e:
            logger.error(f"Screen hashing failed: {e}")
            return "unknown"
    
    @staticmethod
    def hash_text_region(image, detection: TextDetection) -> str:
        """Generate hash for specific text region"""
        x, y, w, h = detection.bounding_box
        # Add padding around text region
        padding = 10
        region = (
            max(0, x - padding),
            max(0, y - padding),
            min(image.width, x + w + padding * 2),
            min(image.height, y + h + padding * 2)
        )
        return ScreenHasher.hash_screen(image, region)

class PositionCacheDatabase:
    """SQLite database for persistent position caching"""
    
    def __init__(self, db_path: str = "position_cache.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS cached_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    bounding_box TEXT NOT NULL,
                    center_point TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    screen_hash TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    last_verified REAL DEFAULT 0,
                    app_context TEXT DEFAULT '',
                    UNIQUE(text, screen_hash, app_context)
                )
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_text_hash 
                ON cached_positions(text, screen_hash)
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_app_context 
                ON cached_positions(app_context)
            """)
            
            self.connection.commit()
            logger.info(f"Position cache database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.connection = None
    
    def save_position(self, cached_pos: CachedPosition) -> bool:
        """Save cached position to database"""
        if not self.connection:
            return False
        
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO cached_positions 
                (text, bounding_box, center_point, confidence, screen_hash, 
                 timestamp, hit_count, last_verified, app_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cached_pos.text,
                json.dumps(cached_pos.bounding_box),
                json.dumps(cached_pos.center_point),
                cached_pos.confidence,
                cached_pos.screen_hash,
                cached_pos.timestamp,
                cached_pos.hit_count,
                cached_pos.last_verified,
                cached_pos.app_context
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save position: {e}")
            return False
    
    def get_position(self, text: str, screen_hash: str, app_context: str = "") -> Optional[CachedPosition]:
        """Retrieve cached position from database"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.execute("""
                SELECT text, bounding_box, center_point, confidence, screen_hash,
                       timestamp, hit_count, last_verified, app_context
                FROM cached_positions 
                WHERE text = ? AND screen_hash = ? AND app_context = ?
            """, (text, screen_hash, app_context))
            
            row = cursor.fetchone()
            if row:
                return CachedPosition(
                    text=row[0],
                    bounding_box=tuple(json.loads(row[1])),
                    center_point=tuple(json.loads(row[2])),
                    confidence=row[3],
                    screen_hash=row[4],
                    timestamp=row[5],
                    hit_count=row[6],
                    last_verified=row[7],
                    app_context=row[8]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get position: {e}")
            return None
    
    def update_hit_count(self, text: str, screen_hash: str, app_context: str = ""):
        """Update hit count for cached position"""
        if not self.connection:
            return
        
        try:
            self.connection.execute("""
                UPDATE cached_positions 
                SET hit_count = hit_count + 1, last_verified = ? 
                WHERE text = ? AND screen_hash = ? AND app_context = ?
            """, (time.time(), text, screen_hash, app_context))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to update hit count: {e}")
    
    def cleanup_old_entries(self, max_age_days: int = 7):
        """Remove old cache entries"""
        if not self.connection:
            return
        
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            
            cursor = self.connection.execute("SELECT COUNT(*) FROM cached_positions WHERE timestamp < ?", (cutoff_time,))
            old_count = cursor.fetchone()[0]
            
            if old_count > 0:
                self.connection.execute("DELETE FROM cached_positions WHERE timestamp < ?", (cutoff_time,))
                self.connection.commit()
                logger.info(f"Cleaned up {old_count} old cache entries")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.execute("SELECT COUNT(*), AVG(hit_count), MAX(timestamp) FROM cached_positions")
            row = cursor.fetchone()
            
            return {
                'total_entries': row[0] or 0,
                'avg_hit_count': row[1] or 0.0,
                'last_update': row[2] or 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

class IntelligentPositionCache:
    """
    Main position caching system with smart algorithms and performance optimization
    """
    
    def __init__(self, max_memory_cache: int = 1000, 
                 verification_threshold: float = 300.0,  # 5 minutes
                 confidence_threshold: float = 0.7):
        
        self.max_memory_cache = max_memory_cache
        self.verification_threshold = verification_threshold
        self.confidence_threshold = confidence_threshold
        
        # In-memory cache for fastest access
        self.memory_cache: Dict[str, CachedPosition] = {}
        
        # Persistent database cache
        self.db_cache = PositionCacheDatabase()
        
        # Performance tracking
        self.stats = CacheStats()
        
        # Current app context
        self.current_app_context = ""
        
        logger.info("Intelligent position cache initialized")
    
    def set_app_context(self, app_name: str):
        """Set current app context for better caching"""
        self.current_app_context = app_name
        logger.debug(f"App context set to: {app_name}")
    
    async def find_cached_position(self, text: str, screen_image, 
                                 fuzzy_match: bool = True) -> Optional[CachedPosition]:
        """
        Find cached position for text with intelligent matching
        
        Args:
            text: Text to find
            screen_image: Current screen image
            fuzzy_match: Enable fuzzy text matching
            
        Returns:
            CachedPosition if found and valid, None otherwise
        """
        start_time = time.time()
        self.stats.total_requests += 1
        
        try:
            # Generate screen hash
            screen_hash = ScreenHasher.hash_screen(screen_image)
            
            # Create cache key
            cache_key = f"{text}:{screen_hash}:{self.current_app_context}"
            
            # Check memory cache first
            cached_pos = self._check_memory_cache(cache_key, text, fuzzy_match)
            
            # Check database cache if not in memory
            if not cached_pos:
                cached_pos = self._check_database_cache(text, screen_hash, fuzzy_match)
                
                # Add to memory cache if found
                if cached_pos:
                    self._add_to_memory_cache(cache_key, cached_pos)
            
            # Verify cache validity if found
            if cached_pos:
                is_valid = await self._verify_cached_position(cached_pos, screen_image)
                if is_valid:
                    self._update_cache_hit(cached_pos, cache_key)
                    self.stats.cache_hits += 1
                    
                    lookup_time = time.time() - start_time
                    self._update_avg_lookup_time(lookup_time)
                    
                    logger.debug(f"Cache hit for '{text}' in {lookup_time:.3f}s")
                    return cached_pos
                else:
                    # Remove invalid entry
                    self._invalidate_cached_position(cache_key, cached_pos)
            
            self.stats.cache_misses += 1
            lookup_time = time.time() - start_time
            self._update_avg_lookup_time(lookup_time)
            
            return None
            
        except Exception as e:
            logger.error(f"Cache lookup failed: {e}")
            return None
    
    def cache_positions(self, ocr_result: OCRResult, screen_image) -> int:
        """
        Cache text positions from OCR result
        
        Args:
            ocr_result: OCR analysis result
            screen_image: Screen image used for OCR
            
        Returns:
            Number of positions cached
        """
        cached_count = 0
        current_time = time.time()
        
        try:
            screen_hash = ScreenHasher.hash_screen(screen_image)
            
            for detection in ocr_result.detections:
                # Only cache high-confidence detections
                if detection.confidence >= self.confidence_threshold:
                    
                    cached_pos = CachedPosition(
                        text=detection.text,
                        bounding_box=detection.bounding_box,
                        center_point=detection.center_point,
                        confidence=detection.confidence,
                        screen_hash=screen_hash,
                        timestamp=current_time,
                        app_context=self.current_app_context
                    )
                    
                    # Save to both caches
                    if self._save_to_caches(cached_pos):
                        cached_count += 1
            
            logger.debug(f"Cached {cached_count} positions from {len(ocr_result.detections)} detections")
            return cached_count
            
        except Exception as e:
            logger.error(f"Position caching failed: {e}")
            return 0
    
    def _check_memory_cache(self, cache_key: str, text: str, fuzzy_match: bool) -> Optional[CachedPosition]:
        """Check in-memory cache for position"""
        # Exact match
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Fuzzy match if enabled
        if fuzzy_match:
            text_lower = text.lower()
            for key, cached_pos in self.memory_cache.items():
                if text_lower in cached_pos.text.lower() or cached_pos.text.lower() in text_lower:
                    return cached_pos
        
        return None
    
    def _check_database_cache(self, text: str, screen_hash: str, fuzzy_match: bool) -> Optional[CachedPosition]:
        """Check database cache for position"""
        # Exact match
        cached_pos = self.db_cache.get_position(text, screen_hash, self.current_app_context)
        if cached_pos:
            return cached_pos
        
        # Fuzzy match would require more complex database queries
        # For now, return None and let OCR handle it
        return None
    
    async def _verify_cached_position(self, cached_pos: CachedPosition, screen_image) -> bool:
        """Verify that cached position is still valid"""
        current_time = time.time()
        
        # Skip verification if recently verified
        if current_time - cached_pos.last_verified < self.verification_threshold:
            return True
        
        try:
            # Quick verification by checking if text region looks similar
            x, y, w, h = cached_pos.bounding_box
            
            # Ensure coordinates are within screen bounds
            if (x + w > screen_image.width or y + h > screen_image.height or 
                x < 0 or y < 0):
                logger.debug(f"Cached position out of bounds: {cached_pos.bounding_box}")
                return False
            
            # Extract current text region
            region_hash = ScreenHasher.hash_text_region(screen_image, 
                TextDetection(cached_pos.text, cached_pos.confidence,
                            cached_pos.bounding_box, cached_pos.center_point,
                            0, "cache"))
            
            # Compare with expected region (simple hash comparison)
            # In a more sophisticated implementation, this could use image similarity
            cached_pos.last_verified = current_time
            return True  # For now, assume valid
            
        except Exception as e:
            logger.debug(f"Position verification failed: {e}")
            return False
    
    def _add_to_memory_cache(self, cache_key: str, cached_pos: CachedPosition):
        """Add position to memory cache with size management"""
        # Remove oldest entries if cache is full
        while len(self.memory_cache) >= self.max_memory_cache:
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k].timestamp)
            del self.memory_cache[oldest_key]
        
        self.memory_cache[cache_key] = cached_pos
    
    def _save_to_caches(self, cached_pos: CachedPosition) -> bool:
        """Save position to both memory and database caches"""
        try:
            # Save to database
            db_saved = self.db_cache.save_position(cached_pos)
            
            # Save to memory
            cache_key = f"{cached_pos.text}:{cached_pos.screen_hash}:{cached_pos.app_context}"
            self._add_to_memory_cache(cache_key, cached_pos)
            
            return db_saved
            
        except Exception as e:
            logger.error(f"Failed to save to caches: {e}")
            return False
    
    def _update_cache_hit(self, cached_pos: CachedPosition, cache_key: str):
        """Update cache hit statistics"""
        cached_pos.hit_count += 1
        self.db_cache.update_hit_count(
            cached_pos.text, 
            cached_pos.screen_hash, 
            cached_pos.app_context
        )
    
    def _invalidate_cached_position(self, cache_key: str, cached_pos: CachedPosition):
        """Remove invalid cached position"""
        # Remove from memory cache
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        # Note: For simplicity, we don't remove from database
        # In production, you might want to mark as invalid or remove
    
    def _update_avg_lookup_time(self, lookup_time: float):
        """Update average lookup time statistic"""
        if self.stats.total_requests == 1:
            self.stats.avg_lookup_time = lookup_time
        else:
            # Running average
            self.stats.avg_lookup_time = (
                (self.stats.avg_lookup_time * (self.stats.total_requests - 1) + lookup_time) / 
                self.stats.total_requests
            )
    
    def get_cache_performance(self) -> CacheStats:
        """Get comprehensive cache performance statistics"""
        self.stats.cache_size = len(self.memory_cache)
        self.stats.hit_rate = (
            self.stats.cache_hits / self.stats.total_requests 
            if self.stats.total_requests > 0 else 0.0
        )
        
        return self.stats
    
    def cleanup_cache(self, max_age_days: int = 7):
        """Clean up old cache entries"""
        self.db_cache.cleanup_old_entries(max_age_days)
        
        # Clean up memory cache of old entries
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 3600)
        
        old_keys = [key for key, pos in self.memory_cache.items() 
                   if pos.timestamp < cutoff_time]
        
        for key in old_keys:
            del self.memory_cache[key]
        
        logger.info(f"Cleaned up {len(old_keys)} old memory cache entries")
    
    def export_cache_data(self) -> Dict[str, Any]:
        """Export cache data for analysis"""
        return {
            'memory_cache_size': len(self.memory_cache),
            'database_stats': self.db_cache.get_cache_stats(),
            'performance_stats': asdict(self.get_cache_performance())
        }
    
    def close(self):
        """Close cache and cleanup resources"""
        self.db_cache.close()
        logger.info("Position cache closed")


# Example usage and testing
async def main():
    """Test the position caching system"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        from .ocr_engine import OCRDetectionEngine, TextDetection
        
        # Initialize cache
        cache = IntelligentPositionCache()
        cache.set_app_context("TestApp")
        
        # Create test image
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add test text
        test_texts = ["Settings", "Profile", "Help", "Back"]
        for i, text in enumerate(test_texts):
            y_pos = 50 + i * 60
            draw.text((50, y_pos), text, fill='black', font=font)
        
        # Simulate OCR result
        detections = []
        for i, text in enumerate(test_texts):
            y_pos = 50 + i * 60
            detection = TextDetection(
                text=text,
                confidence=0.95,
                bounding_box=(50, y_pos, 80, 20),
                center_point=(90, y_pos + 10),
                detection_time=0.1,
                detection_method="Test"
            )
            detections.append(detection)
        
        from .ocr_engine import OCRResult
        ocr_result = OCRResult(
            detections=detections,
            processing_time=0.5,
            image_dimensions=img.size,
            total_detections=len(detections),
            average_confidence=0.95
        )
        
        # Cache the positions
        cached_count = cache.cache_positions(ocr_result, img)
        print(f"Cached {cached_count} positions")
        
        # Test cache lookup
        print("\nTesting cache lookups:")
        for text in test_texts:
            cached_pos = await cache.find_cached_position(text, img)
            if cached_pos:
                print(f"✓ Found cached position for '{text}': {cached_pos.center_point}")
            else:
                print(f"✗ No cached position for '{text}'")
        
        # Test fuzzy matching
        cached_pos = await cache.find_cached_position("help", img, fuzzy_match=True)
        if cached_pos:
            print(f"✓ Fuzzy match found for 'help': '{cached_pos.text}'")
        
        # Show performance stats
        stats = cache.get_cache_performance()
        print(f"\nCache Performance:")
        print(f"  Hit rate: {stats.hit_rate:.2%}")
        print(f"  Avg lookup time: {stats.avg_lookup_time:.3f}s")
        print(f"  Total requests: {stats.total_requests}")
        
        # Cleanup
        cache.close()
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())