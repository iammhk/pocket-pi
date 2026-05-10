# test_camera.py
# Temporary script to test camera connectivity on the Pi.
import sys
try:
    from picamera2 import Picamera2
    pc2 = Picamera2()
    print("Cameras found:", pc2.cameras)
except Exception as e:
    print(f"Error: {e}")
