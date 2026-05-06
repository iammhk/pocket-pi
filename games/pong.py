# pong.py
# This file is part of the actual project. It implements a simple Ping-Pong game to test the LCD and buttons.

import time
import random
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from drivers.st7735 import ST7735

# Button Pins
UP_PIN = 6
DOWN_PIN = 19
KEY1_PIN = 21 # Enter / Retry
KEY2_PIN = 20
KEY3_PIN = 16 # Back

class PongGame:
    def __init__(self, display):
        self.display = display
        self.width = 128
        self.height = 128
        
        # Game state
        self.paddle_width = 4
        self.paddle_height = 20
        self.ball_size = 4
        
        self.reset_game()
        
        # GPIO Setup for buttons
        GPIO.setup(UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def reset_game(self):
        self.player_y = self.height // 2 - self.paddle_height // 2
        self.ai_y = self.height // 2 - self.paddle_height // 2
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = 3 if random.random() > 0.5 else -3
        self.ball_dy = random.randint(-3, 3)
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            if GPIO.input(KEY1_PIN) == GPIO.LOW:
                self.reset_game()
            return

        # Player Movement
        if GPIO.input(UP_PIN) == GPIO.LOW:
            self.player_y -= 4
        if GPIO.input(DOWN_PIN) == GPIO.LOW:
            self.player_y += 4
        
        # Clamp player
        self.player_y = max(0, min(self.height - self.paddle_height, self.player_y))
        
        # AI Movement (Simple follow)
        if self.ai_y + self.paddle_height // 2 < self.ball_y:
            self.ai_y += 2
        else:
            self.ai_y -= 2
        self.ai_y = max(0, min(self.height - self.paddle_height, self.ai_y))
        
        # Ball Movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Bounce off top/bottom
        if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_size:
            self.ball_dy *= -1
            
        # Collision with Player Paddle
        if (self.ball_x <= self.paddle_width and 
            self.player_y <= self.ball_y <= self.player_y + self.paddle_height):
            self.ball_dx *= -1
            self.ball_x = self.paddle_width + 1
            # Add some spin based on where it hit the paddle
            self.ball_dy += (self.ball_y - (self.player_y + self.paddle_height / 2)) / 5
            
        # Collision with AI Paddle
        if (self.ball_x >= self.width - self.paddle_width - self.ball_size and 
            self.ai_y <= self.ball_y <= self.ai_y + self.paddle_height):
            self.ball_dx *= -1
            self.ball_x = self.width - self.paddle_width - self.ball_size - 1
            
        # Scoring
        if self.ball_x < 0:
            self.ai_score += 1
            self.respawn_ball()
        elif self.ball_x > self.width:
            self.player_score += 1
            self.respawn_ball()
            
        if self.player_score >= 5 or self.ai_score >= 5:
            self.game_over = True

    def respawn_ball(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx *= -1
        self.ball_dy = random.randint(-2, 2)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)
        
        # Draw Center Line
        for i in range(0, self.height, 8):
            draw.line([(self.width // 2, i), (self.width // 2, i + 4)], fill="gray")
            
        # Draw Paddles
        draw.rectangle([0, self.player_y, self.paddle_width, self.player_y + self.paddle_height], fill="white")
        draw.rectangle([self.width - self.paddle_width, self.ai_y, self.width, self.ai_y + self.paddle_height], fill="white")
        
        # Draw Ball
        draw.ellipse([self.ball_x, self.ball_y, self.ball_x + self.ball_size, self.ball_y + self.ball_size], fill="yellow")
        
        # Draw Score
        draw.text((self.width // 4, 10), str(self.player_score), fill="white")
        draw.text((3 * self.width // 4, 10), str(self.ai_score), fill="white")
        
        if self.game_over:
            winner = "PLAYER" if self.player_score >= 5 else "AI"
            draw.text((20, 50), f"GAME OVER", fill="red")
            draw.text((25, 70), f"{winner} WINS!", fill="green")
            draw.text((10, 100), "Press KEY1 to Reset", fill="blue")
            
        self.display.display(image)

def main():
    print("Starting Pong Game Demo...")
    disp = ST7735()
    disp.init()
    
    # Set rotation (0, 90, 180, or 270)
    disp.rotate(90)
    
    game = PongGame(disp)
    
    try:
        while True:
            game.update()
            game.draw()
            time.sleep(0.02) # ~50 FPS
            
            # Key 3: Back / Exit
            if GPIO.input(KEY3_PIN) == GPIO.LOW:
                break
    except KeyboardInterrupt:
        print("\nStopping game.")
        disp.clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
