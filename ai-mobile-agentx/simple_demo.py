"""
AI Mobile AgentX - Simple Demo
Demonstrates the core concepts without complex dependencies
"""

import asyncio
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

def create_mock_screenshot():
    """Create a mock mobile screenshot for demonstration"""
    # Create a mock mobile screen (1080x1920 - typical mobile resolution)
    img = Image.new('RGB', (1080, 1920), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw mock mobile UI elements
    # Status bar
    draw.rectangle([0, 0, 1080, 80], fill='black')
    draw.text((20, 30), "9:42", fill='white', font=font)
    draw.text((950, 30), "100%", fill='white', font=font)
    
    # App icons (Gmail example)
    draw.rectangle([50, 200, 200, 350], outline='gray', width=2)
    draw.text((80, 275), "Gmail", fill='black', font=font)
    
    # WhatsApp
    draw.rectangle([250, 200, 400, 350], outline='gray', width=2)
    draw.text((270, 275), "WhatsApp", fill='black', font=font)
    
    # Spotify
    draw.rectangle([450, 200, 600, 350], outline='gray', width=2)
    draw.text((480, 275), "Spotify", fill='black', font=font)
    
    # Maps
    draw.rectangle([650, 200, 800, 350], outline='gray', width=2)
    draw.text((690, 275), "Maps", fill='black', font=font)
    
    # Calendar
    draw.rectangle([850, 200, 1000, 350], outline='gray', width=2)
    draw.text((870, 275), "Calendar", fill='black', font=font)
    
    # Add some UI text that OCR would detect
    draw.text((50, 500), "Search", fill='blue', font=font)
    draw.text((50, 600), "Settings", fill='black', font=font)
    draw.text((50, 700), "Messages", fill='black', font=font)
    
    return img

def simulate_ocr_detection(image):
    """Simulate OCR text detection on the mock screenshot"""
    # In real implementation, this would use Tesseract/EasyOCR
    # Here we simulate the detected text regions
    detected_texts = [
        {'text': 'Gmail', 'bbox': (80, 250, 170, 300), 'confidence': 0.95},
        {'text': 'WhatsApp', 'bbox': (270, 250, 380, 300), 'confidence': 0.92},
        {'text': 'Spotify', 'bbox': (480, 250, 570, 300), 'confidence': 0.88},
        {'text': 'Maps', 'bbox': (690, 250, 740, 300), 'confidence': 0.94},
        {'text': 'Calendar', 'bbox': (870, 250, 960, 300), 'confidence': 0.91},
        {'text': 'Search', 'bbox': (50, 480, 120, 520), 'confidence': 0.89},
        {'text': 'Settings', 'bbox': (50, 580, 140, 620), 'confidence': 0.93},
        {'text': 'Messages', 'bbox': (50, 680, 150, 720), 'confidence': 0.87}
    ]
    return detected_texts

def simulate_tap_coordination(target_text, detected_texts):
    """Simulate intelligent tap coordinate calculation"""
    for detection in detected_texts:
        if target_text.lower() in detection['text'].lower():
            x, y, w, h = detection['bbox']
            # Calculate center point with slight randomization (human-like)
            center_x = x + (w - x) // 2 + (hash(target_text) % 10 - 5)
            center_y = y + (h - y) // 2 + (hash(target_text) % 10 - 5)
            return center_x, center_y, detection['confidence']
    return None, None, 0.0

def create_annotated_screenshot(image, detected_texts, target_text=None, tap_coords=None):
    """Create annotated screenshot showing OCR detection and tap targets"""
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    
    # Draw OCR detection boxes
    for detection in detected_texts:
        x, y, w, h = detection['bbox']
        color = 'green' if detection['confidence'] > 0.9 else 'orange'
        draw.rectangle([x, y, w, h], outline=color, width=2)
        
        # Add confidence score
        confidence_text = f"{detection['confidence']:.2f}"
        draw.text((x, y-20), confidence_text, fill=color)
    
    # Draw tap target if specified
    if tap_coords and tap_coords[0] is not None:
        x, y = tap_coords[0], tap_coords[1]
        # Draw red circle for tap target
        radius = 15
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='red', width=3)
        draw.text((x+20, y-10), f"TAP: {target_text}", fill='red')
    
    return annotated

