"""
AI Mobile AgentX - Intelligent Automation Engine
Advanced automation with looping, conditional logic, and human-like behavior
"""

import asyncio
import logging
import random
import time
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json

from .screen_capture import ScreenCaptureManager
from .ocr_engine import OCRDetectionEngine, OCRResult, TextDetection
from .tap_coordinator import TapCoordinateEngine, TapResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of automation actions"""
    TAP = "tap"
    WAIT = "wait"
    FIND_TEXT = "find_text"
    SCROLL = "scroll"
    SWIPE = "swipe"
    VERIFY = "verify"
    LOOP = "loop"
    CONDITION = "condition"

class ConditionType(Enum):
    """Types of conditional checks"""
    TEXT_EXISTS = "text_exists"
    TEXT_NOT_EXISTS = "text_not_exists"
    SCREEN_CONTAINS = "screen_contains"
    CUSTOM = "custom"

@dataclass
class AutomationAction:
    """Represents a single automation action"""
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    timeout: float = 10.0
    description: str = ""
    condition: Optional['AutomationCondition'] = None

@dataclass
class AutomationCondition:
    """Represents a conditional check"""
    condition_type: ConditionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    negate: bool = False

@dataclass
class AutomationResult:
    """Result of automation execution"""
    success: bool
    action: AutomationAction
    execution_time: float
    attempts: int
    error_message: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)

class AutomationSequence:
    """Represents a sequence of automation actions"""
    
    def __init__(self, name: str, actions: List[AutomationAction], 
                 global_timeout: float = 300.0):
        self.name = name
        self.actions = actions
        self.global_timeout = global_timeout
        self.results: List[AutomationResult] = []
        self.start_time = None
        self.end_time = None
    
    def add_action(self, action: AutomationAction):
        """Add action to sequence"""
        self.actions.append(action)
    
    def get_duration(self) -> Optional[float]:
        """Get total execution duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

class HumanBehaviorEngine:
    """Simulates human-like behavior patterns"""
    
    def __init__(self):
        self.behavior_patterns = {
            'reading_delay': (0.5, 2.0),  # Time to "read" text
            'thinking_delay': (1.0, 3.0),  # Time to "think" between actions
            'typing_speed': (0.1, 0.3),   # Delay between keystrokes
            'scroll_pause': (0.2, 0.8),   # Pause after scrolling
        }
        
        # Fatigue simulation
        self.actions_count = 0
        self.fatigue_threshold = 50
        self.fatigue_multiplier = 1.0
    
    async def apply_reading_delay(self, text_length: int = 10):
        """Simulate time needed to read text"""
        base_delay = random.uniform(*self.behavior_patterns['reading_delay'])
        # Longer text takes more time to read
        reading_time = base_delay + (text_length * 0.05)
        reading_time *= self.fatigue_multiplier
        
        logger.debug(f"Applying reading delay: {reading_time:.2f}s")
        await asyncio.sleep(reading_time)
    
    async def apply_thinking_delay(self):
        """Simulate thinking time between actions"""
        thinking_time = random.uniform(*self.behavior_patterns['thinking_delay'])
        thinking_time *= self.fatigue_multiplier
        
        logger.debug(f"Applying thinking delay: {thinking_time:.2f}s")
        await asyncio.sleep(thinking_time)
    
    async def apply_action_delay(self):
        """Apply general delay between actions"""
        delay = random.uniform(0.3, 1.0) * self.fatigue_multiplier
        await asyncio.sleep(delay)
    
    def update_fatigue(self):
        """Update fatigue based on action count"""
        self.actions_count += 1
        if self.actions_count > self.fatigue_threshold:
            # Gradually slow down as more actions are performed
            excess = self.actions_count - self.fatigue_threshold
            self.fatigue_multiplier = 1.0 + (excess * 0.02)
            logger.debug(f"Fatigue multiplier: {self.fatigue_multiplier:.2f}")

