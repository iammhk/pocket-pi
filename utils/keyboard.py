# utils/keyboard.py
# This file is part of the actual project. It implements a virtual keyboard for text input using a joystick.

import time
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw

# Pins
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
KEY1, KEY2, KEY3 = 21, 20, 16

class VirtualKeyboard:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.keys = [
            ['A','B','C','D','E','F'],
            ['G','H','I','J','K','L'],
            ['M','N','O','P','Q','R'],
            ['S','T','U','V','W','X'],
            ['Y','Z','0','1','2','3'],
            ['4','5','6','7','8','9'],
            ['SPC','DEL','CLR','OK','','']
        ]
        self.row = 0
        self.col = 0
        self.text = ""
        
        # Initialize pins
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, LEFT, RIGHT, KEY1, KEY2, KEY3]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), (10, 10, 10))
        draw = ImageDraw.Draw(image)
        
        # Draw Text Field
        draw.rectangle([5, 5, 123, 25], fill=(40, 40, 40))
        draw.text((10, 10), self.text + "_", fill="white")
        
        # Draw Keys
        for r, row_keys in enumerate(self.keys):
            for c, key in enumerate(row_keys):
                if not key: continue
                
                x = 5 + c * 20
                y = 35 + r * 13
                
                color = "white"
                if r == self.row and c == self.col:
                    draw.rectangle([x-1, y-1, x+18, y+11], fill=(0, 255, 255))
                    color = "black"
                
                draw.text((x+2, y), key, fill=color)
        
        self.display.display(image)

    def get_input(self):
        last_move = 0
        while True:
            self.draw()
            
            if time.time() - last_move > 0.15:
                if GPIO.input(UP) == GPIO.LOW:
                    self.row = (self.row - 1) % len(self.keys); last_move = time.time()
                elif GPIO.input(DOWN) == GPIO.LOW:
                    self.row = (self.row + 1) % len(self.keys); last_move = time.time()
                elif GPIO.input(LEFT) == GPIO.LOW:
                    self.col = (self.col - 1) % 6; last_move = time.time()
                elif GPIO.input(RIGHT) == GPIO.LOW:
                    self.col = (self.col + 1) % 6; last_move = time.time()
                
                if GPIO.input(KEY1) == GPIO.LOW: # OK button
                    char = self.keys[self.row][self.col]
                    if char == 'OK': return self.text
                    elif char == 'SPC': self.text += " "
                    elif char == 'DEL': self.text = self.text[:-1]
                    elif char == 'CLR': self.text = ""
                    else: self.text += char
                    time.sleep(0.2)
                
                if GPIO.input(KEY3) == GPIO.LOW: # Cancel
                    return None
            
            time.sleep(0.05)
