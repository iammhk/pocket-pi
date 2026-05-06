# games/snake.py
# This file is part of the actual project. It implements a Snake game for the Pocket-Pi.

import time
import random
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
from drivers.st7735 import ST7735

# Pins
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
KEY1, KEY2, KEY3 = 21, 20, 16

class SnakeGame:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.grid_size = 8
        self.reset()

    def reset(self):
        self.snake = [(64, 64), (56, 64), (48, 64)]
        self.direction = (8, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            food = (random.randint(0, (self.width // self.grid_size) - 1) * self.grid_size,
                    random.randint(0, (self.height // self.grid_size) - 1) * self.grid_size)
            if food not in self.snake:
                return food

    def update(self):
        if self.game_over:
            if GPIO.input(KEY1) == GPIO.LOW:
                self.reset()
            return

        # Input
        if GPIO.input(UP) == GPIO.LOW and self.direction != (0, 8):
            self.direction = (0, -8)
        elif GPIO.input(DOWN) == GPIO.LOW and self.direction != (0, -8):
            self.direction = (0, 8)
        elif GPIO.input(LEFT) == GPIO.LOW and self.direction != (8, 0):
            self.direction = (-8, 0)
        elif GPIO.input(RIGHT) == GPIO.LOW and self.direction != (-8, 0):
            self.direction = (8, 0)

        # Move
        new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

        # Wall Collision
        if (new_head[0] < 0 or new_head[0] >= self.width or 
            new_head[1] < 0 or new_head[1] >= self.height or 
            new_head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Food Collision
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        # Draw Food
        draw.rectangle([self.food[0], self.food[1], self.food[0]+7, self.food[1]+7], fill="red")

        # Draw Snake
        for i, segment in enumerate(self.snake):
            color = "green" if i == 0 else (0, 200, 0)
            draw.rectangle([segment[0], segment[1], segment[0]+7, segment[1]+7], fill=color)

        # Draw Score
        draw.text((5, 5), f"Score: {self.score}", fill="white")

        if self.game_over:
            draw.text((30, 50), "GAME OVER", fill="red")
            draw.text((20, 70), "Press Key1 to Retry", fill="yellow")

        self.display.display(image)

def main(display=None):
    if display is None:
        from drivers.st7735 import ST7735
        display = ST7735()
        display.init()
        display.rotate(90)
    
    game = SnakeGame(display)
    
    try:
        while True:
            game.update()
            game.draw()
            time.sleep(0.1)
            
            if game.game_over and GPIO.input(KEY1) == GPIO.LOW:
                game.reset()
            
            if GPIO.input(KEY3) == GPIO.LOW:
                break
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
