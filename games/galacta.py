# games/galacta.py
# This file is part of the actual project. It implements a simple space shooter for the Pocket-Pi.

import time
import random
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
from drivers.st7735 import ST7735

# Pins
LEFT, RIGHT = 5, 26
PRESS = 13 # Also Shoot
KEY1, KEY2, KEY3 = 21, 20, 16

class GalactaGame:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.reset()

    def reset(self):
        self.player_x = 60
        self.player_y = 110
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.last_enemy_spawn = 0

    def update(self):
        if self.game_over:
            if GPIO.input(KEY1) == GPIO.LOW or GPIO.input(PRESS) == GPIO.LOW: # Press to restart
                self.reset()
            return

        # Player Move
        if GPIO.input(LEFT) == GPIO.LOW: self.player_x -= 3
        if GPIO.input(RIGHT) == GPIO.LOW: self.player_x += 3
        self.player_x = max(0, min(120, self.player_x))

        # Shooting
        if GPIO.input(PRESS) == GPIO.LOW or GPIO.input(KEY1) == GPIO.LOW:
            if len(self.bullets) < 5:
                self.bullets.append([self.player_x + 4, self.player_y])
                time.sleep(0.1) # Debounce

        # Update Bullets
        for b in self.bullets[:]:
            b[1] -= 5
            if b[1] < 0: self.bullets.remove(b)

        # Spawn Enemies
        if time.time() - self.last_enemy_spawn > 1.5:
            self.enemies.append([random.randint(0, 120), 0])
            self.last_enemy_spawn = time.time()

        # Update Enemies
        for e in self.enemies[:]:
            e[1] += 2
            if e[1] > 128: self.enemies.remove(e)
            
            # Collision with Player
            if (abs(e[0] - self.player_x) < 8 and abs(e[1] - self.player_y) < 8):
                self.game_over = True

            # Collision with Bullets
            for b in self.bullets[:]:
                if (abs(e[0] - b[0]) < 8 and abs(e[1] - b[1]) < 8):
                    self.score += 10
                    if e in self.enemies: self.enemies.remove(e)
                    if b in self.bullets: self.bullets.remove(b)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), (0, 0, 20))
        draw = ImageDraw.Draw(image)

        # Starfield
        for _ in range(10):
            draw.point((random.randint(0, 127), random.randint(0, 127)), fill="white")

        # Player
        draw.polygon([(self.player_x, self.player_y+8), (self.player_x+4, self.player_y), (self.player_x+8, self.player_y+8)], fill="cyan")

        # Bullets
        for b in self.bullets:
            draw.rectangle([b[0], b[1], b[0]+1, b[1]+3], fill="yellow")

        # Enemies
        for e in self.enemies:
            draw.rectangle([e[0], e[1], e[0]+8, e[1]+8], fill="red")

        draw.text((5, 5), f"Score: {self.score}", fill="white")

        if self.game_over:
            draw.text((30, 50), "GAME OVER", fill="red")
            draw.text((20, 70), "Press SELECT to Retry", fill="yellow")

        self.display.display(image)

def main():
    disp = ST7735()
    disp.init()
    disp.rotate(90)
    game = GalactaGame(disp)
    
    try:
        while True:
            game.update()
            game.draw()
            time.sleep(0.03)
            
            # Key 3: Back / Exit
            if GPIO.input(KEY3) == GPIO.LOW:
                break
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
