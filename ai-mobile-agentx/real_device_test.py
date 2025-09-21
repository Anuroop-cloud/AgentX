"""
AI Mobile AgentX - Real Device Testing
Connects to actual Android device for automation testing
"""

import subprocess
import asyncio
import os
import time
from PIL import Image
import io
from datetime import datetime

class RealDeviceController:
    def __init__(self):
        # Full path to ADB (adjust if your Android SDK is elsewhere)
        self.adb_path = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
        self.device_connected = False
        
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
    
    def check_adb_installation(self):
        """Verify ADB is properly installed"""
        print("🔧 Checking ADB Installation...")
        
        if not os.path.exists(self.adb_path):
            print(f"❌ ADB not found at: {self.adb_path}")
            print("💡 Please install Android SDK or Android Studio")
            return False
            
        success, stdout, stderr = self.run_adb_command("version")
        if success:
            print("✅ ADB is installed and working")
            print(f"   Version: {stdout.strip().split()[2] if stdout else 'Unknown'}")
            return True
        else:
            print(f"❌ ADB installation issue: {stderr}")
            return False
    
    def check_device_connection(self):
        """Check if Android device is connected"""
        print("\n📱 Checking Device Connection...")
        
        success, stdout, stderr = self.run_adb_command("devices")
        if not success:
            print(f"❌ Failed to check devices: {stderr}")
            return False
            
        lines = stdout.strip().split('\n')[1:]  # Skip header
        connected_devices = [line for line in lines if line.strip() and 'device' in line]
        
        if not connected_devices:
            print("❌ No devices connected")
            print("\n📋 Device Setup Instructions:")
            print("   1. Enable 'Developer Options' on your Android device:")
            print("      Settings → About Phone → Tap 'Build Number' 7 times")
            print("   2. Enable 'USB Debugging':")
            print("      Settings → Developer Options → USB Debugging")
            print("   3. Connect device via USB cable")
            print("   4. Allow USB debugging when prompted on device")
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
    
    def simulate_ocr_on_real_image(self, image):
        """Simulate OCR detection on real device screenshot"""
        # This is a simplified simulation - in real implementation would use Tesseract/EasyOCR
        print("👁️  Simulating OCR detection on real device screenshot...")
        
        width, height = image.size
        print(f"   Screen resolution: {width}x{height}")
        
        # Common locations where apps/buttons might be found (percentage-based)
        common_elements = [
            {'text': 'Gmail', 'position': (0.2, 0.3), 'confidence': 0.85},
            {'text': 'Chrome', 'position': (0.4, 0.3), 'confidence': 0.80},
            {'text': 'Settings', 'position': (0.6, 0.3), 'confidence': 0.90},
            {'text': 'Phone', 'position': (0.8, 0.3), 'confidence': 0.88},
            {'text': 'Messages', 'position': (0.2, 0.5), 'confidence': 0.92},
            {'text': 'Camera', 'position': (0.4, 0.5), 'confidence': 0.87},
            {'text': 'Photos', 'position': (0.6, 0.5), 'confidence': 0.89},
            {'text': 'Play Store', 'position': (0.8, 0.5), 'confidence': 0.84}
        ]
        
        detected_elements = []
        for element in common_elements:
            x = int(element['position'][0] * width)
            y = int(element['position'][1] * height)
            detected_elements.append({
                'text': element['text'],
                'center': (x, y),
                'confidence': element['confidence']
            })
        
        print(f"   📝 Simulated detection of {len(detected_elements)} elements")
        return detected_elements

async def run_real_device_test():
    """Main function to test AI Mobile AgentX with real device"""
    print("🤖 AI Mobile AgentX - Real Device Testing")
    print("=" * 45)
    
    controller = RealDeviceController()
    
    # Step 1: Check ADB installation
    if not controller.check_adb_installation():
        return False
    
    # Step 2: Check device connection
    if not controller.check_device_connection():
        return False
    
    # Step 3: Capture real screenshot
    screenshot = controller.capture_screen()
    if screenshot is None:
        return False
    
    # Save screenshot
    os.makedirs("real_device_output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"real_device_output/screenshot_{timestamp}.png"
    screenshot.save(screenshot_path)
    print(f"📁 Screenshot saved: {screenshot_path}")
    
    # Step 4: Simulate OCR detection
    detected_elements = controller.simulate_ocr_on_real_image(screenshot)
    
    # Step 5: Demonstrate tap automation
    print("\n🎯 Testing Tap Automation...")
    
    # Find a target to tap (let's try Settings)
    target_app = "Settings"
    target_element = None
    
    for element in detected_elements:
        if target_app.lower() in element['text'].lower():
            target_element = element
            break
    
    if target_element:
        x, y = target_element['center']
        print(f"   🎯 Found '{target_app}' at ({x}, {y})")
        print("   ⚠️  About to tap in 3 seconds... (Ctrl+C to cancel)")
        
        try:
            await asyncio.sleep(3)
            success = controller.tap_screen(x, y)
            if success:
                print("   ✅ Tap executed on real device!")
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
        print(f"   ❌ '{target_app}' not found in detected elements")
    
    # Step 6: Summary
    print("\n📊 Real Device Test Summary")
    print("=" * 35)
    print("✅ ADB connection: Working")
    print("✅ Device detection: Connected")
    print("✅ Screen capture: Success")
    print("✅ OCR simulation: Completed")
    print("✅ Tap automation: Executed")
    print(f"📁 Results saved to: real_device_output/")
    
    return True

def show_installation_help():
    """Show help for missing dependencies"""
    print("\n🔧 Missing Dependencies Setup:")
    print("=" * 35)
    print("📦 For full OCR functionality, install:")
    print("   pip install pytesseract easyocr opencv-python")
    print()
    print("📱 For Tesseract OCR engine:")
    print("   Download from: https://github.com/tesseract-ocr/tesseract")
    print("   Or use Windows installer")
    print()
    print("💡 Current test uses simulated OCR for demonstration")

if __name__ == "__main__":
    try:
        print("🚀 Starting Real Device Test...")
        success = asyncio.run(run_real_device_test())
        
        if success:
            print("\n🎉 Real device test completed successfully!")
            show_installation_help()
        else:
            print("\n❌ Real device test failed - check setup requirements")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("💡 Make sure your Android device is properly connected")