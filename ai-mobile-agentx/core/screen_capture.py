"""
AI Mobile AgentX - Reformed Architecture
Core screen capture system for dynamic mobile automation
"""

import asyncio
import logging
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import numpy as np
from datetime import datetime, timedelta
import platform
import subprocess
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenCaptureEngine:
    """
    Dynamic mobile screen capture system with cross-platform support
    Optimized for mobile performance and battery efficiency
    """
    
    def __init__(self, optimize_for_mobile: bool = True):
        self.optimize_for_mobile = optimize_for_mobile
        self.last_capture_time = None
        self.capture_cooldown = timedelta(milliseconds=100)  # Prevent excessive captures
        self.screen_dimensions = None
        self.device_info = self._detect_device()
        
        # Performance optimization settings
        self.max_resolution = (1080, 1920) if optimize_for_mobile else None
        self.compression_quality = 85  # Balance quality vs performance
        
        logger.info(f"Screen capture engine initialized for {self.device_info['platform']}")
    
    def _detect_device(self) -> Dict[str, Any]:
        """Detect device platform and capabilities"""
        platform_info = {
            'platform': platform.system().lower(),
            'architecture': platform.machine(),
            'is_mobile': False
        }
        
        # Detect mobile platforms
        if platform_info['platform'] in ['android', 'ios']:
            platform_info['is_mobile'] = True
        elif 'arm' in platform_info['architecture'].lower():
            platform_info['is_mobile'] = True  # ARM often indicates mobile
            
        return platform_info
    
    async def capture_screen(self, force: bool = False) -> Optional[Image.Image]:
        """
        Capture current screen with intelligent throttling
        
        Args:
            force: Bypass throttling if True
            
        Returns:
            PIL Image or None if throttled
        """
        # Throttling to prevent excessive captures
        if not force and self.last_capture_time:
            time_since_last = datetime.now() - self.last_capture_time
            if time_since_last < self.capture_cooldown:
                logger.debug("Screen capture throttled")
                return None
        
        try:
            # Platform-specific capture logic
            if self.device_info['platform'] == 'android':
                image = await self._capture_android()
            elif self.device_info['platform'] == 'ios':
                image = await self._capture_ios()
            else:
                image = await self._capture_desktop()
            
            if image:
                image = self._optimize_image(image)
                self.last_capture_time = datetime.now()
                self._update_screen_dimensions(image)
                
            return image
            
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    async def _capture_android(self) -> Optional[Image.Image]:
        """Android-specific screen capture using ADB"""
        try:
            # Use ADB screencap for Android
            process = await asyncio.create_subprocess_exec(
                'adb', 'exec-out', 'screencap', '-p',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                image = Image.open(io.BytesIO(stdout))
                logger.debug("Android screen captured successfully")
                return image
            else:
                logger.error(f"ADB screencap failed: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Android capture error: {e}")
            return None
    
    async def _capture_ios(self) -> Optional[Image.Image]:
        """iOS-specific screen capture using iOS tools"""
        try:
            # Use iOS-specific tools or fall back to desktop capture
            # This would typically require specialized iOS automation tools
            logger.warning("iOS capture not fully implemented - using fallback")
            return await self._capture_desktop()
            
        except Exception as e:
            logger.error(f"iOS capture error: {e}")
            return None
    
    async def _capture_desktop(self) -> Optional[Image.Image]:
        """Desktop/emulator screen capture using cross-platform methods"""
        try:
            # Use PIL ImageGrab for desktop environments
            from PIL import ImageGrab
            
            image = ImageGrab.grab()
            logger.debug("Desktop screen captured successfully")
            return image
            
        except Exception as e:
            logger.error(f"Desktop capture error: {e}")
            return None
    
    def _optimize_image(self, image: Image.Image) -> Image.Image:
        """Optimize captured image for mobile performance"""
        if not self.optimize_for_mobile:
            return image
        
        # Resize if too large
        if self.max_resolution:
            width, height = image.size
            max_width, max_height = self.max_resolution
            
            if width > max_width or height > max_height:
                # Calculate scaling factor maintaining aspect ratio
                scale = min(max_width / width, max_height / height)
                new_size = (int(width * scale), int(height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Image resized to {new_size} for performance")
        
        # Convert to RGB if needed (removes alpha channel)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def _update_screen_dimensions(self, image: Image.Image):
        """Update cached screen dimensions"""
        self.screen_dimensions = image.size
        logger.debug(f"Screen dimensions updated: {self.screen_dimensions}")
    
    def get_screen_dimensions(self) -> Optional[Tuple[int, int]]:
        """Get current screen dimensions"""
        return self.screen_dimensions
    
    async def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """
        Capture specific screen region for targeted analysis
        
        Args:
            x, y: Top-left corner coordinates
            width, height: Region dimensions
            
        Returns:
            Cropped PIL Image or None
        """
        full_image = await self.capture_screen()
        if not full_image:
            return None
        
        try:
            # Ensure coordinates are within bounds
            img_width, img_height = full_image.size
            x = max(0, min(x, img_width))
            y = max(0, min(y, img_height))
            width = min(width, img_width - x)
            height = min(height, img_height - y)
            
            region = full_image.crop((x, y, x + width, y + height))
            logger.debug(f"Captured region: ({x}, {y}, {width}, {height})")
            return region
            
        except Exception as e:
            logger.error(f"Region capture failed: {e}")
            return None
    
    def save_capture(self, image: Image.Image, filename: str) -> bool:
        """Save captured image to file"""
        try:
            image.save(filename, quality=self.compression_quality, optimize=True)
            logger.info(f"Screen capture saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save capture: {e}")
            return False
    
    def to_base64(self, image: Image.Image) -> str:
        """Convert image to base64 for API transmission"""
        try:
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=self.compression_quality)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
        except Exception as e:
            logger.error(f"Base64 conversion failed: {e}")
            return ""


class ScreenCaptureManager:
    """
    High-level manager for screen capture operations
    Handles multiple capture engines and intelligent switching
    """
    
    def __init__(self):
        self.primary_engine = ScreenCaptureEngine(optimize_for_mobile=True)
        self.fallback_engine = ScreenCaptureEngine(optimize_for_mobile=False)
        self.current_engine = self.primary_engine
        
    async def capture(self, force: bool = False) -> Optional[Image.Image]:
        """Capture screen with automatic fallback"""
        image = await self.current_engine.capture_screen(force)
        
        # Try fallback if primary fails
        if not image and self.current_engine == self.primary_engine:
            logger.warning("Primary capture failed, trying fallback")
            image = await self.fallback_engine.capture_screen(force)
            if image:
                self.current_engine = self.fallback_engine
        
        return image
    
    async def capture_with_retry(self, max_retries: int = 3) -> Optional[Image.Image]:
        """Capture screen with retry logic"""
        for attempt in range(max_retries):
            image = await self.capture(force=attempt > 0)
            if image:
                return image
            
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # Brief delay between retries
                
        logger.error("Screen capture failed after all retries")
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get current capture engine capabilities"""
        return {
            'platform': self.current_engine.device_info['platform'],
            'is_mobile': self.current_engine.device_info['is_mobile'],
            'max_resolution': self.current_engine.max_resolution,
            'screen_dimensions': self.current_engine.get_screen_dimensions()
        }


# Example usage and testing
async def main():
    """Test the screen capture system"""
    manager = ScreenCaptureManager()
    
    print("Testing screen capture system...")
    print(f"Capabilities: {manager.get_capabilities()}")
    
    # Test basic capture
    image = await manager.capture_with_retry()
    if image:
        print(f"Screen captured successfully: {image.size}")
        
        # Save test capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_capture_{timestamp}.jpg"
        manager.current_engine.save_capture(image, filename)
        
        # Test region capture
        region = await manager.current_engine.capture_region(0, 0, 200, 200)
        if region:
            print(f"Region captured: {region.size}")
    else:
        print("Screen capture failed")


if __name__ == "__main__":
    asyncio.run(main())