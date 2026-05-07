# games/pet.py
# This file is part of the actual project. It implements a virtual pet (Tamagotchi-like) game for the Pocket-Pi.

import time
import json
import os
import math
import sys
import RPi.GPIO as GPIO

# Add parent directory to path for driver imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw
from drivers.st7735 import ST7735

# Pins
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
KEY1, KEY2, KEY3 = 21, 20, 16

SAVE_FILE = "pet_state.json"

class VirtualPet:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.load_state()
        self.last_tick = time.time()
        self.selected_action = 0
        self.actions = [
            {"name": "FEED", "icon": "🍎"},
            {"name": "PLAY", "icon": "🎾"},
            {"name": "SLEEP", "icon": "💤"},
            {"name": "CLEAN", "icon": "🚿"}
        ]
        self.message = "Hello! I'm Pixel!"
        self.message_time = 0
        
        # Animation Sheet Setup
        self.anim_sheet = None
        self.frame_index = 0
        self.last_frame_time = 0
        self.animation_speed = 0.2 # Seconds per frame
        
        try:
            self.anim_sheet = Image.open("assets/pet_animations.png").convert("RGBA")
            # Image is 1024x1024, 6 columns, 4 rows
            self.cell_w = 1024 // 6
            self.cell_h = 1024 // 4
        except:
            print("Animation sheet not found, using static sprite or drawing.")
            self.anim_sheet = None

    def load_state(self):
        self.default_state() # Initialize with defaults first
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    loaded_state = json.load(f)
                    if isinstance(loaded_state, dict):
                        self.state.update(loaded_state)
                        
                        # Check for time elapsed
                        now = time.time()
                        last_saved = self.state.get("last_saved", now)
                        if not isinstance(last_saved, (int, float)):
                            last_saved = now
                            
                        elapsed = now - last_saved
                        # Decay stats based on time (1 point per 5 mins for hunger/happiness)
                        decay = elapsed / 300
                        self.state["hunger"] = max(0, float(self.state.get("hunger", 80)) - decay)
                        self.state["happiness"] = max(0, float(self.state.get("happiness", 80)) - decay)
                        
                        if self.state.get("is_sleeping", False):
                            self.state["energy"] = min(100, float(self.state.get("energy", 80)) + (elapsed / 60))
                        else:
                            self.state["energy"] = max(0, float(self.state.get("energy", 80)) - (elapsed / 600))
            except Exception as e:
                print(f"Error loading state: {e}")
                # default_state already set

    def default_state(self):
        self.state = {
            "name": "Pixel",
            "hunger": 80,
            "happiness": 80,
            "energy": 80,
            "is_sleeping": False,
            "last_saved": time.time()
        }

    def save_state(self):
        self.state["last_saved"] = time.time()
        with open(SAVE_FILE, "w") as f:
            json.dump(self.state, f)

    def update(self):
        now = time.time()
        # Game tick (faster decay while playing)
        if now - self.last_tick > 10: # Every 10 seconds
            if not self.state["is_sleeping"]:
                self.state["hunger"] = max(0, self.state["hunger"] - 0.5)
                self.state["happiness"] = max(0, self.state["happiness"] - 0.3)
                self.state["energy"] = max(0, self.state["energy"] - 0.2)
            else:
                self.state["energy"] = min(100, self.state["energy"] + 2)
            self.last_tick = now

        # Inputs
        if GPIO.input(LEFT) == GPIO.LOW:
            self.selected_action = (self.selected_action - 1) % len(self.actions)
            time.sleep(0.2)
        elif GPIO.input(RIGHT) == GPIO.LOW:
            self.selected_action = (self.selected_action + 1) % len(self.actions)
            time.sleep(0.2)
        elif GPIO.input(KEY1) == GPIO.LOW:
            self.perform_action()
            time.sleep(0.2)

    def perform_action(self):
        action = self.actions[self.selected_action]["name"]
        
        if self.state["is_sleeping"] and action != "SLEEP":
            self.set_message("Shhh... sleeping!")
            return

        if action == "FEED":
            if self.state["hunger"] >= 100:
                self.set_message("Too full!")
            else:
                self.state["hunger"] = min(100, self.state["hunger"] + 20)
                self.set_message("Yum! +20 Hunger")
        elif action == "PLAY":
            if self.state["energy"] < 10:
                self.set_message("Too tired...")
            else:
                self.state["happiness"] = min(100, self.state["happiness"] + 15)
                self.state["energy"] = max(0, self.state["energy"] - 10)
                self.set_message("Fun! +15 Happy")
        elif action == "SLEEP":
            self.state["is_sleeping"] = not self.state["is_sleeping"]
            self.set_message("Zzz..." if self.state["is_sleeping"] else "Woke up!")
        elif action == "CLEAN":
            self.set_message("Sparkling clean!")

    def set_message(self, text):
        self.message = text
        self.message_time = time.time()

    def get_animated_sprite(self):
        # Determine animation row and max frames
        row = 0
        max_frames = 6
        
        now = time.time()
        # Message-based (action) overrides
        if now - self.message_time < 2:
            if "Yum" in self.message: 
                row = 2 # EATING (Starts on Row 2)
                max_frames = 12 # Row 2 and 3 together
            elif "Woke" in self.message or "Zzz" in self.message:
                row = 0 # Default for now
        
        # State-based
        if self.state["energy"] > 90 and row == 0:
            row = 1 # LOOKING AROUND
        
        # Update frame index based on time
        if now - self.last_frame_time > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % max_frames
            self.last_frame_time = now
            
        # Calculate crop coordinates
        f_col = self.frame_index % 6
        f_row = row + (self.frame_index // 6)
        
        left = f_col * self.cell_w
        top = f_row * self.cell_h
        right = left + self.cell_w
        bottom = top + self.cell_h
        
        sprite = self.anim_sheet.crop((left, top, right, bottom))
        # Remove labels/boxes if possible by shrinking the crop slightly
        sprite = sprite.crop((10, 20, self.cell_w - 10, self.cell_h - 10))
        return sprite.resize((80, 80), Image.NEAREST)

    def draw_pet(self, draw, image):
        cx, cy = 64, 75
        
        if self.anim_sheet:
            try:
                sprite = self.get_animated_sprite()
                # Paste sprite
                pos = (cx - 40, cy - 40)
                image.paste(sprite, pos, sprite)
                return
            except Exception as e:
                pass # Fallback

        # Fallback to simple drawing
        offset = int(math.sin(time.time() * 4) * 3) if not self.state["is_sleeping"] else 0
        # ... (rest of old drawing code)

    def draw(self):
        # Background: Sky or Night
        bg = (30, 30, 60) if self.state["is_sleeping"] else (135, 206, 235)
        image = Image.new("RGB", (self.width, self.height), bg)
        draw = ImageDraw.Draw(image)

        # Draw Stats
        draw.rectangle([5, 5, 123, 25], fill=(0, 0, 0, 100))
        draw.text((10, 8), f"H:{int(self.state['hunger'])} S:{int(self.state['happiness'])} E:{int(self.state['energy'])}", fill="white")
        
        # Progress bars
        def draw_bar(x, y, val, color):
            draw.rectangle([x, y, x+30, y+3], outline="white")
            draw.rectangle([x, y, x+(val*30/100), y+3], fill=color)

        draw_bar(10, 18, self.state['hunger'], "red")
        draw_bar(45, 18, self.state['happiness'], "green")
        draw_bar(80, 18, self.state['energy'], "blue")

        # Draw Pet
        self.draw_pet(draw, image)

        # Draw Message
        if time.time() - self.message_time < 3:
            draw.rectangle([10, 100, 118, 115], fill="white", outline="black")
            draw.text((15, 102), self.message, fill="black")

        # Draw Actions Toolbar
        draw.rectangle([0, 118, 128, 128], fill=(50, 50, 50))
        for i, action in enumerate(self.actions):
            x = i * 32
            if i == self.selected_action:
                draw.rectangle([x, 118, x+32, 128], fill=(100, 100, 100))
            draw.text((x+5, 118), action["icon"], fill="white")
            if i == self.selected_action:
                draw.text((x+5, 105), action["name"], fill="yellow")

        self.display.display(image)

def main(display=None):
    import traceback
    try:
        if display is None:
            from drivers.st7735 import ST7735
            display = ST7735()
            display.init()
            display.rotate(90)
        
        # Ensure GPIO is set up for this module
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, LEFT, RIGHT, KEY1, KEY2, KEY3]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        pet = VirtualPet(display)
        while True:
            pet.update()
            pet.draw()
            if GPIO.input(KEY3) == GPIO.LOW:
                pet.save_state()
                break
            time.sleep(0.05)
    except Exception as e:
        with open("pet_crash.log", "w") as f:
            f.write(traceback.format_exc())
        print(f"PET CRASHED: {e}")

if __name__ == "__main__":
    main()