async def demo_ai_mobile_automation():
    """Demonstrate AI Mobile AgentX automation concepts"""
    print("🤖 AI Mobile AgentX - Core Concepts Demo")
    print("=" * 45)
    
    # Step 1: Screen Capture Simulation
    print("\n📸 Step 1: Screen Capture")
    print("   Capturing mobile screen... (simulated)")
    screenshot = create_mock_screenshot()
    
    # Save original screenshot
    os.makedirs("demo_output", exist_ok=True)
    screenshot.save("demo_output/01_original_screen.png")
    print("   ✅ Screenshot saved: demo_output/01_original_screen.png")
    
    await asyncio.sleep(1)  # Simulate processing time
    
    # Step 2: OCR Text Detection
    print("\n👁️  Step 2: OCR Text Detection")
    print("   Analyzing screenshot for text...")
    detected_texts = simulate_ocr_detection(screenshot)
    
    print("   📝 Detected texts:")
    for detection in detected_texts:
        print(f"      '{detection['text']}' (confidence: {detection['confidence']:.2f})")
    
    # Create OCR visualization
    ocr_image = create_annotated_screenshot(screenshot, detected_texts)
    ocr_image.save("demo_output/02_ocr_detection.png")
    print("   ✅ OCR visualization saved: demo_output/02_ocr_detection.png")
    
    await asyncio.sleep(1)
    
    # Step 3: Intelligent Tap Coordination
    print("\n🎯 Step 3: Intelligent Tap Coordination")
    test_targets = ['Gmail', 'WhatsApp', 'Spotify']
    
    for target in test_targets:
        print(f"   Finding tap coordinates for '{target}'...")
        x, y, confidence = simulate_tap_coordination(target, detected_texts)
        
        if x is not None:
            print(f"   ✅ Target found: ({x}, {y}) - confidence: {confidence:.2f}")
            
            # Create visualization with tap target
            tap_image = create_annotated_screenshot(screenshot, detected_texts, target, (x, y))
            tap_image.save(f"demo_output/03_tap_{target.lower()}.png")
            print(f"   📸 Tap visualization saved: demo_output/03_tap_{target.lower()}.png")
        else:
            print(f"   ❌ Target '{target}' not found")
        
        await asyncio.sleep(0.5)
    
    # Step 4: Automation Sequence Simulation
    print("\n🤖 Step 4: Automation Sequence Simulation")
    print("   Simulating Gmail automation sequence...")
    
    automation_steps = [
        "1. Tap Gmail app icon",
        "2. Wait for app to load",
        "3. Tap 'Compose' button", 
        "4. Enter recipient email",
        "5. Enter subject line",
        "6. Type email body",
        "7. Tap 'Send' button"
    ]
    
    for step in automation_steps:
        print(f"   {step}")
        await asyncio.sleep(0.3)  # Simulate execution time
    
    print("   ✅ Automation sequence completed!")
    
    # Step 5: Summary
    print("\n📊 Demo Summary")
    print("=" * 30)
    print("✅ Screen capture: Simulated mobile screen capture")
    print("✅ OCR detection: Found 8 text elements with high confidence")
    print("✅ Tap coordination: Calculated precise tap coordinates")
    print("✅ Automation sequence: Demonstrated Gmail workflow")
    print("✅ Visual feedback: Generated annotated screenshots")
    
    print(f"\n📁 All demo files saved to: demo_output/")
    print("🎯 This demonstrates how AI Mobile AgentX works without a real device!")

def show_real_device_setup():
    """Show what would be needed for real device testing"""
    print("\n📱 For Real Device Testing, You Would Need:")
    print("=" * 45)
    print("🔧 Android Setup:")
    print("   • Enable Developer Options")
    print("   • Enable USB Debugging") 
    print("   • Install ADB (Android Debug Bridge)")
    print("   • Connect device via USB")
    print("   • Run: adb devices (to verify connection)")
    
    print("\n🔧 iOS Setup (Limited Support):")
    print("   • Requires jailbroken device")
    print("   • Additional tools for screen capture")
    print("   • More complex setup process")
    
    print("\n🔧 OCR Engine Setup:")
    print("   • Install Tesseract OCR")
    print("   • Download from: https://github.com/tesseract-ocr/tesseract")
    print("   • Or use EasyOCR: pip install easyocr")
    
    print("\n💡 But for now, the mock demo shows you exactly how it works!")

if __name__ == "__main__":
    try:
        print("🚀 Starting AI Mobile AgentX Demo...")
        asyncio.run(demo_ai_mobile_automation())
        show_real_device_setup()
        
        print("\n🎉 Demo completed successfully!")
        print("📖 Check the demo_output folder for visual results")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("💡 This is a simplified demo - see README.md for full capabilities")