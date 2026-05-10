# utils/camera_app.py
# This file provides camera preview and photo taking functionality for the Pocket Pi.
# It is updated to support the modern rpicam/libcamera stack.

import time
import os
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
import datetime
import io
import subprocess

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
    camera = None
    mode = None
    
    # Initialize GPIO pins
    GPIO.setmode(GPIO.BCM)
    for pin in [UP, DOWN, LEFT, RIGHT, PRESS, KEY1, KEY2, KEY3]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Try to initialize Picamera2 (Modern stack)
    error_msg = "No cameras found"
    try:
        from picamera2 import Picamera2
        try:
            camera = Picamera2()
            config = camera.create_preview_configuration(main={"format": "RGB888", "size": (128, 128)})
            camera.configure(config)
            camera.set_controls({"Rotation": 90}) # 90 degree clockwise
            camera.start()
            mode = "picamera2"
        except Exception as e:
            error_msg = str(e)
            if "Pipeline handler in use" in error_msg:
                error_msg = "Camera Busy"
            print(f"Picamera2 init failed: {e}")
            raise # Fallback to legacy
    except Exception:
        # Fallback to legacy picamera
        try:
            from picamera import PiCamera
            try:
                camera = PiCamera()
                camera.rotation = 90 # 90 degree clockwise
                camera.resolution = (128, 128)
                camera.framerate = 30
                time.sleep(0.5)
                mode = "legacy"
            except Exception as e:
                error_msg = str(e)
                print(f"Legacy Picamera init failed: {e}")
                raise
        except Exception:
            # Last resort: Show error and instructions
            img = Image.new("RGB", (128, 128), (20, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((10, 20), "CAMERA ERROR", fill="red")
            
            # Truncate error message if too long
            display_err = error_msg[:20] + "..." if len(error_msg) > 20 else error_msg
            draw.text((10, 40), display_err, fill="yellow")
            
            draw.text((10, 60), "Try:", fill="white")
            draw.text((10, 75), "sudo apt install", fill="cyan")
            draw.text((10, 90), "python3-picamera2", fill="cyan")
            draw.text((10, 110), "K3: EXIT", fill="yellow")
            disp.display(img)
            while GPIO.input(KEY3) == GPIO.HIGH:
                time.sleep(0.1)
            return

    # Ensure photos directory exists
    photo_dir = "assets/photos"
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)

    running = True
    show_message = None
    message_time = 0

    try:
        while running:
            # Capture frame for preview
            if mode == "picamera2":
                img_array = camera.capture_array()
                img = Image.fromarray(img_array).convert("RGB")
            else:
                stream = io.BytesIO()
                camera.capture(stream, format='jpeg', use_video_port=True, resize=(128, 128))
                stream.seek(0)
                img = Image.open(stream).convert("RGB")
            
            # Draw UI
            draw = ImageDraw.Draw(img)
            
            # Crosshair
            draw.line([(64, 54), (64, 74)], fill=(0, 255, 0, 100))
            draw.line([(54, 64), (74, 64)], fill=(0, 255, 0, 100))
            
            if show_message:
                draw.rectangle([10, 50, 118, 80], fill=(0, 0, 0, 180))
                draw.text((25, 60), show_message, fill="cyan")
                if time.time() - message_time > 1.5:
                    show_message = None

            # Overlay info
            draw.rectangle([0, 0, 128, 15], fill=(0, 0, 0, 100))
            draw.text((5, 2), f"📷 {mode.upper()} PREVIEW", fill="white")
            draw.rectangle([0, 113, 128, 128], fill=(0, 0, 0, 100))
            draw.text((5, 115), "K1:SNAP  K3:EXIT", fill="yellow")

            disp.display(img)

            # Check inputs
            if GPIO.input(KEY1) == GPIO.LOW or GPIO.input(PRESS) == GPIO.LOW:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(photo_dir, f"IMG_{timestamp}.jpg")
                
                # Visual feedback
                flash = Image.new("RGB", (128, 128), "white")
                disp.display(flash)
                
                # Take photo
                if mode == "picamera2":
                    camera.capture_file(filename)
                else:
                    old_res = camera.resolution
                    camera.resolution = (2592, 1944) # v1.3 max res
                    camera.capture(filename)
                    camera.resolution = old_res
                
                show_message = "PHOTO SAVED!"
                message_time = time.time()
                time.sleep(0.3)

            if GPIO.input(KEY3) == GPIO.LOW:
                running = False
            time.sleep(0.01)

    except Exception as e:
        print(f"Camera Error: {e}")
    finally:
        if camera:
            if mode == "picamera2":
                camera.stop()
            else:
                camera.close()

if __name__ == "__main__":
    from drivers.st7735 import ST7735
    disp = ST7735()
    disp.init()
    disp.rotate(90)
    main(disp)
