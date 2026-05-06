# ai/gemini_chat.py
# This file is part of the actual project. It implements the AI Assistant functionality using the Gemini API.

import time
import json
import os
import requests
import textwrap
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from utils.keyboard import VirtualKeyboard

# Pins (consistent with launcher.py)
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
PRESS, KEY1, KEY2, KEY3 = 13, 21, 20, 16

class GeminiAssistant:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.config_path = "pocket_config.json"
        self.api_key = self._load_api_key()
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/openai/v1/chat/completions"
        self.history = []

    def _load_api_key(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    key = config.get("GEMINI_API_KEY")
                    if key and key != "YOUR_API_KEY_HERE":
                        return key
            return None
        except Exception as e:
            print(f"Config load error: {e}")
            return None

    def draw_status(self, text, color="white"):
        image = Image.new("RGB", (self.width, self.height), (20, 20, 40))
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "AI ASSISTANT", fill="cyan")
        draw.line([(10, 25), (118, 25)], fill="gray")
        
        # Wrap status text
        lines = textwrap.wrap(text, width=20)
        for i, line in enumerate(lines):
            draw.text((10, 40 + i * 15), line, fill=color)
            
        draw.text((10, 110), "Key3 to Exit", fill="yellow")
        self.display.display(image)

    def draw_response(self, response_text, scroll_y=0):
        image = Image.new("RGB", (self.width, self.height), (10, 10, 25))
        draw = ImageDraw.Draw(image)
        
        # Header with Gradient-like bar
        for i in range(20):
            draw.line([(0, i), (128, i)], fill=(40+i, 40+i, 80+i))
        draw.text((30, 4), "GEMINI ASSISTANT", fill="white")
        
        # Wrap the response
        lines = []
        for p in response_text.split('\n'):
            if not p:
                lines.append("")
                continue
            lines.extend(textwrap.wrap(p, width=21))
        
        line_height = 13
        visible_lines = 6
        
        for i, line in enumerate(lines):
            y = 28 + i * line_height - scroll_y
            if 20 < y < 110:
                draw.text((5, y), line, fill=(220, 220, 255))
        
        # Scroll indicator (sleeker)
        if len(lines) > 0:
            total_h = len(lines) * line_height
            view_h = 80
            if total_h > view_h:
                bar_h = max(10, int((view_h / total_h) * 80))
                bar_y = 25 + int((scroll_y / (total_h - view_h)) * (80 - bar_h)) if total_h > view_h else 25
                draw.rectangle([125, bar_y, 127, bar_y + bar_h], fill=(0, 255, 255))

        # Footer
        draw.rectangle([0, 110, 128, 128], fill=(30, 30, 60))
        draw.text((5, 114), "K1:Ask  K2:Clr  K3:Back", fill=(0, 255, 0))
        
        self.display.display(image)
        return len(lines)

    def ask_gemini(self, prompt):
        if not self.api_key:
            return "Error: No API Key found. Please add your Gemini API Key to pocket_config.json"

        self.draw_status("Thinking...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gemini-3-flash",
            "messages": self.history + [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            # Update history
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": answer})
            if len(self.history) > 10: self.history = self.history[-10:]
            
            return answer
        except Exception as e:
            return f"API Error: {str(e)}"

    def run(self):
        if not self.api_key:
            self.draw_status("API Key Missing! Edit pocket_config.json", color="red")
            while GPIO.input(KEY3) == GPIO.HIGH:
                time.sleep(0.1)
            return

        last_response = "Hello! I am your AI assistant. Press Key 1 to ask me anything."
        scroll_y = 0
        num_lines = 0
        
        while True:
            num_lines = self.draw_response(last_response, scroll_y)
            
            # Input Handling
            if GPIO.input(KEY1) == GPIO.LOW: # Ask
                kb = VirtualKeyboard(self.display)
                prompt = kb.get_input()
                if prompt:
                    last_response = self.ask_gemini(prompt)
                    scroll_y = 0
                time.sleep(0.2)
                
            elif GPIO.input(KEY2) == GPIO.LOW: # Clear
                self.history = []
                last_response = "History cleared. Ask me something!"
                scroll_y = 0
                time.sleep(0.2)
                
            elif GPIO.input(KEY3) == GPIO.LOW: # Back
                break
                
            elif GPIO.input(UP) == GPIO.LOW:
                scroll_y = max(0, scroll_y - 13)
                time.sleep(0.1)
                
            elif GPIO.input(DOWN) == GPIO.LOW:
                max_scroll = max(0, num_lines * 13 - 80)
                scroll_y = min(max_scroll, scroll_y + 13)
                time.sleep(0.1)
                
            time.sleep(0.05)

def main(display):
    assistant = GeminiAssistant(display)
    assistant.run()
