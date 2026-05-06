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
KEY1 = 21
KEY2 = 20
KEY3 = 16

class Launcher:
    def __init__(self):
        self.disp = ST7735()
        self.disp.init()
        self.disp.rotate(90)
        
        self.width = 128
        self.height = 128
        
        # Menu Definitions
        self.main_menu = [
            {"title": "Games", "icon": "🎮", "action": self.enter_games},
            {"title": "System Info", "icon": "📊", "action": self.run_sys_info},
            {"title": "Pocket Config", "icon": "🛠️", "action": self.enter_config},
            {"title": "Power", "icon": "⚡", "action": self.enter_power},
            {"title": "Exit GUI", "icon": "🚪", "action": exit}
        ]
        
        self.games_menu = [
            {"title": "Ping Pong", "icon": "🏓", "action": self.run_pong},
            {"title": "Snake", "icon": "🐍", "action": self.run_snake},
            {"title": "Galacta", "icon": "🚀", "action": self.run_galacta},
            {"title": "Back", "icon": "⬅️", "action": self.enter_main}
        ]

        self.power_menu = [
            {"title": "Restart GUI", "icon": "🔄", "action": self.restart_gui},
            {"title": "Reboot", "icon": "⚙️", "action": self.reboot_pi},
            {"title": "Shutdown", "icon": "🔌", "action": self.shutdown_pi},
            {"title": "Back", "icon": "⬅️", "action": self.enter_main}
        ]

        self.config_menu = [
            {"title": "WiFi Status", "icon": "📡", "action": self.run_wifi_status},
            {"title": "Rotate Screen", "icon": "🔄", "action": self.run_rotate_config},
            {"title": "Back", "icon": "⬅️", "action": self.enter_main}
        ]
        
        self.current_menu = self.main_menu
        self.selected_index = 0
        self.__init_gpio__()

    def __init_gpio__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, PRESS, KEY1, KEY2, KEY3]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def enter_games(self):
        self.current_menu = self.games_menu
        self.selected_index = 0

    def enter_power(self):
        self.current_menu = self.power_menu
        self.selected_index = 0

    def enter_config(self):
        self.current_menu = self.config_menu
        self.selected_index = 0

    def enter_main(self):
        self.current_menu = self.main_menu
        self.selected_index = 0

    def show_splash(self):
        try:
            logo = Image.open("assets/logo.png").resize((128, 128))
            self.disp.display(logo)
            time.sleep(2)
        except Exception as e:
            print(f"Splash error: {e}")
            self.disp.clear((20, 20, 40))

    def draw_menu(self):
        image = Image.new("RGB", (self.width, self.height), (10, 10, 20))
        draw = ImageDraw.Draw(image)
        
        # Header
        if self.current_menu == self.main_menu:
            title = "POCKET PI"
        elif self.current_menu == self.games_menu:
            title = "GAMES"
        elif self.current_menu == self.power_menu:
            title = "POWER"
        else:
            title = "CONFIG"
            
        draw.rectangle([0, 0, 128, 20], fill=(40, 40, 80))
        draw.text((35, 4), title, fill="white")
        
        # Items
        for i, item in enumerate(self.current_menu):
            y = 30 + i * 18
            color = "white"
            if i == self.selected_index:
                draw.rectangle([5, y-1, 123, y+16], outline=(0, 255, 255), width=1)
                color = (0, 255, 255)
            
            draw.text((15, y+1), f"{item['icon']} {item['title']}", fill=color)
            
        self.disp.display(image)

    def run_pong(self):
        from games import pong
        pong.main(self.disp)
        self.__init_gpio__()

    def run_snake(self):
        from games import snake
        snake.main(self.disp)
        self.__init_gpio__()

    def run_galacta(self):
        from games import galacta
        galacta.main(self.disp)
        self.__init_gpio__()

    def run_sys_info(self):
        print("Opening System Info...")
        running = True
        while running:
            image = Image.new("RGB", (self.width, self.height), "black")
            draw = ImageDraw.Draw(image)
            
            cpu = psutil.cpu_percent()
            temp = os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", "")
            mem = psutil.virtual_memory().percent
            
            draw.text((10, 10), "SYSTEM INFO", fill="cyan")
            draw.line([(10, 25), (118, 25)], fill="gray")
            
            draw.text((10, 40), f"CPU: {cpu}%", fill="white")
            draw.text((10, 55), f"Temp: {temp}C", fill="white")
            draw.text((10, 70), f"RAM: {mem}%", fill="white")
            
            draw.text((10, 100), "Key1 to Back", fill="yellow")
            
            self.disp.display(image)
            
            if GPIO.input(KEY1) == GPIO.LOW or GPIO.input(PRESS) == GPIO.LOW:
                running = False
            time.sleep(0.5)

    def run_wifi_status(self):
        running = True
        while running:
            image = Image.new("RGB", (128, 128), "black")
            draw = ImageDraw.Draw(image)
            
            ssid = os.popen("iwgetid -r").read().strip() or "Not Connected"
            ip = socket.gethostbyname(socket.gethostname())
            
            draw.text((10, 10), "WIFI STATUS", fill="cyan")
            draw.line([(10, 25), (118, 25)], fill="gray")
            draw.text((10, 40), f"SSID: {ssid}", fill="white")
            draw.text((10, 60), f"IP: {ip}", fill="white")
            draw.text((10, 100), "Key3 to Back", fill="yellow")
            
            self.disp.display(image)
            if GPIO.input(KEY3) == GPIO.LOW or GPIO.input(KEY1) == GPIO.LOW:
                running = False
            time.sleep(0.5)

    def run_rotate_config(self):
        rotations = [0, 90, 180, 270]
        curr_idx = rotations.index(self.disp.rotation) if self.disp.rotation in rotations else 1
        
        running = True
        while running:
            image = Image.new("RGB", (128, 128), (20, 20, 20))
            draw = ImageDraw.Draw(image)
            
            draw.text((10, 10), "ROTATE SCREEN", fill="cyan")
            draw.text((10, 40), f"Current: {rotations[curr_idx]}", fill="white")
            draw.text((10, 60), "Use UP/DOWN", fill="gray")
            draw.text((10, 80), "Key1 to SAVE", fill="green")
            draw.text((10, 100), "Key3 to Cancel", fill="red")
            
            self.disp.display(image)
            
            if GPIO.input(UP) == GPIO.LOW:
                curr_idx = (curr_idx - 1) % 4
                time.sleep(0.2)
            elif GPIO.input(DOWN) == GPIO.LOW:
                curr_idx = (curr_idx + 1) % 4
                time.sleep(0.2)
            elif GPIO.input(KEY1) == GPIO.LOW:
                self.disp.rotate(rotations[curr_idx])
                running = False
            elif GPIO.input(KEY3) == GPIO.LOW:
                running = False
            time.sleep(0.05)

    def reboot_pi(self):
        self.disp.clear((0, 0, 255))
        image = Image.new("RGB", (128, 128), "blue")
        draw = ImageDraw.Draw(image)
        draw.text((30, 60), "REBOOTING...", fill="white")
        self.disp.display(image)
        time.sleep(1)
        os.system("sudo reboot")

    def restart_gui(self):
        self.disp.clear((0, 255, 0))
        image = Image.new("RGB", (128, 128), "green")
        draw = ImageDraw.Draw(image)
        draw.text((30, 60), "RESTARTING...", fill="white")
        self.disp.display(image)
        time.sleep(0.5)
        os.system("sudo systemctl restart pocket-pi.service")

    def shutdown_pi(self):
        self.disp.clear((255, 0, 0))
        image = Image.new("RGB", (128, 128), "red")
        draw = ImageDraw.Draw(image)
        draw.text((30, 60), "SHUTTING DOWN...", fill="white")
        self.disp.display(image)
        time.sleep(1)
        os.system("sudo poweroff")

    def main_loop(self):
        self.show_splash()
        last_move = 0
        
        while True:
            self.draw_menu()
            
            # Global Key Listeners
            if GPIO.input(KEY1) == GPIO.LOW: # OK / Enter
                self.current_menu[self.selected_index]["action"]()
                last_move = time.time()
                
            if GPIO.input(KEY2) == GPIO.LOW: # Main Menu (Home)
                self.enter_main()
                last_move = time.time()
                
            if GPIO.input(KEY3) == GPIO.LOW: # Back
                if self.current_menu != self.main_menu:
                    self.enter_main()
                last_move = time.time()

            if time.time() - last_move > 0.15:
                if GPIO.input(UP) == GPIO.LOW:
                    self.selected_index = (self.selected_index - 1) % len(self.current_menu)
                    last_move = time.time()
                elif GPIO.input(DOWN) == GPIO.LOW:
                    self.selected_index = (self.selected_index + 1) % len(self.current_menu)
                    last_move = time.time()
                elif GPIO.input(PRESS) == GPIO.LOW: # Also OK
                    self.current_menu[self.selected_index]["action"]()
                    last_move = time.time()
                    
            time.sleep(0.05)


if __name__ == "__main__":
    launcher = Launcher()
    launcher.main_loop()
