"""
AI Mobile AgentX - Mock Testing Framework
Safe testing environment with visual feedback for automation validation
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from ..core import ScreenCaptureManager, OCRDetectionEngine, TapCoordinateEngine
from ..core.automation_engine import SmartAutomationEngine, AutomationSequence, AutomationAction
from ..intelligence import IntelligentPositionCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Test result status"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    PARTIAL = "partial"

@dataclass
class MockAction:
    """Represents a mock action for testing"""
    action_type: str
    target: str
    expected_result: bool
    description: str
    visual_feedback: bool = True

@dataclass
class TestCase:
    """Represents a complete test case"""
    name: str
    description: str
    mock_actions: List[MockAction]
    expected_outcome: str
    timeout: float = 30.0
    
@dataclass
class TestReport:
    """Test execution report"""
    test_name: str
    result: TestResult
    execution_time: float
    actions_performed: int
    actions_successful: int
    error_message: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    visual_feedback_data: Dict[str, Any] = field(default_factory=dict)

class VisualDebugger:
    """Provides visual feedback for automation testing"""
    
    def __init__(self, output_dir: str = "test_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.colors = {
            'tap_target': (255, 0, 0),      # Red for tap targets
            'text_detection': (0, 255, 0),  # Green for detected text
            'success': (0, 255, 0),         # Green for success
            'failure': (255, 0, 0),         # Red for failure
            'warning': (255, 165, 0),       # Orange for warnings
        }
        
        self.font_size = 12
        try:
            self.font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            self.font = ImageFont.load_default()
    
    def annotate_screen(self, image: Image.Image, annotations: List[Dict[str, Any]], 
                       title: str = "") -> Image.Image:
        """Add visual annotations to screenshot"""
        try:
            # Create a copy to avoid modifying original
            annotated = image.copy()
            draw = ImageDraw.Draw(annotated)
            
            # Add title if provided
            if title:
                draw.text((10, 10), title, fill=self.colors['text_detection'], font=self.font)
            
            # Add annotations
            for i, annotation in enumerate(annotations):
                x, y = annotation.get('position', (0, 0))
                text = annotation.get('text', f'Annotation {i+1}')
                color = self.colors.get(annotation.get('type', 'text_detection'), (255, 255, 255))
                
                # Draw circle at position
                radius = 8
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           outline=color, width=2)
                
                # Draw text label
                text_y = y + radius + 5
                draw.text((x-20, text_y), text, fill=color, font=self.font)
            
            return annotated
            
        except Exception as e:
            logger.error(f"Screen annotation failed: {e}")
            return image
    
    def create_test_comparison(self, before_image: Image.Image, 
                             after_image: Image.Image, 
                             action_description: str) -> Image.Image:
        """Create before/after comparison image"""
        try:
            # Resize images to same height for comparison
            height = min(before_image.height, after_image.height)
            before_resized = before_image.resize((
                int(before_image.width * height / before_image.height), height
            ))
            after_resized = after_image.resize((
                int(after_image.width * height / after_image.height), height
            ))
            
            # Create comparison image
            total_width = before_resized.width + after_resized.width + 20  # 20px gap
            comparison = Image.new('RGB', (total_width, height + 50), color='white')
            
            # Paste images
            comparison.paste(before_resized, (0, 50))
            comparison.paste(after_resized, (before_resized.width + 20, 50))
            
            # Add labels
            draw = ImageDraw.Draw(comparison)
            draw.text((10, 10), f"Action: {action_description}", fill=(0, 0, 0), font=self.font)
            draw.text((before_resized.width // 2 - 30, 30), "BEFORE", fill=(0, 0, 0), font=self.font)
            draw.text((before_resized.width + 20 + after_resized.width // 2 - 25, 30), 
                     "AFTER", fill=(0, 0, 0), font=self.font)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Test comparison creation failed: {e}")
            return before_image
    
    def save_test_screenshot(self, image: Image.Image, test_name: str, 
                           step_name: str, timestamp: str = None) -> str:
        """Save test screenshot with organized naming"""
        try:
            if not timestamp:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            filename = f"{test_name}_{step_name}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            image.save(filepath)
            logger.debug(f"Test screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Screenshot saving failed: {e}")
            return ""

class MockAutomationEngine:
    """
    Mock automation engine for safe testing without actual device interaction
    """
    
    def __init__(self):
        self.visual_debugger = VisualDebugger()
        self.mock_responses = {
            'tap': self._mock_tap_response,
            'find_text': self._mock_find_text_response,
            'wait': self._mock_wait_response,
            'verify': self._mock_verify_response,
        }
        
        # Mock screen states for testing
        self.mock_screens = self._initialize_mock_screens()
        self.current_screen_index = 0
        
        # Test execution tracking
        self.execution_log = []
        
        logger.info("Mock automation engine initialized")
    
    def _initialize_mock_screens(self) -> List[Dict[str, Any]]:
        """Initialize mock screen states for testing"""
        return [
            {
                'name': 'home_screen',
                'detected_texts': ['Settings', 'Gmail', 'WhatsApp', 'Maps', 'Spotify'],
                'image_size': (1080, 1920),
                'success_rate': 0.95
            },
            {
                'name': 'gmail_inbox',
                'detected_texts': ['Inbox', 'Compose', 'Search', 'Menu', 'Important'],
                'image_size': (1080, 1920),
                'success_rate': 0.90
            },
            {
                'name': 'whatsapp_chats',
                'detected_texts': ['Chats', 'New chat', 'Search', 'John Doe', 'Jane Smith'],
                'image_size': (1080, 1920),
                'success_rate': 0.88
            },
        ]
    
    async def execute_mock_sequence(self, sequence: AutomationSequence, 
                                  visual_feedback: bool = True) -> TestReport:
        """Execute automation sequence in mock mode with visual feedback"""
        start_time = time.time()
        
        test_report = TestReport(
            test_name=sequence.name,
            result=TestResult.PASS,
            execution_time=0.0,
            actions_performed=0,
            actions_successful=0
        )
        
        try:
            logger.info(f"Starting mock execution: {sequence.name}")
            
            for i, action in enumerate(sequence.actions):
                # Create mock screen state
                mock_screen = self._create_mock_screen()
                
                # Take "before" screenshot
                before_screenshot = None
                if visual_feedback:
                    before_screenshot = self.visual_debugger.save_test_screenshot(
                        mock_screen, sequence.name, f"step_{i+1}_before"
                    )
                    test_report.screenshots.append(before_screenshot)
                
                # Execute mock action
                success, feedback_data = await self._execute_mock_action(action, mock_screen)
                test_report.actions_performed += 1
                
                if success:
                    test_report.actions_successful += 1
                else:
                    test_report.result = TestResult.PARTIAL
                
                # Create visual feedback
                if visual_feedback:
                    annotated_screen = self._create_annotated_screen(
                        mock_screen, action, success, feedback_data
                    )
                    
                    after_screenshot = self.visual_debugger.save_test_screenshot(
                        annotated_screen, sequence.name, f"step_{i+1}_after"
                    )
                    test_report.screenshots.append(after_screenshot)
                    
                    # Create comparison if we have before image
                    if before_screenshot:
                        comparison = self.visual_debugger.create_test_comparison(
                            mock_screen, annotated_screen, action.description
                        )
                        comparison_path = self.visual_debugger.save_test_screenshot(
                            comparison, sequence.name, f"step_{i+1}_comparison"
                        )
                        test_report.screenshots.append(comparison_path)
                
                # Update visual feedback data
                test_report.visual_feedback_data[f"step_{i+1}"] = feedback_data
                
                # Log execution step
                self.execution_log.append({
                    'step': i + 1,
                    'action': action.description,
                    'success': success,
                    'timestamp': time.time()
                })
                
                # Simulate human-like delay
                await asyncio.sleep(0.5)
            
            # Determine final result
            if test_report.actions_successful == test_report.actions_performed:
                test_report.result = TestResult.PASS
            elif test_report.actions_successful == 0:
                test_report.result = TestResult.FAIL
            else:
                test_report.result = TestResult.PARTIAL
            
            test_report.execution_time = time.time() - start_time
            
            logger.info(f"Mock execution completed: {test_report.result.value}")
            return test_report
            
        except Exception as e:
            test_report.result = TestResult.FAIL
            test_report.error_message = str(e)
            test_report.execution_time = time.time() - start_time
            logger.error(f"Mock execution failed: {e}")
            return test_report
    
    def _create_mock_screen(self) -> Image.Image:
        """Create a mock screen image for testing"""
        try:
            # Create a basic mock screen
            img = Image.new('RGB', (1080, 1920), color='white')
            draw = ImageDraw.Draw(img)
            
            # Get current mock screen data
            screen_data = self.mock_screens[self.current_screen_index % len(self.mock_screens)]
            
            # Add mock UI elements
            y_offset = 100
            for text in screen_data['detected_texts']:
                x_pos = 50 + (hash(text) % 300)  # Pseudo-random but consistent positioning
                draw.text((x_pos, y_offset), text, fill='black', font=self.visual_debugger.font)
                
                # Draw button background
                text_width = len(text) * 8  # Approximate text width
                draw.rectangle([x_pos-5, y_offset-5, x_pos+text_width+5, y_offset+20], 
                             outline='gray', width=1)
                
                y_offset += 100
            
            # Add some visual elements
            draw.rectangle([50, 50, 1030, 1870], outline='black', width=2)  # Screen border
            draw.text((50, 25), f"Mock Screen: {screen_data['name']}", fill='blue', 
                     font=self.visual_debugger.font)
            
            return img
            
        except Exception as e:
            logger.error(f"Mock screen creation failed: {e}")
            # Return a simple fallback image
            return Image.new('RGB', (1080, 1920), color='lightgray')
    
    async def _execute_mock_action(self, action: AutomationAction, 
                                  mock_screen: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """Execute a single mock action"""
        try:
            action_type = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
            
            if action_type in self.mock_responses:
                return await self.mock_responses[action_type](action, mock_screen)
            else:
                # Unknown action type
                return False, {'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            return False, {'error': str(e)}
    
    async def _mock_tap_response(self, action: AutomationAction, 
                                mock_screen: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """Mock tap action response"""
        target_text = action.parameters.get('text', 'Unknown')
        
        # Get current screen data
        screen_data = self.mock_screens[self.current_screen_index % len(self.mock_screens)]
        
        # Check if target text exists in mock screen
        if target_text in screen_data['detected_texts']:
            # Simulate successful tap
            success = True
            tap_x = 100 + (hash(target_text) % 300)
            tap_y = 100 + (screen_data['detected_texts'].index(target_text) * 100)
            
            feedback = {
                'target_found': True,
                'tap_position': (tap_x, tap_y),
                'confidence': screen_data['success_rate']
            }
            
            # Move to next screen state (simulate app navigation)
            self.current_screen_index += 1
            
        else:
            # Target not found
            success = False
            feedback = {
                'target_found': False,
                'available_targets': screen_data['detected_texts'],
                'error': f"Target '{target_text}' not found on screen"
            }
        
        # Add small delay to simulate real action
        await asyncio.sleep(0.2)
        
        return success, feedback
    
    async def _mock_find_text_response(self, action: AutomationAction, 
                                     mock_screen: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """Mock find text action response"""
        target_text = action.parameters.get('text', 'Unknown')
        screen_data = self.mock_screens[self.current_screen_index % len(self.mock_screens)]
        
        found = target_text in screen_data['detected_texts']
        
        feedback = {
            'text_found': found,
            'search_target': target_text,
            'detected_texts': screen_data['detected_texts']
        }
        
        return found, feedback
    
    async def _mock_wait_response(self, action: AutomationAction, 
                                mock_screen: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """Mock wait action response"""
        duration = action.parameters.get('duration', 1.0)
        
        # Actually wait for the specified duration
        await asyncio.sleep(duration)
        
        feedback = {
            'wait_duration': duration,
            'completed': True
        }
        
        return True, feedback
    
    async def _mock_verify_response(self, action: AutomationAction, 
                                  mock_screen: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """Mock verify action response"""
        # Same as find_text for verification
        return await self._mock_find_text_response(action, mock_screen)
    
    def _create_annotated_screen(self, mock_screen: Image.Image, 
                               action: AutomationAction, success: bool, 
                               feedback_data: Dict[str, Any]) -> Image.Image:
        """Create annotated screen showing action results"""
        try:
            annotations = []
            
            # Add action target annotation
            if 'tap_position' in feedback_data:
                x, y = feedback_data['tap_position']
                annotations.append({
                    'position': (x, y),
                    'text': f"TAP: {action.parameters.get('text', 'Unknown')}",
                    'type': 'success' if success else 'failure'
                })
            
            # Add status annotation
            status_text = "SUCCESS" if success else "FAILED"
            status_color = 'success' if success else 'failure'
            
            title = f"{action.description} - {status_text}"
            
            return self.visual_debugger.annotate_screen(mock_screen, annotations, title)
            
        except Exception as e:
            logger.error(f"Screen annotation failed: {e}")
            return mock_screen
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of mock execution"""
        total_steps = len(self.execution_log)
        successful_steps = sum(1 for step in self.execution_log if step['success'])
        
        return {
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'success_rate': successful_steps / total_steps if total_steps > 0 else 0.0,
            'execution_log': self.execution_log
        }
    
    def reset_mock_state(self):
        """Reset mock automation state"""
        self.current_screen_index = 0
        self.execution_log.clear()
        logger.info("Mock automation state reset")

