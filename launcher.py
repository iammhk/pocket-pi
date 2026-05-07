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
LEFT = 5
RIGHT = 26
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
            {"title": "AI Assistant", "icon": "🤖", "action": self.run_ai_chat},
            {"title": "System Info", "icon": "📊", "action": self.run_sys_info},
            {"title": "Task Manager", "icon": "📝", "action": self.run_task_manager},
            {"title": "Pocket Config", "icon": "🛠️", "action": self.enter_config},
            {"title": "Power", "icon": "⚡", "action": self.enter_power}
        ]
        
        self.games_menu = [
            {"title": "Ping Pong", "icon": "🏓", "action": self.run_pong},
            {"title": "Snake", "icon": "🐍", "action": self.run_snake},
            {"title": "Flappy Bird", "icon": "🐦", "action": self.run_flappy},
            {"title": "Breakout", "icon": "🧱", "action": self.run_breakout},
            {"title": "2048", "icon": "🔢", "action": self.run_2048},
            {"title": "Particle Storm", "icon": "✨", "action": self.run_particles},
            {"title": "Pocket Pet", "icon": "🐶", "action": self.run_pet},
            {"title": "Galacta", "icon": "🚀", "action": self.run_galacta},
            {"title": "Tetris", "icon": "🧱", "action": self.run_tetris},
            {"title": "Back", "icon": "⬅️", "action": self.enter_main}
        ]

        self.power_menu = [
            {"title": "Restart Pocket-Pi", "icon": "🔄", "action": self.restart_gui},
            {"title": "Reboot", "icon": "⚙️", "action": self.reboot_pi},
            {"title": "Shutdown", "icon": "🔌", "action": self.shutdown_pi},
            {"title": "Back", "icon": "⬅️", "action": self.enter_main}
        ]

        self.config_menu = [
            {"title": "WiFi Status", "icon": "📡", "action": self.run_wifi_status},
            {"title": "Bluetooth", "icon": "🔵", "action": self.run_bt_status},
            {"title": "Update Pocket Pi", "icon": "📥", "action": self.run_update},
            {"title": "Keyboard Test", "icon": "⌨️", "action": self.run_keyboard_test},
            {"title": "Rotate Screen", "icon": "🔄", "action": self.run_rotate_config},
            {"title": "Back", "icon": "⬅️", "action": self.enter_main}
        ]
        
        self.current_menu = self.main_menu
        self.selected_index = 0
        self.__init_gpio__()

    def __init_gpio__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, LEFT, RIGHT, PRESS, KEY1, KEY2, KEY3]:
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
        
        # Items with Scrolling Logic
        visible_items = 5
        offset = 0
        if self.selected_index >= visible_items:
            offset = self.selected_index - (visible_items - 1)

        for i, item in enumerate(self.current_menu):
            # Calculate relative position
            idx_rel = i - offset
            y = 30 + idx_rel * 18
            
            # Clip items outside the visible area
            if y < 25 or y > 120:
                continue
                
            color = "white"
            if i == self.selected_index:
                draw.rectangle([5, y-1, 123, y+16], outline=(0, 255, 255), width=1)
                color = (0, 255, 255)
            
            draw.text((15, y+1), f"{item['icon']} {item['title']}", fill=color)
            
        # Scroll Indicators
        if len(self.current_menu) > visible_items:
            if offset > 0:
                draw.polygon([(64, 25), (60, 29), (68, 29)], fill="gray") # Up arrow
            if offset < len(self.current_menu) - visible_items:
                draw.polygon([(64, 125), (60, 121), (68, 121)], fill="gray") # Down arrow
            
        self.disp.display(image)

    def run_pong(self):
        from games import pong
        pong.main(self.disp)
        self.__init_gpio__()

    def run_snake(self):
        from games import snake
        snake.main(self.disp)
        self.__init_gpio__()

    def run_flappy(self):
        from games import flappy
        flappy.main(self.disp)
        self.__init_gpio__()

    def run_breakout(self):
        from games import breakout
        breakout.main(self.disp)
        self.__init_gpio__()

    def run_2048(self):
        from games import game2048
        game2048.main(self.disp)
        self.__init_gpio__()

    def run_particles(self):
        from games import particles
        particles.main(self.disp)
        self.__init_gpio__()

    def run_pet(self):
        from games import pet
        pet.main(self.disp)
        self.__init_gpio__()

    def run_galacta(self):
        from games import galacta
        galacta.main(self.disp)
        self.__init_gpio__()

    def run_tetris(self):
        from games import tetris
        tetris.main(self.disp)
        self.__init_gpio__()

    def run_ai_chat(self):
        from ai import gemini_chat
        gemini_chat.main(self.disp)
        self.__init_gpio__()

    def run_sys_info(self):
        print("Opening System Info...")
        running = True
        while running:
            image = Image.new("RGB", (self.width, self.height), "black")
            draw = ImageDraw.Draw(image)
            
            # Stats
            cpu = psutil.cpu_percent()
            temp = os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", "")
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # WiFi Signal
            try:
                wifi_raw = os.popen("iwconfig wlan0 | grep Quality").read()
                quality = wifi_raw.split("Quality=")[1].split(" ")[0] if "Quality=" in wifi_raw else "0/70"
            except: quality = "N/A"
            
            draw.text((10, 5), "SYSTEM INFO", fill="cyan")
            draw.line([(10, 18), (118, 18)], fill="gray")
            
            draw.text((10, 25), f"CPU: {cpu}%", fill="white")
            draw.text((10, 40), f"Temp: {temp}C", fill="white")
            draw.text((10, 55), f"RAM: {mem}%", fill="white")
            draw.text((10, 70), f"Disk: {disk}%", fill="white")
            draw.text((10, 85), f"WiFi: {quality}", fill="yellow")
            
            # Draw simple bars
            draw.rectangle([70, 28, 70+(cpu/2), 33], fill="red")
            draw.rectangle([70, 58, 70+(mem/2), 63], fill="green")
            draw.rectangle([70, 73, 70+(disk/2), 78], fill="blue")
            
            draw.text((10, 105), "Key3 to Back", fill="gray")
            
            self.disp.display(image)
            
            if GPIO.input(KEY3) == GPIO.LOW or GPIO.input(PRESS) == GPIO.LOW:
                running = False
            time.sleep(0.5)

    def run_task_manager(self):
        print("Opening Task Manager...")
        selected_proc = 0
        running = True
        mem_history = [0] * 20 # For the graph
        
        while running:
            # Get stats
            mem = psutil.virtual_memory().percent
            mem_history.append(mem)
            mem_history = mem_history[-20:]
            
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    procs.append(proc.info)
                except: continue
            
            procs = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:6]
            
            image = Image.new("RGB", (128, 128), (20, 0, 20))
            draw = ImageDraw.Draw(image)
            draw.text((10, 5), "TASK MANAGER", fill="cyan")
            
            # Memory Graph (Sparkline)
            for i in range(len(mem_history)-1):
                x1 = 80 + i * 2
                y1 = 15 - (mem_history[i] / 10)
                x2 = 80 + (i+1) * 2
                y2 = 15 - (mem_history[i+1] / 10)
                draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 0))
            
            draw.line([(10, 18), (118, 18)], fill="gray")
            
            for i, p in enumerate(procs):
                y = 25 + i * 14
                color = "white"
                if i == selected_proc:
                    draw.rectangle([5, y-1, 123, y+12], outline="green")
                    color = "green"
                
                name = p['name'][:8]
                draw.text((10, y), f"{p['pid']} {name} {int(p['cpu_percent'])}% {int(p['memory_percent'])}%", fill=color)
            
            draw.text((5, 110), "K1:Kill K2:Rst K3:Back", fill="yellow")
            self.disp.display(image)
            
            # Inputs
            if GPIO.input(UP) == GPIO.LOW:
                selected_proc = (selected_proc - 1) % len(procs)
                time.sleep(0.15)
            elif GPIO.input(DOWN) == GPIO.LOW:
                selected_proc = (selected_proc + 1) % len(procs)
                time.sleep(0.15)
            elif GPIO.input(KEY1) == GPIO.LOW: # Kill
                os.system(f"sudo kill -9 {procs[selected_proc]['pid']}")
                time.sleep(0.5)
            elif GPIO.input(KEY2) == GPIO.LOW: # Restart (Kill and let systemd or user handle it)
                os.system(f"sudo kill -1 {procs[selected_proc]['pid']}")
                time.sleep(0.5)
            elif GPIO.input(KEY3) == GPIO.LOW:
                running = False
            time.sleep(0.1)

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

    def run_bt_status(self):
        running = True
        while running:
            image = Image.new("RGB", (128, 128), (10, 10, 30))
            draw = ImageDraw.Draw(image)
            
            bt_info = os.popen("bluetoothctl show").read()
            is_powered = "Powered: yes" in bt_info
            status = "ON" if is_powered else "OFF"
            
            draw.text((10, 10), "BLUETOOTH", fill="cyan")
            draw.line([(10, 25), (118, 25)], fill="gray")
            draw.text((10, 40), f"Status: {status}", fill="white")
            draw.text((10, 70), "Key1 to TOGGLE", fill="green")
            draw.text((10, 100), "Key3 to Back", fill="yellow")
            
            self.disp.display(image)
            
            if GPIO.input(KEY1) == GPIO.LOW:
                new_state = "off" if is_powered else "on"
                os.system(f"bluetoothctl power {new_state}")
                time.sleep(0.5)
            elif GPIO.input(KEY3) == GPIO.LOW:
                running = False
            time.sleep(0.1)

    def run_update(self):
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)
        draw.text((10, 40), "UPDATING...", fill="cyan")
        draw.text((10, 60), "Please wait...", fill="white")
        self.disp.display(image)
        
        try:
            # Run git pull
            res = os.popen("git pull").read()
            
            image = Image.new("RGB", (self.width, self.height), "black")
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "UPDATE RESULT", fill="green")
            
            if "Already up to date" in res:
                draw.text((10, 40), "No updates found.", fill="white")
            else:
                draw.text((10, 40), "Update Success!", fill="green")
                draw.text((10, 60), "Restarting GUI...", fill="yellow")
                self.disp.display(image)
                time.sleep(2)
                self.restart_gui()
                return
            
            draw.text((10, 100), "Key3 to Back", fill="yellow")
            self.disp.display(image)
            while GPIO.input(KEY3) == GPIO.HIGH:
                time.sleep(0.1)
        except Exception as e:
            image = Image.new("RGB", (self.width, self.height), "black")
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "UPDATE ERROR", fill="red")
            draw.text((10, 40), str(e)[:20], fill="white")
            draw.text((10, 100), "Key3 to Back", fill="yellow")
            self.disp.display(image)
            while GPIO.input(KEY3) == GPIO.HIGH:
                time.sleep(0.1)
        self.__init_gpio__()

    def run_keyboard_test(self):
        from utils.keyboard import VirtualKeyboard
        kb = VirtualKeyboard(self.disp)
        result = kb.get_input()
        
        if result is not None:
            image = Image.new("RGB", (128, 128), "black")
            draw = ImageDraw.Draw(image)
            draw.text((10, 40), "You Typed:", fill="cyan")
            draw.text((10, 60), result, fill="white")
            draw.text((10, 100), "Key3 to Exit", fill="yellow")
            self.disp.display(image)
            while GPIO.input(KEY3) == GPIO.HIGH:
                time.sleep(0.1)
        self.__init_gpio__()

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
        draw.text((20, 60), "RESTARTING POCKET-PI...", fill="white")
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
