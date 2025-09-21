"""
AI Mobile AgentX - OCR Detection Engine
Advanced text detection with ML Kit and Tesseract integration
Optimized for mobile performance with smart bounding box calculation
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from PIL import Image
import numpy as np
import cv2
from abc import ABC, abstractmethod
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextDetection:
    """Represents detected text with position and confidence"""
    text: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    center_point: Tuple[int, int]
    detection_time: float
    detection_method: str


@dataclass 
class OCRResult:
    """Complete OCR analysis result"""
    detections: List[TextDetection]
    processing_time: float
    image_dimensions: Tuple[int, int]
    total_detections: int
    average_confidence: float


class BaseOCREngine(ABC):
    """Abstract base class for OCR engines"""
    
    @abstractmethod
    async def detect_text(self, image: Image.Image) -> List[TextDetection]:
        pass
    
    @abstractmethod
    def get_engine_name(self) -> str:
        pass


class TesseractEngine(BaseOCREngine):
    """Tesseract OCR engine implementation"""
    
    def __init__(self):
        self.engine_name = "Tesseract"
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.available = True
            logger.info("Tesseract engine initialized successfully")
        except ImportError:
            logger.warning("Tesseract not available - install pytesseract")
            self.available = False
    
    async def detect_text(self, image: Image.Image) -> List[TextDetection]:
        """Detect text using Tesseract OCR"""
        if not self.available:
            return []
        
        start_time = time.time()
        detections = []
        
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Get detailed data with bounding boxes
            data = self.pytesseract.image_to_data(
                cv_image, 
                output_type=self.pytesseract.Output.DICT,
                config='--psm 6'  # Uniform block of text
            )
            
            # Process detections
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                confidence = float(data['conf'][i])
                
                # Filter out low confidence or empty detections
                if confidence > 30 and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    detection = TextDetection(
                        text=text,
                        confidence=confidence / 100.0,  # Normalize to 0-1
                        bounding_box=(x, y, w, h),
                        center_point=(center_x, center_y),
                        detection_time=time.time() - start_time,
                        detection_method=self.engine_name
                    )
                    detections.append(detection)
            
            logger.debug(f"Tesseract detected {len(detections)} text elements")
            return detections
            
        except Exception as e:
            logger.error(f"Tesseract detection failed: {e}")
            return []
    
    def get_engine_name(self) -> str:
        return self.engine_name


class MLKitEngine(BaseOCREngine):
    """ML Kit OCR engine implementation (mock for desktop testing)"""
    
    def __init__(self):
        self.engine_name = "ML Kit"
        # This would integrate with actual ML Kit on mobile
        self.available = True
        logger.info("ML Kit engine initialized (mock mode)")
    
    async def detect_text(self, image: Image.Image) -> List[TextDetection]:
        """Mock ML Kit text detection"""
        # In real implementation, this would use Firebase ML Kit
        # For now, we'll simulate ML Kit behavior
        start_time = time.time()
        
        try:
            # Simulate ML Kit processing delay
            await asyncio.sleep(0.1)
            
            # Mock detections for demo purposes
            width, height = image.size
            mock_detections = [
                TextDetection(
                    text="Sample Text",
                    confidence=0.95,
                    bounding_box=(width//4, height//4, width//2, 50),
                    center_point=(width//2, height//4 + 25),
                    detection_time=time.time() - start_time,
                    detection_method=self.engine_name
                )
            ]
            
            logger.debug("ML Kit mock detection completed")
            return mock_detections
            
        except Exception as e:
            logger.error(f"ML Kit detection failed: {e}")
            return []
    
    def get_engine_name(self) -> str:
        return self.engine_name


class EasyOCREngine(BaseOCREngine):
    """EasyOCR engine as alternative option"""
    
    def __init__(self):
        self.engine_name = "EasyOCR"
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=False)  # CPU only for mobile
            self.available = True
            logger.info("EasyOCR engine initialized successfully")
        except ImportError:
            logger.warning("EasyOCR not available - install easyocr")
            self.available = False
    
    async def detect_text(self, image: Image.Image) -> List[TextDetection]:
        """Detect text using EasyOCR"""
        if not self.available:
            return []
        
        start_time = time.time()
        detections = []
        
        try:
            # Convert PIL to numpy array
            image_array = np.array(image)
            
            # Run EasyOCR detection
            results = self.reader.readtext(image_array)
            
            # Process results
            for (bbox, text, confidence) in results:
                if confidence > 0.3 and text.strip():
                    # Calculate bounding box
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    x, y = int(min(x_coords)), int(min(y_coords))
                    w, h = int(max(x_coords) - x), int(max(y_coords) - y)
                    
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    detection = TextDetection(
                        text=text.strip(),
                        confidence=confidence,
                        bounding_box=(x, y, w, h),
                        center_point=(center_x, center_y),
                        detection_time=time.time() - start_time,
                        detection_method=self.engine_name
                    )
                    detections.append(detection)
            
            logger.debug(f"EasyOCR detected {len(detections)} text elements")
            return detections
            
        except Exception as e:
            logger.error(f"EasyOCR detection failed: {e}")
            return []
    
    def get_engine_name(self) -> str:
        return self.engine_name


class OCRDetectionEngine:
    """
    Main OCR detection engine with multiple backend support
    Intelligently selects best engine and provides unified interface
    """
    
    def __init__(self, preferred_engines: List[str] = None):
        if preferred_engines is None:
            preferred_engines = ["EasyOCR", "Tesseract", "ML Kit"]
        
        self.engines = {}
        self.active_engine = None
        
        # Initialize available engines
        for engine_name in preferred_engines:
            if engine_name == "Tesseract":
                engine = TesseractEngine()
            elif engine_name == "ML Kit":
                engine = MLKitEngine()
            elif engine_name == "EasyOCR":
                engine = EasyOCREngine()
            else:
                continue
            
            if engine.available:
                self.engines[engine_name] = engine
                if not self.active_engine:
                    self.active_engine = engine
        
        if not self.active_engine:
            raise RuntimeError("No OCR engines available")
        
        logger.info(f"OCR Engine initialized with {len(self.engines)} engines")
        logger.info(f"Active engine: {self.active_engine.get_engine_name()}")
    
    async def detect_text(self, image: Image.Image, engine_name: str = None) -> OCRResult:
        """
        Detect text in image with specified or default engine
        
        Args:
            image: PIL Image to analyze
            engine_name: Specific engine to use (optional)
            
        Returns:
            OCRResult with all detections and metadata
        """
        start_time = time.time()
        
        # Select engine
        engine = self.active_engine
        if engine_name and engine_name in self.engines:
            engine = self.engines[engine_name]
        
        # Perform detection
        detections = await engine.detect_text(image)
        
        # Calculate result metadata
        processing_time = time.time() - start_time
        total_detections = len(detections)
        average_confidence = sum(d.confidence for d in detections) / total_detections if detections else 0.0
        
        result = OCRResult(
            detections=detections,
            processing_time=processing_time,
            image_dimensions=image.size,
            total_detections=total_detections,
            average_confidence=average_confidence
        )
        
        logger.info(f"OCR completed: {total_detections} detections in {processing_time:.2f}s")
        return result
    
    def find_text(self, ocr_result: OCRResult, search_text: str, fuzzy: bool = True) -> List[TextDetection]:
        """
        Find specific text in OCR results
        
        Args:
            ocr_result: OCR analysis result
            search_text: Text to search for
            fuzzy: Enable fuzzy matching
            
        Returns:
            List of matching detections
        """
        matches = []
        search_lower = search_text.lower()
        
        for detection in ocr_result.detections:
            text_lower = detection.text.lower()
            
            # Exact match
            if search_lower == text_lower:
                matches.append(detection)
            # Fuzzy matching
            elif fuzzy and (search_lower in text_lower or text_lower in search_lower):
                matches.append(detection)
        
        logger.debug(f"Found {len(matches)} matches for '{search_text}'")
        return matches
    
    def find_text_by_pattern(self, ocr_result: OCRResult, pattern: str) -> List[TextDetection]:
        """Find text matching regex pattern"""
        import re
        matches = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            for detection in ocr_result.detections:
                if regex.search(detection.text):
                    matches.append(detection)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
        
        return matches
    
    def get_text_near_point(self, ocr_result: OCRResult, x: int, y: int, radius: int = 50) -> List[TextDetection]:
        """Find text elements near a specific point"""
        nearby = []
        
        for detection in ocr_result.detections:
            center_x, center_y = detection.center_point
            distance = ((center_x - x) ** 2 + (center_y - y) ** 2) ** 0.5
            
            if distance <= radius:
                nearby.append(detection)
        
        # Sort by distance
        nearby.sort(key=lambda d: ((d.center_point[0] - x) ** 2 + (d.center_point[1] - y) ** 2) ** 0.5)
        return nearby
    
    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines"""
        return list(self.engines.keys())
    
    def switch_engine(self, engine_name: str) -> bool:
        """Switch to different OCR engine"""
        if engine_name in self.engines:
            self.active_engine = self.engines[engine_name]
            logger.info(f"Switched to {engine_name} engine")
            return True
        return False
    
    def export_results(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """Export OCR results to dictionary for caching/storage"""
        return {
            'detections': [
                {
                    'text': d.text,
                    'confidence': d.confidence,
                    'bounding_box': d.bounding_box,
                    'center_point': d.center_point,
                    'detection_time': d.detection_time,
                    'detection_method': d.detection_method
                }
                for d in ocr_result.detections
            ],
            'processing_time': ocr_result.processing_time,
            'image_dimensions': ocr_result.image_dimensions,
            'total_detections': ocr_result.total_detections,
            'average_confidence': ocr_result.average_confidence
        }


# Example usage and testing
async def main():
    """Test the OCR detection system"""
    try:
        # Initialize OCR engine
        ocr = OCRDetectionEngine()
        print(f"Available engines: {ocr.get_available_engines()}")
        
        # Create test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add test text
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 50), "Hello World", fill='black', font=font)
        draw.text((50, 100), "Click Here", fill='blue', font=font)
        draw.text((50, 150), "Settings", fill='green', font=font)
        
        # Test OCR detection
        print("Running OCR detection...")
        result = await ocr.detect_text(img)
        
        print(f"Total detections: {result.total_detections}")
        print(f"Average confidence: {result.average_confidence:.2f}")
        print(f"Processing time: {result.processing_time:.2f}s")
        
        # Show detected text
        for detection in result.detections:
            print(f"Text: '{detection.text}' at {detection.center_point} (confidence: {detection.confidence:.2f})")
        
        # Test text finding
        matches = ocr.find_text(result, "Hello")
        print(f"Found {len(matches)} matches for 'Hello'")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())