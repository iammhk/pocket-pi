# games/flappy.py
# This file is part of the actual project. It implements a Flappy Bird clone for the Pocket-Pi.

import time
import random
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
from drivers.st7735 import ST7735

# Pins (Matches Waveshare 1.44" LCD HAT)
UP = 6
DOWN = 19
LEFT = 5
RIGHT = 26
KEY1 = 21
KEY2 = 20
KEY3 = 16

class FlappyGame:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.reset()

    def reset(self):
        self.bird_y = 64
        self.bird_x = 30
        self.velocity = 0
        self.gravity = 0.5
        self.flap_strength = -5
        self.pipes = [] # Each pipe is [x, gap_y]
        self.spawn_timer = 0
        self.score = 0
        self.game_over = False
        self.last_flap_time = 0

    def spawn_pipe(self):
        gap_y = random.randint(30, 90)
        self.pipes.append([self.width, gap_y])

    def update(self):
        if self.game_over:
            if GPIO.input(KEY1) == GPIO.LOW:
                self.reset()
            return

        # Flap Input
        current_time = time.time()
        if (GPIO.input(UP) == GPIO.LOW or GPIO.input(KEY1) == GPIO.LOW) and (current_time - self.last_flap_time > 0.15):
            self.velocity = self.flap_strength
            self.last_flap_time = current_time

        # Physics
        self.velocity += self.gravity
        self.bird_y += self.velocity

        # Ground/Ceiling collision
        if self.bird_y > self.height - 5 or self.bird_y < 0:
            self.game_over = True

        # Pipes logic
        self.spawn_timer += 1
        if self.spawn_timer > 30:
            self.spawn_pipe()
            self.spawn_timer = 0

        for pipe in self.pipes:
            pipe[0] -= 3 # Move left

            # Collision Detection
            # Pipe width is 15, Gap is 40
            if (pipe[0] < self.bird_x + 5 < pipe[0] + 15):
                if not (pipe[1] - 20 < self.bird_y < pipe[1] + 20):
                    self.game_over = True

            # Scoring
            if pipe[0] + 15 < self.bird_x and len(pipe) == 2:
                self.score += 1
                pipe.append(True) # Mark as scored

        # Remove old pipes
        self.pipes = [p for p in self.pipes if p[0] > -20]

    def draw(self):
        # Using a sky blue background
        image = Image.new("RGB", (self.width, self.height), (135, 206, 235))
        draw = ImageDraw.Draw(image)

        # Draw Pipes
        for pipe in self.pipes:
            # Top pipe
            draw.rectangle([pipe[0], 0, pipe[0] + 15, pipe[1] - 20], fill=(34, 139, 34))
            # Bottom pipe
            draw.rectangle([pipe[0], pipe[1] + 20, pipe[0] + 15, self.height], fill=(34, 139, 34))

        # Draw Bird (Yellow circle)
        draw.ellipse([self.bird_x - 4, self.bird_y - 4, self.bird_x + 4, self.bird_y + 4], fill="yellow", outline="black")

        # Draw Score
        draw.text((5, 5), f"Score: {self.score}", fill="black")

        if self.game_over:
            # Semi-transparent overlay style (drawn as rectangle)
            draw.text((35, 50), "CRASHED!", fill="red")
            draw.text((25, 70), f"Score: {self.score}", fill="black")
            draw.text((15, 90), "Press KEY1 to Flap", fill="blue")

        self.display.display(image)

def main(display=None):
    if display is None:
        from drivers.st7735 import ST7735
        display = ST7735()
        display.init()
        display.rotate(90)
    
    game = FlappyGame(display)
    
    try:
        # Pre-initialize GPIO for buttons (usually done in launcher, but for standalone)
        GPIO.setmode(GPIO.BCM)
        for pin in [UP, DOWN, LEFT, RIGHT, KEY1, KEY2, KEY3]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        while True:
            game.update()
            game.draw()
            time.sleep(0.04) # ~25 FPS
            
            if GPIO.input(KEY3) == GPIO.LOW:
                break
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
