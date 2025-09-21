"""
AI Mobile AgentX - Dynamic Tap Coordinate System
Intelligent tap coordination with dynamic coordinate calculation from OCR results
Human-like tapping with randomization and safety checks
"""

import asyncio
import logging
import random
import time
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import platform
import subprocess
from abc import ABC, abstractmethod

from .ocr_engine import TextDetection, OCRResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TapMethod(Enum):
    """Available tap execution methods"""
    ADB = "adb"
    ACCESSIBILITY = "accessibility"  
    COORDINATES = "coordinates"
    MOCK = "mock"

@dataclass
class TapCoordinate:
    """Represents a tap coordinate with metadata"""
    x: int
    y: int
    confidence: float
    source_text: str
    method: TapMethod
    timestamp: float
    randomization_applied: bool = False

@dataclass
class TapResult:
    """Result of tap execution"""
    success: bool
    coordinate: TapCoordinate
    execution_time: float
    error_message: Optional[str] = None

class BaseTapExecutor(ABC):
    """Abstract base class for tap execution methods"""
    
    @abstractmethod
    async def execute_tap(self, x: int, y: int) -> bool:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        pass

class ADBTapExecutor(BaseTapExecutor):
    """ADB-based tap execution for Android devices"""
    
    def __init__(self):
        self.method_name = "ADB"
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if ADB is available and device is connected"""
        try:
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, text=True, timeout=5)
            self.available = result.returncode == 0 and 'device' in result.stdout
            if self.available:
                logger.info("ADB tap executor initialized successfully")
            else:
                logger.warning("ADB not available or no device connected")
        except Exception as e:
            logger.error(f"ADB availability check failed: {e}")
            self.available = False
        return self.available
    
    async def execute_tap(self, x: int, y: int) -> bool:
        """Execute tap using ADB input tap command"""
        if not self.available:
            return False
        
        try:
            process = await asyncio.create_subprocess_exec(
                'adb', 'shell', 'input', 'tap', str(x), str(y),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            success = process.returncode == 0
            
            if success:
                logger.debug(f"ADB tap executed at ({x}, {y})")
            else:
                logger.error(f"ADB tap failed: {stderr.decode()}")
            
            return success
            
        except Exception as e:
            logger.error(f"ADB tap execution failed: {e}")
            return False
    
    def is_available(self) -> bool:
        return self.available
    
    def get_method_name(self) -> str:
        return self.method_name

class MockTapExecutor(BaseTapExecutor):
    """Mock tap executor for testing and simulation"""
    
    def __init__(self):
        self.method_name = "Mock"
        self.available = True
        self.tap_history = []
    
    async def execute_tap(self, x: int, y: int) -> bool:
        """Simulate tap execution"""
        # Simulate execution delay
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        self.tap_history.append({
            'x': x, 'y': y, 
            'timestamp': time.time()
        })
        
        logger.info(f"MOCK TAP executed at ({x}, {y})")
        return True
    
    def is_available(self) -> bool:
        return self.available
    
    def get_method_name(self) -> str:
        return self.method_name
    
    def get_tap_history(self) -> List[Dict]:
        """Get history of executed taps"""
        return self.tap_history.copy()

class AccessibilityTapExecutor(BaseTapExecutor):
    """Accessibility service-based tap execution (Android/iOS)"""
    
    def __init__(self):
        self.method_name = "Accessibility"
        self.available = False  # Would be set based on accessibility service availability
        logger.info("Accessibility tap executor initialized (not implemented)")
    
    async def execute_tap(self, x: int, y: int) -> bool:
        """Execute tap using accessibility services"""
        # This would integrate with platform-specific accessibility APIs
        logger.warning("Accessibility tap not implemented")
        return False
    
    def is_available(self) -> bool:
        return self.available
    
    def get_method_name(self) -> str:
        return self.method_name

class TapCoordinateEngine:
    """
    Main engine for calculating and executing dynamic tap coordinates
    Integrates with OCR results to provide intelligent tapping
    """
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.executors = {}
        self.active_executor = None
        
        # Initialize available executors
        self._initialize_executors()
        
        # Tap configuration
        self.randomization_enabled = True
        self.randomization_radius = 5  # pixels
        self.min_tap_interval = 0.5  # seconds
        self.max_tap_interval = 2.0  # seconds
        self.last_tap_time = 0
        
        # Safety bounds (percentage of screen)
        self.safe_bounds = {
            'left': 0.05,   # 5% from left edge
            'right': 0.95,  # 5% from right edge  
            'top': 0.1,     # 10% from top (status bar)
            'bottom': 0.9   # 10% from bottom (navigation)
        }
        
        logger.info(f"Tap coordinate engine initialized (test_mode: {test_mode})")
    
    def _initialize_executors(self):
        """Initialize available tap execution methods"""
        # Always add mock executor
        mock_executor = MockTapExecutor()
        self.executors[TapMethod.MOCK] = mock_executor
        self.active_executor = mock_executor
        
        # Add ADB executor if available
        adb_executor = ADBTapExecutor()
        if adb_executor.is_available():
            self.executors[TapMethod.ADB] = adb_executor
            if not self.test_mode:
                self.active_executor = adb_executor
        
        # Add accessibility executor (placeholder)
        acc_executor = AccessibilityTapExecutor()
        self.executors[TapMethod.ACCESSIBILITY] = acc_executor
        
        logger.info(f"Initialized {len(self.executors)} tap executors")
        logger.info(f"Active executor: {self.active_executor.get_method_name()}")
    
    def calculate_tap_coordinate(self, detection: TextDetection, 
                               screen_dimensions: Tuple[int, int]) -> TapCoordinate:
        """
        Calculate optimal tap coordinate from text detection
        
        Args:
            detection: OCR text detection result
            screen_dimensions: Screen width and height
            
        Returns:
            TapCoordinate with calculated position
        """
        # Start with center point of detected text
        base_x, base_y = detection.center_point
        
        # Apply randomization if enabled
        if self.randomization_enabled:
            offset_x = random.randint(-self.randomization_radius, self.randomization_radius)
            offset_y = random.randint(-self.randomization_radius, self.randomization_radius)
            tap_x = base_x + offset_x
            tap_y = base_y + offset_y
            randomization_applied = True
        else:
            tap_x, tap_y = base_x, base_y
            randomization_applied = False
        
        # Apply safety bounds
        screen_width, screen_height = screen_dimensions
        safe_x = max(
            int(screen_width * self.safe_bounds['left']),
            min(tap_x, int(screen_width * self.safe_bounds['right']))
        )
        safe_y = max(
            int(screen_height * self.safe_bounds['top']),
            min(tap_y, int(screen_height * self.safe_bounds['bottom']))
        )
        
        coordinate = TapCoordinate(
            x=safe_x,
            y=safe_y,
            confidence=detection.confidence,
            source_text=detection.text,
            method=TapMethod(self.active_executor.get_method_name().lower()),
            timestamp=time.time(),
            randomization_applied=randomization_applied
        )
        
        logger.debug(f"Calculated tap coordinate: ({safe_x}, {safe_y}) for '{detection.text}'")
        return coordinate
    
    async def tap_text(self, ocr_result: OCRResult, target_text: str, 
                      screen_dimensions: Tuple[int, int], fuzzy: bool = True) -> TapResult:
        """
        Find and tap specific text on screen
        
        Args:
            ocr_result: OCR analysis result
            target_text: Text to find and tap
            screen_dimensions: Screen dimensions
            fuzzy: Enable fuzzy text matching
            
        Returns:
            TapResult with execution details
        """
        # Find matching text detections
        from .ocr_engine import OCRDetectionEngine
        ocr_engine = OCRDetectionEngine()
        matches = ocr_engine.find_text(ocr_result, target_text, fuzzy)
        
        if not matches:
            return TapResult(
                success=False,
                coordinate=None,
                execution_time=0,
                error_message=f"Text '{target_text}' not found"
            )
        
        # Use best match (highest confidence)
        best_match = max(matches, key=lambda x: x.confidence)
        
        # Calculate tap coordinate
        coordinate = self.calculate_tap_coordinate(best_match, screen_dimensions)
        
        # Execute tap with timing control
        result = await self._execute_tap_with_timing(coordinate)
        return result
    
    async def tap_coordinate(self, x: int, y: int, screen_dimensions: Tuple[int, int]) -> TapResult:
        """
        Tap at specific coordinate with safety checks
        
        Args:
            x, y: Target coordinates
            screen_dimensions: Screen dimensions for bounds checking
            
        Returns:
            TapResult with execution details
        """
        # Create coordinate object
        coordinate = TapCoordinate(
            x=x, y=y,
            confidence=1.0,
            source_text="manual_coordinate",
            method=TapMethod(self.active_executor.get_method_name().lower()),
            timestamp=time.time(),
            randomization_applied=False
        )
        
        # Apply safety bounds
        screen_width, screen_height = screen_dimensions
        coordinate.x = max(
            int(screen_width * self.safe_bounds['left']),
            min(coordinate.x, int(screen_width * self.safe_bounds['right']))
        )
        coordinate.y = max(
            int(screen_height * self.safe_bounds['top']),
            min(coordinate.y, int(screen_height * self.safe_bounds['bottom']))
        )
        
        # Execute tap
        result = await self._execute_tap_with_timing(coordinate)
        return result
    
    async def _execute_tap_with_timing(self, coordinate: TapCoordinate) -> TapResult:
        """Execute tap with human-like timing and safety checks"""
        start_time = time.time()
        
        # Respect minimum tap interval
        current_time = time.time()
        time_since_last = current_time - self.last_tap_time
        if time_since_last < self.min_tap_interval:
            wait_time = self.min_tap_interval - time_since_last
            logger.debug(f"Waiting {wait_time:.2f}s before next tap")
            await asyncio.sleep(wait_time)
        
        # Add random delay for human-like behavior
        if self.randomization_enabled:
            random_delay = random.uniform(0.1, 0.5)
            await asyncio.sleep(random_delay)
        
        # Execute the tap
        try:
            success = await self.active_executor.execute_tap(coordinate.x, coordinate.y)
            execution_time = time.time() - start_time
            self.last_tap_time = time.time()
            
            result = TapResult(
                success=success,
                coordinate=coordinate,
                execution_time=execution_time,
                error_message=None if success else "Tap execution failed"
            )
            
            if success:
                logger.info(f"Tap successful at ({coordinate.x}, {coordinate.y}) in {execution_time:.2f}s")
            else:
                logger.error(f"Tap failed at ({coordinate.x}, {coordinate.y})")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tap execution error: {e}")
            
            return TapResult(
                success=False,
                coordinate=coordinate,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def switch_executor(self, method: TapMethod) -> bool:
        """Switch to different tap execution method"""
        if method in self.executors and self.executors[method].is_available():
            self.active_executor = self.executors[method]
            logger.info(f"Switched to {method.value} tap executor")
            return True
        else:
            logger.warning(f"Tap executor {method.value} not available")
            return False
    
    def get_available_methods(self) -> List[TapMethod]:
        """Get list of available tap methods"""
        return [method for method, executor in self.executors.items() 
                if executor.is_available()]
    
    def configure_randomization(self, enabled: bool, radius: int = 5):
        """Configure tap randomization settings"""
        self.randomization_enabled = enabled
        self.randomization_radius = radius
        logger.info(f"Tap randomization: {enabled} (radius: {radius}px)")
    
    def configure_timing(self, min_interval: float, max_interval: float):
        """Configure tap timing intervals"""
        self.min_tap_interval = min_interval
        self.max_tap_interval = max_interval
        logger.info(f"Tap timing: {min_interval}s - {max_interval}s")
    
    def configure_safety_bounds(self, left: float, right: float, top: float, bottom: float):
        """Configure safety bounds as percentages of screen"""
        self.safe_bounds = {
            'left': left, 'right': right,
            'top': top, 'bottom': bottom
        }
        logger.info(f"Safety bounds updated: {self.safe_bounds}")


# Example usage and testing
async def main():
    """Test the tap coordinate system"""
    try:
        # Initialize tap engine
        tap_engine = TapCoordinateEngine(test_mode=True)
        print(f"Available methods: {[m.value for m in tap_engine.get_available_methods()]}")
        
        # Test coordinate calculation
        from .ocr_engine import TextDetection
        
        # Mock text detection
        detection = TextDetection(
            text="Click Here",
            confidence=0.95,
            bounding_box=(100, 200, 80, 40),
            center_point=(140, 220),
            detection_time=0.1,
            detection_method="Mock"
        )
        
        screen_dims = (1080, 1920)
        coordinate = tap_engine.calculate_tap_coordinate(detection, screen_dims)
        print(f"Calculated coordinate: ({coordinate.x}, {coordinate.y})")
        
        # Test tap execution
        result = await tap_engine.tap_coordinate(coordinate.x, coordinate.y, screen_dims)
        print(f"Tap result: success={result.success}, time={result.execution_time:.2f}s")
        
        # Test mock executor history
        if isinstance(tap_engine.active_executor, MockTapExecutor):
            history = tap_engine.active_executor.get_tap_history()
            print(f"Tap history: {len(history)} taps executed")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())