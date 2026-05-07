# games/pet.py
# This file is part of the actual project. It implements a virtual pet (Tamagotchi-like) game for the Pocket-Pi.

import time
import json
import os
import RPi.GPIO as GPIO
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

    def load_state(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    self.state = json.load(f)
                    # Check for time elapsed
                    elapsed = time.time() - self.state.get("last_saved", time.time())
                    # Decay stats based on time (1 point per 5 mins for hunger/happiness)
                    decay = elapsed / 300
                    self.state["hunger"] = max(0, self.state["hunger"] - decay)
                    self.state["happiness"] = max(0, self.state["happiness"] - decay)
                    if self.state.get("is_sleeping", False):
                        self.state["energy"] = min(100, self.state["energy"] + (elapsed / 60))
                    else:
                        self.state["energy"] = max(0, self.state["energy"] - (elapsed / 600))
            except:
                self.default_state()
        else:
            self.default_state()

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

    def draw_pet(self, draw):
        cx, cy = 64, 70
        # Simple bouncing animation
        offset = int(math.sin(time.time() * 4) * 3) if not self.state["is_sleeping"] else 0
        
        # Body
        body_color = (100, 200, 100) if self.state["happiness"] > 50 else (150, 150, 150)
        draw.ellipse([cx-20, cy-15+offset, cx+20, cy+15+offset], fill=body_color, outline="black")
        
        if not self.state["is_sleeping"]:
            # Eyes
            draw.ellipse([cx-10, cy-5+offset, cx-6, cy-1+offset], fill="black")
            draw.ellipse([cx+6, cy-5+offset, cx+10, cy-1+offset], fill="black")
            # Mouth
            if self.state["hunger"] < 30:
                draw.line([cx-5, cy+5+offset, cx+5, cy+5+offset], fill="black") # Flat
            else:
                draw.arc([cx-5, cy+2+offset, cx+5, cy+8+offset], 0, 180, fill="black") # Smile
        else:
            # Sleeping eyes
            draw.line([cx-10, cy-3, cx-6, cy-3], fill="black")
            draw.line([cx+6, cy-3, cx+10, cy-3], fill="black")
            draw.text((cx+15, cy-20), "Z", fill="white")
            draw.text((cx+22, cy-28), "z", fill="white")

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
        import math
        self.draw_pet(draw)

        # Draw Message
        if time.time() - self.message_time < 3:
            draw.rectangle([10, 100, 118, 115], fill="white", outline="black")
            draw.text((15, 102), self.message, fill="black")

        # Draw Actions Toolbar
        draw.rectangle([0, 118, 128, 128], fill=(50, 50, 50))
        for i, action in enumerate(self.actions):
            x = i * 32
            if i == self.selected_index:
                draw.rectangle([x, 118, x+32, 128], fill=(100, 100, 100))
            draw.text((x+5, 118), action["icon"], fill="white")
            if i == self.selected_index:
                draw.text((x+5, 105), action["name"], fill="yellow")

        self.display.display(image)

def main(display=None):
    if display is None:
        from drivers.st7735 import ST7735
        display = ST7735()
        display.init()
        display.rotate(90)
    
    pet = VirtualPet(display)
    try:
        while True:
            pet.update()
            pet.draw()
            if GPIO.input(KEY3) == GPIO.LOW:
                pet.save_state()
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        pet.save_state()

if __name__ == "__main__":
    main()