class SmartAutomationEngine:
    """
    Main automation engine with intelligent behavior and conditional logic
    """
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        
        # Initialize core components
        self.screen_capture = ScreenCaptureManager()
        self.ocr_engine = OCRDetectionEngine()
        self.tap_engine = TapCoordinateEngine(test_mode=test_mode)
        self.behavior_engine = HumanBehaviorEngine()
        
        # Execution state
        self.is_running = False
        self.current_sequence = None
        self.execution_context = {}
        
        # Performance tracking
        self.stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'total_execution_time': 0.0
        }
        
        logger.info(f"Smart automation engine initialized (test_mode: {test_mode})")
    
    async def execute_sequence(self, sequence: AutomationSequence) -> List[AutomationResult]:
        """Execute a complete automation sequence"""
        logger.info(f"Starting automation sequence: {sequence.name}")
        
        self.is_running = True
        self.current_sequence = sequence
        sequence.start_time = time.time()
        
        try:
            for i, action in enumerate(sequence.actions):
                if not self.is_running:
                    logger.info("Automation stopped by user")
                    break
                
                # Check global timeout
                elapsed = time.time() - sequence.start_time
                if elapsed > sequence.global_timeout:
                    logger.error(f"Global timeout reached: {elapsed:.2f}s")
                    break
                
                logger.info(f"Executing action {i+1}/{len(sequence.actions)}: {action.description}")
                
                # Execute action with retries
                result = await self._execute_action_with_retries(action)
                sequence.results.append(result)
                
                # Update statistics
                self.stats['total_actions'] += 1
                if result.success:
                    self.stats['successful_actions'] += 1
                else:
                    self.stats['failed_actions'] += 1
                self.stats['total_execution_time'] += result.execution_time
                
                # Apply human-like behavior
                self.behavior_engine.update_fatigue()
                await self.behavior_engine.apply_action_delay()
                
                # Stop on critical failure
                if not result.success and action.action_type in [ActionType.CONDITION]:
                    logger.error("Critical action failed, stopping sequence")
                    break
        
        finally:
            sequence.end_time = time.time()
            self.is_running = False
            self._log_sequence_summary(sequence)
        
        return sequence.results
    
    async def _execute_action_with_retries(self, action: AutomationAction) -> AutomationResult:
        """Execute single action with retry logic"""
        start_time = time.time()
        last_error = None
        
        for attempt in range(action.max_retries):
            try:
                # Apply human thinking delay before attempts (except first)
                if attempt > 0:
                    await self.behavior_engine.apply_thinking_delay()
                
                # Execute the action
                success, data, error = await self._execute_single_action(action)
                
                execution_time = time.time() - start_time
                
                if success:
                    return AutomationResult(
                        success=True,
                        action=action,
                        execution_time=execution_time,
                        attempts=attempt + 1,
                        data=data
                    )
                else:
                    last_error = error
                    logger.warning(f"Action attempt {attempt + 1} failed: {error}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Action attempt {attempt + 1} error: {e}")
        
        # All attempts failed
        execution_time = time.time() - start_time
        return AutomationResult(
            success=False,
            action=action,
            execution_time=execution_time,
            attempts=action.max_retries,
            error_message=last_error
        )
    
    async def _execute_single_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute a single automation action"""
        
        # Check condition if specified
        if action.condition:
            condition_met = await self._evaluate_condition(action.condition)
            if not condition_met:
                return False, {}, "Action condition not met"
        
        # Execute based on action type
        if action.action_type == ActionType.TAP:
            return await self._execute_tap_action(action)
        elif action.action_type == ActionType.WAIT:
            return await self._execute_wait_action(action)
        elif action.action_type == ActionType.FIND_TEXT:
            return await self._execute_find_text_action(action)
        elif action.action_type == ActionType.VERIFY:
            return await self._execute_verify_action(action)
        elif action.action_type == ActionType.LOOP:
            return await self._execute_loop_action(action)
        elif action.action_type == ActionType.CONDITION:
            return await self._execute_condition_action(action)
        else:
            return False, {}, f"Unknown action type: {action.action_type}"
    
    async def _execute_tap_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute tap action"""
        try:
            target_text = action.parameters.get('text')
            coordinates = action.parameters.get('coordinates')
            
            # Capture current screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return False, {}, "Failed to capture screen"
            
            screen_dims = image.size
            
            if target_text:
                # Find and tap text
                ocr_result = await self.ocr_engine.detect_text(image)
                result = await self.tap_engine.tap_text(ocr_result, target_text, screen_dims)
            elif coordinates:
                # Tap at specific coordinates
                x, y = coordinates
                result = await self.tap_engine.tap_coordinate(x, y, screen_dims)
            else:
                return False, {}, "No tap target specified"
            
            return result.success, {'tap_result': result}, result.error_message
            
        except Exception as e:
            return False, {}, str(e)
    
    async def _execute_wait_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute wait action"""
        try:
            duration = action.parameters.get('duration', 1.0)
            await asyncio.sleep(duration)
            return True, {'waited': duration}, None
        except Exception as e:
            return False, {}, str(e)
    
    async def _execute_find_text_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute find text action"""
        try:
            target_text = action.parameters.get('text')
            if not target_text:
                return False, {}, "No text specified to find"
            
            # Capture and analyze screen
            image = await self.screen_capture.capture_with_retry()
            if not image:
                return False, {}, "Failed to capture screen"
            
            ocr_result = await self.ocr_engine.detect_text(image)
            matches = self.ocr_engine.find_text(ocr_result, target_text)
            
            found = len(matches) > 0
            data = {
                'found': found,
                'matches': len(matches),
                'text_detections': [m.text for m in matches]
            }
            
            # Apply reading delay for human-like behavior
            if found:
                await self.behavior_engine.apply_reading_delay(len(target_text))
            
            return found, data, None if found else f"Text '{target_text}' not found"
            
        except Exception as e:
            return False, {}, str(e)
    
    async def _execute_verify_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute verification action"""
        # Similar to find_text but used for verification
        return await self._execute_find_text_action(action)
    
    async def _execute_loop_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute loop action"""
        try:
            iterations = action.parameters.get('iterations', 1)
            sub_actions = action.parameters.get('actions', [])
            
            loop_results = []
            for i in range(iterations):
                logger.info(f"Loop iteration {i+1}/{iterations}")
                
                for sub_action in sub_actions:
                    success, data, error = await self._execute_single_action(sub_action)
                    loop_results.append({
                        'iteration': i + 1,
                        'success': success,
                        'data': data,
                        'error': error
                    })
                    
                    if not success:
                        logger.warning(f"Loop sub-action failed: {error}")
                        # Continue with next action unless it's critical
            
            return True, {'loop_results': loop_results}, None
            
        except Exception as e:
            return False, {}, str(e)
    
    async def _execute_condition_action(self, action: AutomationAction) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Execute conditional action"""
        try:
            condition = action.parameters.get('condition')
            if not condition:
                return False, {}, "No condition specified"
            
            condition_met = await self._evaluate_condition(condition)
            return condition_met, {'condition_met': condition_met}, None if condition_met else "Condition not met"
            
        except Exception as e:
            return False, {}, str(e)
    
    async def _evaluate_condition(self, condition: AutomationCondition) -> bool:
        """Evaluate a conditional check"""
        try:
            if condition.condition_type == ConditionType.TEXT_EXISTS:
                text = condition.parameters.get('text')
                image = await self.screen_capture.capture_with_retry()
                if image:
                    ocr_result = await self.ocr_engine.detect_text(image)
                    matches = self.ocr_engine.find_text(ocr_result, text)
                    result = len(matches) > 0
                else:
                    result = False
            
            elif condition.condition_type == ConditionType.TEXT_NOT_EXISTS:
                text = condition.parameters.get('text')
                image = await self.screen_capture.capture_with_retry()
                if image:
                    ocr_result = await self.ocr_engine.detect_text(image)
                    matches = self.ocr_engine.find_text(ocr_result, text)
                    result = len(matches) == 0
                else:
                    result = True  # If can't capture, assume text doesn't exist
            
            else:
                logger.warning(f"Unknown condition type: {condition.condition_type}")
                result = False
            
            # Apply negation if specified
            if condition.negate:
                result = not result
            
            return result
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def stop_execution(self):
        """Stop current automation execution"""
        self.is_running = False
        logger.info("Automation execution stopped")
    
    def _log_sequence_summary(self, sequence: AutomationSequence):
        """Log execution summary"""
        duration = sequence.get_duration()
        total_actions = len(sequence.results)
        successful = sum(1 for r in sequence.results if r.success)
        failed = total_actions - successful
        
        logger.info(f"Sequence '{sequence.name}' completed:")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Actions: {successful}/{total_actions} successful")
        logger.info(f"  Success rate: {(successful/total_actions)*100 if total_actions > 0 else 0:.1f}%")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get automation statistics"""
        return self.stats.copy()


