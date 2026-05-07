# games/breakout.py
# This file is part of the actual project. It implements a Breakout clone for the Pocket-Pi.

import time
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
import random

# Pins
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
KEY1, KEY2, KEY3 = 21, 20, 16

class BreakoutGame:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.reset()

    def reset(self):
        # Paddle
        self.paddle_w = 24
        self.paddle_h = 4
        self.paddle_x = (self.width - self.paddle_w) // 2
        self.paddle_y = self.height - 15
        
        # Ball
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = random.choice([-2, 2])
        self.ball_dy = -2
        self.ball_radius = 2
        
        # Bricks
        self.bricks = []
        rows = 4
        cols = 6
        bw = 18
        bh = 6
        padding = 2
        offset_x = (self.width - (cols * (bw + padding))) // 2
        offset_y = 20
        
        colors = ["red", "orange", "yellow", "green"]
        for r in range(rows):
            for c in range(cols):
                bx = offset_x + c * (bw + padding)
                by = offset_y + r * (bh + padding)
                self.bricks.append({"rect": [bx, by, bx + bw, by + bh], "color": colors[r]})
        
        self.score = 0
        self.game_over = False
        self.win = False

    def update(self):
        if self.game_over or self.win:
            if GPIO.input(KEY1) == GPIO.LOW:
                self.reset()
            return

        # Paddle Movement
        if GPIO.input(LEFT) == GPIO.LOW:
            self.paddle_x -= 4
        if GPIO.input(RIGHT) == GPIO.LOW:
            self.paddle_x += 4
        self.paddle_x = max(0, min(self.width - self.paddle_w, self.paddle_x))

        # Ball Movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Wall Collisions
        if self.ball_x <= 0 or self.ball_x >= self.width:
            self.ball_dx *= -1
        if self.ball_y <= 0:
            self.ball_dy *= -1
        
        # Ground Collision (Lose)
        if self.ball_y >= self.height:
            self.game_over = True

        # Paddle Collision
        if (self.paddle_y <= self.ball_y + self.ball_radius <= self.paddle_y + self.paddle_h and
            self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_w):
            self.ball_dy *= -1
            # Add some English/spin based on hit location
            hit_pos = (self.ball_x - (self.paddle_x + self.paddle_w / 2)) / (self.paddle_w / 2)
            self.ball_dx += hit_pos * 2
            # Limit dx
            self.ball_dx = max(-4, min(4, self.ball_dx))

        # Brick Collisions
        for brick in self.bricks[:]:
            r = brick["rect"]
            if (r[0] <= self.ball_x <= r[2] and r[1] <= self.ball_y <= r[3]):
                self.bricks.remove(brick)
                self.ball_dy *= -1
                self.score += 10
                break
        
        if not self.bricks:
            self.win = True

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        # Bricks
        for brick in self.bricks:
            draw.rectangle(brick["rect"], fill=brick["color"], outline="white")

        # Paddle
        draw.rectangle([self.paddle_x, self.paddle_y, self.paddle_x + self.paddle_w, self.paddle_y + self.paddle_h], fill="blue")

        # Ball
        draw.ellipse([self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, 
                      self.ball_x + self.ball_radius, self.ball_y + self.ball_radius], fill="white")

        # Score
        draw.text((5, 5), f"Score: {self.score}", fill="white")

        if self.game_over:
            draw.text((35, 60), "GAME OVER", fill="red")
            draw.text((25, 80), "Press K1 to Reset", fill="yellow")
        elif self.win:
            draw.text((40, 60), "YOU WIN!", fill="green")
            draw.text((25, 80), "Press K1 to Play Again", fill="yellow")

        self.display.display(image)

def main(display=None):
    if display is None:
        from drivers.st7735 import ST7735
        display = ST7735()
        display.init()
        display.rotate(90)
    
    game = BreakoutGame(display)
    
    try:
        while True:
            game.update()
            game.draw()
            time.sleep(0.03) # ~33 FPS
            
            if GPIO.input(KEY3) == GPIO.LOW:
                break
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
