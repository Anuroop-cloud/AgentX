"""
AI Mobile AgentX - Enhanced Real Device Testing with OCR
Uses actual Tesseract and EasyOCR for text detection on real device screenshots
"""

import subprocess
import asyncio
import os
import time
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import cv2
import numpy as np

# Try importing OCR libraries
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR imported successfully")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract OCR not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✅ EasyOCR imported successfully")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  EasyOCR not available")

class EnhancedRealDeviceController:
    def __init__(self):
        # Full path to ADB
        self.adb_path = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
        self.device_connected = False
        
        # Initialize OCR engines
        if EASYOCR_AVAILABLE:
            print("🔄 Initializing EasyOCR reader...")
            self.easyocr_reader = easyocr.Reader(['en'])
            print("✅ EasyOCR reader initialized")
        else:
            self.easyocr_reader = None
            
        # Tesseract configuration for mobile screenshots
        self.tesseract_config = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
        
    def run_adb_command(self, command, binary=False):
        """Execute ADB command and return output"""
        try:
            full_command = [self.adb_path] + command.split()
            if binary:
                result = subprocess.run(full_command, capture_output=True, timeout=30)
                return result.returncode == 0, result.stdout, result.stderr.decode('utf-8', errors='ignore')
            else:
                result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)
                return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_device_connection(self):
        """Check if Android device is connected"""
        print("📱 Checking Device Connection...")
        
        success, stdout, stderr = self.run_adb_command("devices")
        if not success:
            print(f"❌ Failed to check devices: {stderr}")
            return False
            
        lines = stdout.strip().split('\n')[1:]  # Skip header
        connected_devices = [line for line in lines if line.strip() and 'device' in line]
        
        if not connected_devices:
            print("❌ No devices connected")
            return False
        else:
            print(f"✅ Found {len(connected_devices)} connected device(s):")
            for device in connected_devices:
                device_id = device.split()[0]
                print(f"   📱 Device ID: {device_id}")
            self.device_connected = True
            return True
    
    def capture_screen(self):
        """Capture screenshot from connected device"""
        if not self.device_connected:
            print("❌ No device connected for screen capture")
            return None
            
        print("📸 Capturing device screen...")
        
        # Use ADB to capture screenshot and save to device first
        temp_path = "/sdcard/temp_screenshot.png"
        
        # Capture screenshot on device
        success, stdout, stderr = self.run_adb_command(f"shell screencap -p {temp_path}")
        if not success:
            print(f"❌ Screenshot capture failed: {stderr}")
            return None
        
        # Pull screenshot from device
        local_temp = "temp_screenshot.png"
        success, stdout, stderr = self.run_adb_command(f"pull {temp_path} {local_temp}")
        if not success:
            print(f"❌ Screenshot pull failed: {stderr}")
            return None
            
        try:
            # Load the screenshot file
            if os.path.exists(local_temp):
                image = Image.open(local_temp)
                print(f"✅ Screenshot captured: {image.size[0]}x{image.size[1]}")
                
                # Create a copy of the image data before closing
                image_copy = image.copy()
                image.close()
                
                # Small delay before cleanup
                time.sleep(0.1)
                
                # Cleanup temp files
                try:
                    os.remove(local_temp)
                except:
                    pass  # Ignore cleanup errors
                self.run_adb_command(f"shell rm {temp_path}")
                
                return image_copy
            else:
                print("❌ Screenshot file not found")
                return None
        except Exception as e:
            print(f"❌ Error processing screenshot: {e}")
            return None
    
    def perform_tesseract_ocr(self, image):
        """Perform OCR using Tesseract"""
        if not TESSERACT_AVAILABLE:
            return []
            
        print("🔍 Running Tesseract OCR...")
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Get detailed OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(opencv_image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            detected_texts = []
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                confidence = float(ocr_data['conf'][i])
                
                if text and confidence > 30:  # Filter out low confidence detections
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    detected_texts.append({
                        'text': text,
                        'bbox': (x, y, x + w, y + h),
                        'confidence': confidence / 100.0,  # Normalize to 0-1
                        'center': (x + w // 2, y + h // 2),
                        'engine': 'Tesseract'
                    })
            
            print(f"   📝 Tesseract found {len(detected_texts)} text elements")
            return detected_texts
            
        except Exception as e:
            print(f"   ❌ Tesseract OCR error: {e}")
            return []
    
    def perform_easyocr_ocr(self, image):
        """Perform OCR using EasyOCR"""
        if not EASYOCR_AVAILABLE or self.easyocr_reader is None:
            return []
            
        print("🔍 Running EasyOCR...")
        try:
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            # Perform OCR
            results = self.easyocr_reader.readtext(image_array)
            
            detected_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filter out low confidence detections
                    # EasyOCR returns bbox as list of 4 points
                    # Convert to simple rectangle
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    x1, y1 = int(min(x_coords)), int(min(y_coords))
                    x2, y2 = int(max(x_coords)), int(max(y_coords))
                    
                    detected_texts.append({
                        'text': text.strip(),
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence,
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                        'engine': 'EasyOCR'
                    })
            
            print(f"   📝 EasyOCR found {len(detected_texts)} text elements")
            return detected_texts
            
        except Exception as e:
            print(f"   ❌ EasyOCR error: {e}")
            return []
    
    def combine_ocr_results(self, tesseract_results, easyocr_results):
        """Combine and deduplicate OCR results from multiple engines"""
        print("🔄 Combining OCR results...")
        
        all_results = tesseract_results + easyocr_results
        
        # Simple deduplication based on text similarity and proximity
        unique_results = []
        for result in all_results:
            is_duplicate = False
            for existing in unique_results:
                # Check if texts are similar and centers are close
                text_similar = result['text'].lower() == existing['text'].lower()
                center_distance = ((result['center'][0] - existing['center'][0])**2 + 
                                 (result['center'][1] - existing['center'][1])**2)**0.5
                
                if text_similar and center_distance < 50:
                    # Keep the one with higher confidence
                    if result['confidence'] > existing['confidence']:
                        unique_results.remove(existing)
                        unique_results.append(result)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        print(f"   ✅ Combined to {len(unique_results)} unique text elements")
        return unique_results
    
    def create_ocr_visualization(self, image, detected_texts):
        """Create annotated image showing OCR detections"""
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        colors = {'Tesseract': 'red', 'EasyOCR': 'blue', 'Combined': 'green'}
        
        for detection in detected_texts:
            x1, y1, x2, y2 = detection['bbox']
            engine = detection.get('engine', 'Combined')
            color = colors.get(engine, 'green')
            
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # Draw confidence score
            confidence_text = f"{detection['confidence']:.2f}"
            draw.text((x1, y1-20), confidence_text, fill=color, font=font)
            
            # Draw detected text (truncated if too long)
            text_display = detection['text'][:20] + "..." if len(detection['text']) > 20 else detection['text']
            draw.text((x1, y2+5), text_display, fill=color, font=font)
        
        return annotated
    
    def tap_screen(self, x, y):
        """Tap screen at specified coordinates"""
        if not self.device_connected:
            print("❌ No device connected for tapping")
            return False
            
        print(f"👆 Tapping screen at ({x}, {y})")
        success, stdout, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        
        if success:
            print("✅ Tap executed successfully")
            return True
        else:
            print(f"❌ Tap failed: {stderr}")
            return False

async def run_enhanced_real_device_test():
    """Run enhanced real device test with actual OCR"""
    print("🤖 AI Mobile AgentX - Enhanced Real Device Testing")
    print("=" * 50)
    
    controller = EnhancedRealDeviceController()
    
    # Check device connection
    if not controller.check_device_connection():
        return False
    
    # Capture screenshot
    screenshot = controller.capture_screen()
    if screenshot is None:
        return False
    
    # Save original screenshot
    os.makedirs("real_device_output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"real_device_output/screenshot_{timestamp}.png"
    screenshot.save(screenshot_path)
    print(f"📁 Screenshot saved: {screenshot_path}")
    
    # Perform OCR with multiple engines
    print("\n👁️  Performing Multi-Engine OCR Analysis...")
    
    tesseract_results = controller.perform_tesseract_ocr(screenshot)
    easyocr_results = controller.perform_easyocr_ocr(screenshot)
    
    # Combine results
    all_detected_texts = controller.combine_ocr_results(tesseract_results, easyocr_results)
    
    # Display results
    print(f"\n📊 OCR Detection Results:")
    print(f"   🔍 Total unique text elements found: {len(all_detected_texts)}")
    
    # Show top 10 most confident detections
    sorted_texts = sorted(all_detected_texts, key=lambda x: x['confidence'], reverse=True)[:10]
    print(f"\n📝 Top 10 Most Confident Detections:")
    for i, detection in enumerate(sorted_texts, 1):
        print(f"   {i:2d}. '{detection['text']}' (conf: {detection['confidence']:.2f}, engine: {detection['engine']})")
    
    # Create OCR visualization
    ocr_visualization = controller.create_ocr_visualization(screenshot, all_detected_texts)
    ocr_viz_path = f"real_device_output/ocr_visualization_{timestamp}.png"
    ocr_visualization.save(ocr_viz_path)
    print(f"📁 OCR visualization saved: {ocr_viz_path}")
    
    # Smart tap target selection
    print(f"\n🎯 Intelligent Tap Target Selection...")
    
    # Look for common app names or UI elements
    target_keywords = ['Settings', 'Chrome', 'Gmail', 'Phone', 'Messages', 'Camera', 'Gallery', 'Play Store']
    found_targets = []
    
    for keyword in target_keywords:
        for detection in all_detected_texts:
            if keyword.lower() in detection['text'].lower() and detection['confidence'] > 0.5:
                found_targets.append({
                    'keyword': keyword,
                    'detection': detection
                })
                break
    
    if found_targets:
        print(f"   ✅ Found {len(found_targets)} tap targets:")
        for target in found_targets[:3]:  # Show top 3
            detection = target['detection']
            print(f"      📱 {target['keyword']}: '{detection['text']}' at {detection['center']}")
        
        # Demo tap on first target
        if found_targets:
            target = found_targets[0]
            detection = target['detection']
            x, y = detection['center']
            
            print(f"\n🎯 Demo: Tapping on '{detection['text']}' in 3 seconds...")
            print("   ⚠️  (Ctrl+C to cancel)")
            
            try:
                await asyncio.sleep(3)
                success = controller.tap_screen(x, y)
                
                if success:
                    await asyncio.sleep(2)  # Wait for response
                    
                    # Capture after-tap screenshot
                    after_screenshot = controller.capture_screen()
                    if after_screenshot:
                        after_path = f"real_device_output/after_tap_{timestamp}.png"
                        after_screenshot.save(after_path)
                        print(f"   📁 After-tap screenshot: {after_path}")
                        
            except KeyboardInterrupt:
                print("   ⚠️  Tap cancelled by user")
    else:
        print("   ❌ No recognizable tap targets found")
    
    # Summary
    print(f"\n📊 Enhanced Test Summary")
    print("=" * 35)
    print(f"✅ Device connection: Working")
    print(f"✅ Screenshot capture: Success ({screenshot.size[0]}x{screenshot.size[1]})")
    print(f"✅ Tesseract OCR: {'Available' if TESSERACT_AVAILABLE else 'Not Available'}")
    print(f"✅ EasyOCR: {'Available' if EASYOCR_AVAILABLE else 'Not Available'}")
    print(f"✅ Text elements detected: {len(all_detected_texts)}")
    print(f"✅ Tap targets found: {len(found_targets)}")
    print(f"📁 All results saved to: real_device_output/")
    
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced Real Device Test...")
        success = asyncio.run(run_enhanced_real_device_test())
        
        if success:
            print("\n🎉 Enhanced real device test completed successfully!")
            print("💡 This demonstrates full AI-powered mobile automation capabilities!")
        else:
            print("\n❌ Enhanced test failed - check device connection")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("💡 Make sure OCR engines are properly installed")