# Helper functions for creating automation sequences
def create_tap_action(text: str = None, coordinates: tuple = None, 
                     description: str = "", **kwargs) -> AutomationAction:
    """Create a tap action"""
    params = {}
    if text:
        params['text'] = text
    if coordinates:
        params['coordinates'] = coordinates
    
    return AutomationAction(
        action_type=ActionType.TAP,
        parameters=params,
        description=description or f"Tap {'text: ' + text if text else 'coordinates: ' + str(coordinates)}",
        **kwargs
    )

def create_wait_action(duration: float, description: str = "", **kwargs) -> AutomationAction:
    """Create a wait action"""
    return AutomationAction(
        action_type=ActionType.WAIT,
        parameters={'duration': duration},
        description=description or f"Wait {duration}s",
        **kwargs
    )

def create_find_text_action(text: str, description: str = "", **kwargs) -> AutomationAction:
    """Create a find text action"""
    return AutomationAction(
        action_type=ActionType.FIND_TEXT,
        parameters={'text': text},
        description=description or f"Find text: {text}",
        **kwargs
    )

def create_condition_action(condition_type: ConditionType, text: str = None, 
                          description: str = "", **kwargs) -> AutomationAction:
    """Create a condition action"""
    condition = AutomationCondition(condition_type=condition_type)
    if text:
        condition.parameters['text'] = text
    
    return AutomationAction(
        action_type=ActionType.CONDITION,
        parameters={'condition': condition},
        description=description or f"Check condition: {condition_type.value}",
        **kwargs
    )


# Example usage
async def main():
    """Test the automation engine"""
    try:
        # Initialize engine
        engine = SmartAutomationEngine(test_mode=True)
        
        # Create a sample automation sequence
        actions = [
            create_find_text_action("Settings", description="Look for Settings"),
            create_tap_action(text="Settings", description="Tap Settings"),
            create_wait_action(2.0, description="Wait for Settings to load"),
            create_find_text_action("WiFi", description="Look for WiFi option"),
            create_tap_action(text="WiFi", description="Tap WiFi"),
        ]
        
        sequence = AutomationSequence("Sample Settings Navigation", actions)
        
        # Execute sequence
        results = await engine.execute_sequence(sequence)
        
        # Show results
        print(f"Executed {len(results)} actions")
        for i, result in enumerate(results):
            status = "✓" if result.success else "✗"
            print(f"{status} Action {i+1}: {result.action.description} ({result.execution_time:.2f}s)")
        
        print(f"Statistics: {engine.get_statistics()}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())