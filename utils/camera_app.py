# utils/camera_app.py
# This file provides camera preview and photo taking functionality for the Pocket Pi.
# It is used in the actual project.

import time
import os
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import io

# Button Pins (must match launcher.py)
UP = 6
DOWN = 19
LEFT = 5
RIGHT = 26
PRESS = 13
KEY1 = 21
KEY2 = 20
KEY3 = 16

def main(disp):
    # Try to import camera libraries
    camera = None
    mode = None
    
    # Simple message display function
    def show_error(msg, submsg=""):
        img = Image.new("RGB", (128, 128), (20, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "CAMERA ERROR", fill="red")
        draw.text((10, 60), msg, fill="white")
        draw.text((10, 75), submsg, fill="gray")
        draw.text((10, 110), "Press KEY3 to exit", fill="yellow")
        disp.display(img)
        while GPIO.input(KEY3) == GPIO.HIGH:
            time.sleep(0.1)

    # Detect camera stack
    try:
        from picamera import PiCamera
        camera = PiCamera()
        camera.resolution = (128, 128)
        camera.framerate = 30
        # Wait for the camera to warm up
        time.sleep(0.5)
        mode = "legacy"
    except Exception as e:
        try:
            # Try libcamera/picamerax or similar if available
            # For now, let's stick to a robust subprocess fallback if picamera fails
            # or try Picamera2 if it's a newer system
            from picamera import PiCamera
            # If we are here, picamera exists but failed to init (maybe legacy stack not enabled)
            raise e
        except:
            show_error("No Camera Found", "Check connection/config")
            return

    # Ensure photos directory exists
    photo_dir = "assets/photos"
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)

    running = True
    show_message = None
    message_time = 0
    
    # We use a stream for the legacy picamera to get frames
    stream = io.BytesIO()

    try:
        while running:
            # Capture frame for preview
            stream.seek(0)
            camera.capture(stream, format='jpeg', use_video_port=True, resize=(128, 128))
            stream.seek(0)
            img = Image.open(stream).convert("RGB")
            
            # Draw UI
            draw = ImageDraw.Draw(img)
            
            # Crosshair
            draw.line([(64, 54), (64, 74)], fill=(0, 255, 0, 100))
            draw.line([(54, 64), (74, 64)], fill=(0, 255, 0, 100))
            
            # UI Overlay
            if show_message:
                # Draw a translucent box for the message
                overlay = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
                o_draw = ImageDraw.Draw(overlay)
                o_draw.rectangle([10, 50, 118, 80], fill=(0, 0, 0, 180))
                o_draw.text((25, 60), show_message, fill="cyan")
                img.paste(overlay, (0, 0), overlay)
                
                if time.time() - message_time > 1.5:
                    show_message = None

            # Top bar info
            draw.rectangle([0, 0, 128, 15], fill=(0, 0, 0, 100))
            draw.text((5, 2), "📷 LIVE PREVIEW", fill="white")
            
            # Bottom bar info
            draw.rectangle([0, 113, 128, 128], fill=(0, 0, 0, 100))
            draw.text((5, 115), "K1:SNAP  K3:EXIT", fill="yellow")

            disp.display(img)

            # Check inputs
            if GPIO.input(KEY1) == GPIO.LOW or GPIO.input(PRESS) == GPIO.LOW:
                # Capture high-res photo
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(photo_dir, f"IMG_{timestamp}.jpg")
                
                # Visual feedback (flash)
                flash = Image.new("RGB", (128, 128), "white")
                disp.display(flash)
                
                # Take the photo
                # For better quality, we switch resolution briefly
                old_res = camera.resolution
                camera.resolution = (1920, 1080)
                camera.capture(filename)
                camera.resolution = old_res
                
                show_message = "PHOTO SAVED!"
                message_time = time.time()
                time.sleep(0.3) # Debounce

            if GPIO.input(KEY3) == GPIO.LOW:
                running = False
                
            # Minor delay to prevent CPU hogging
            time.sleep(0.01)

    except Exception as e:
        show_error("Runtime Error", str(e)[:20])
    finally:
        if camera:
            camera.close()

if __name__ == "__main__":
    # Test script
    from drivers.st7735 import ST7735
    disp = ST7735()
    disp.init()
    disp.rotate(90)
    main(disp)
