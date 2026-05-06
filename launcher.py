# launcher.py
# This file is the main GUI for the Pocket-Pi. It handles the splash screen and the scrollable menu.

import time
import os
import socket
import psutil
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from drivers.st7735 import ST7735

# Button Pins
UP = 6
DOWN = 19
PRESS = 13

class Launcher:
    def __init__(self):
        self.disp = ST7735()
        self.disp.init()
        self.disp.rotate(90)
        
        self.width = 128
        self.height = 128
        
        # Menu Items
        self.menu_items = [
            {"title": "Ping Pong", "icon": "🏓", "action": self.run_pong},
            {"title": "System Info", "icon": "📊", "action": self.run_sys_info},
            {"title": "Settings", "icon": "⚙️", "action": self.run_settings},
            {"title": "Exit", "icon": "🚪", "action": exit}
        ]
        self.selected_index = 0
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, PRESS]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def show_splash(self):
        try:
            logo = Image.open("assets/logo.png").resize((128, 128))
            self.disp.display(logo)
            time.sleep(2)
        except Exception as e:
            print(f"Splash error: {e}")
            self.disp.clear((20, 20, 40)) # Fallback color

    def draw_menu(self):
        image = Image.new("RGB", (self.width, self.height), (10, 10, 20))
        draw = ImageDraw.Draw(image)
        
        # Header
        draw.rectangle([0, 0, 128, 20], fill=(40, 40, 80))
        draw.text((35, 4), "POCKET PI", fill="white")
        
        # Items
        for i, item in enumerate(self.menu_items):
            y = 30 + i * 24
            color = "white"
            if i == self.selected_index:
                draw.rectangle([5, y-2, 123, y+20], outline=(0, 255, 255), width=2)
                color = (0, 255, 255)
            
            draw.text((15, y+2), f"{item['icon']} {item['title']}", fill=color)
            
        self.disp.display(image)

    def run_pong(self):
        import pong
        # We need to re-initialize pins because pong cleanup might have happened
        pong.main()
        # After returning, re-init launcher pins
        self.__init_gpio__()

    def run_sys_info(self):
        running = True
        while running:
            image = Image.new("RGB", (self.width, self.height), "black")
            draw = ImageDraw.Draw(image)
            
            # Stats
            cpu = psutil.cpu_percent()
            temp = os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", "")
            mem = psutil.virtual_memory().percent
            ip = socket.gethostbyname(socket.gethostname())
            
            draw.text((10, 10), "SYSTEM INFO", fill="cyan")
            draw.line([(10, 25), (118, 25)], fill="gray")
            
            draw.text((10, 40), f"CPU: {cpu}%", fill="white")
            draw.text((10, 55), f"Temp: {temp}C", fill="white")
            draw.text((10, 70), f"RAM: {mem}%", fill="white")
            draw.text((10, 85), f"IP: {ip}", fill="yellow")
            draw.text((10, 110), "Press SELECT to return", fill="gray")
            
            self.disp.display(image)
            
            if GPIO.input(PRESS) == GPIO.LOW:
                running = False
            time.sleep(0.5)

    def run_settings(self):
        # Placeholder for settings
        pass

    def __init_gpio__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, PRESS]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def main_loop(self):
        self.show_splash()
        last_move = 0
        
        while True:
            self.draw_menu()
            
            if time.time() - last_move > 0.2:
                if GPIO.input(UP) == GPIO.LOW:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    last_move = time.time()
                elif GPIO.input(DOWN) == GPIO.LOW:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    last_move = time.time()
                elif GPIO.input(PRESS) == GPIO.LOW:
                    self.menu_items[self.selected_index]["action"]()
                    last_move = time.time()
                    
            time.sleep(0.05)

if __name__ == "__main__":
    launcher = Launcher()
    launcher.main_loop()