class SafeTestRunner:
    """
    Main test runner for safe automation testing
    """
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.mock_engine = MockAutomationEngine()
        self.test_results: List[TestReport] = []
        
        logger.info(f"Safe test runner initialized (output: {output_dir})")
    
    async def run_test_case(self, test_case: TestCase, 
                          visual_feedback: bool = True) -> TestReport:
        """Run a single test case"""
        logger.info(f"Running test case: {test_case.name}")
        
        # Convert test case to automation sequence
        actions = []
        for mock_action in test_case.mock_actions:
            action = AutomationAction(
                action_type=mock_action.action_type,
                parameters={'text': mock_action.target},
                description=mock_action.description
            )
            actions.append(action)
        
        sequence = AutomationSequence(test_case.name, actions, test_case.timeout)
        
        # Execute in mock mode
        report = await self.mock_engine.execute_mock_sequence(sequence, visual_feedback)
        
        # Save test report
        self._save_test_report(report)
        self.test_results.append(report)
        
        return report
    
    async def run_test_suite(self, test_cases: List[TestCase], 
                           visual_feedback: bool = True) -> List[TestReport]:
        """Run multiple test cases"""
        logger.info(f"Running test suite with {len(test_cases)} test cases")
        
        suite_results = []
        
        for test_case in test_cases:
            # Reset mock state for each test
            self.mock_engine.reset_mock_state()
            
            # Run test case
            report = await self.run_test_case(test_case, visual_feedback)
            suite_results.append(report)
            
            # Brief pause between tests
            await asyncio.sleep(1.0)
        
        # Generate suite summary
        self._generate_suite_summary(suite_results)
        
        return suite_results
    
    def _save_test_report(self, report: TestReport):
        """Save individual test report"""
        try:
            report_data = {
                'test_name': report.test_name,
                'result': report.result.value,
                'execution_time': report.execution_time,
                'actions_performed': report.actions_performed,
                'actions_successful': report.actions_successful,
                'error_message': report.error_message,
                'screenshots': report.screenshots,
                'visual_feedback_data': report.visual_feedback_data,
                'timestamp': time.time()
            }
            
            report_file = self.output_dir / f"{report.test_name}_report.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Test report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test report: {e}")
    
    def _generate_suite_summary(self, results: List[TestReport]):
        """Generate test suite summary"""
        try:
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.result == TestResult.PASS)
            failed_tests = sum(1 for r in results if r.result == TestResult.FAIL)
            partial_tests = sum(1 for r in results if r.result == TestResult.PARTIAL)
            
            summary = {
                'test_suite_summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'partial_tests': partial_tests,
                    'success_rate': passed_tests / total_tests if total_tests > 0 else 0.0,
                    'total_execution_time': sum(r.execution_time for r in results)
                },
                'individual_results': [
                    {
                        'test_name': r.test_name,
                        'result': r.result.value,
                        'execution_time': r.execution_time,
                        'success_rate': r.actions_successful / r.actions_performed if r.actions_performed > 0 else 0.0
                    }
                    for r in results
                ],
                'mock_execution_summary': self.mock_engine.get_execution_summary(),
                'timestamp': time.time()
            }
            
            summary_file = self.output_dir / "test_suite_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Test suite summary saved: {summary_file}")
            logger.info(f"Suite Results: {passed_tests}/{total_tests} passed ({passed_tests/total_tests*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"Failed to generate suite summary: {e}")
    
    def create_sample_test_cases(self) -> List[TestCase]:
        """Create sample test cases for demonstration"""
        return [
            TestCase(
                name="basic_navigation_test",
                description="Test basic navigation between apps",
                mock_actions=[
                    MockAction("tap", "Gmail", True, "Open Gmail app"),
                    MockAction("find_text", "Inbox", True, "Verify Gmail opened"),
                    MockAction("tap", "Compose", True, "Start composing email"),
                ],
                expected_outcome="Successfully navigate to Gmail compose screen"
            ),
            
            TestCase(
                name="whatsapp_messaging_test",
                description="Test WhatsApp message sending",
                mock_actions=[
                    MockAction("tap", "WhatsApp", True, "Open WhatsApp"),
                    MockAction("tap", "Chats", True, "Navigate to chats"),
                    MockAction("tap", "New chat", True, "Start new chat"),
                    MockAction("find_text", "Search", True, "Find search option"),
                ],
                expected_outcome="Successfully prepare for sending WhatsApp message"
            ),
            
            TestCase(
                name="error_handling_test",
                description="Test error handling with non-existent elements",
                mock_actions=[
                    MockAction("tap", "NonExistentApp", False, "Try to tap non-existent app"),
                    MockAction("find_text", "NonExistentText", False, "Try to find non-existent text"),
                ],
                expected_outcome="Gracefully handle missing UI elements"
            )
        ]


# Example usage and testing
async def main():
    """Test the mock testing framework"""
    try:
        # Initialize test runner
        test_runner = SafeTestRunner()
        
        # Create sample test cases
        test_cases = test_runner.create_sample_test_cases()
        
        print(f"Running {len(test_cases)} test cases...")
        
        # Run test suite
        results = await test_runner.run_test_suite(test_cases, visual_feedback=True)
        
        # Display results
        print("\nTest Results:")
        for result in results:
            status_emoji = "✅" if result.result == TestResult.PASS else "❌" if result.result == TestResult.FAIL else "⚠️"
            print(f"{status_emoji} {result.test_name}: {result.result.value} ({result.execution_time:.2f}s)")
            print(f"   Actions: {result.actions_successful}/{result.actions_performed} successful")
            if result.error_message:
                print(f"   Error: {result.error_message}")
        
        print(f"\nTest artifacts saved to: {test_runner.output_dir}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())