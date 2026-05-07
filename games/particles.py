# games/particles.py
# This file is part of the actual project. It implements an interactive Particle Storm visualizer for the Pocket-Pi.

import time
import random
import math
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
from drivers.st7735 import ST7735

# Pins
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
KEY1, KEY2, KEY3 = 21, 20, 16

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.life = random.randint(50, 100)

class ParticleStorm:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.reset()

    def reset(self):
        self.particles = []
        self.max_particles = 100
        self.attractor_x = self.width // 2
        self.attractor_y = self.height // 2
        self.mode = 0 # 0: Attract, 1: Repel, 2: Orbit
        self.modes = ["ATTRACT", "REPEL", "ORBIT"]
        
        for _ in range(self.max_particles):
            self.particles.append(Particle(random.randint(0, 127), random.randint(0, 127)))

    def update(self):
        # Joystick controls attractor
        speed = 4
        if GPIO.input(UP) == GPIO.LOW: self.attractor_y -= speed
        if GPIO.input(DOWN) == GPIO.LOW: self.attractor_y += speed
        if GPIO.input(LEFT) == GPIO.LOW: self.attractor_x -= speed
        if GPIO.input(RIGHT) == GPIO.LOW: self.attractor_x += speed
        
        self.attractor_x = max(0, min(self.width, self.attractor_x))
        self.attractor_y = max(0, min(self.height, self.attractor_y))

        # Mode toggle
        if GPIO.input(KEY1) == GPIO.LOW:
            self.mode = (self.mode + 1) % len(self.modes)
            time.sleep(0.2)

        # Update particles
        for p in self.particles:
            dx = self.attractor_x - p.x
            dy = self.attractor_y - p.y
            dist_sq = dx*dx + dy*dy + 100
            dist = math.sqrt(dist_sq)
            
            force = 0.5
            if self.mode == 0: # Attract
                p.vx += (dx / dist) * force
                p.vy += (dy / dist) * force
            elif self.mode == 1: # Repel
                p.vx -= (dx / dist) * force * 2
                p.vy -= (dy / dist) * force * 2
            elif self.mode == 2: # Orbit
                p.vx += (dy / dist) * force
                p.vy -= (dx / dist) * force

            # Friction
            p.vx *= 0.98
            p.vy *= 0.98
            
            p.x += p.vx
            p.y += p.vy
            
            # Bounce off walls
            if p.x < 0 or p.x > 127: p.vx *= -0.8; p.x = max(0, min(127, p.x))
            if p.y < 0 or p.y > 127: p.vy *= -0.8; p.y = max(0, min(127, p.y))

    def draw(self):
        # Create image with slight fade for trails (motion blur effect)
        # Note: Real motion blur requires keeping the previous frame, which is slow in PIL.
        # So we'll just draw dots.
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        # Draw Attractor
        color = "cyan" if self.mode == 0 else "red" if self.mode == 1 else "yellow"
        draw.ellipse([self.attractor_x - 3, self.attractor_y - 3, 
                      self.attractor_x + 3, self.attractor_y + 3], outline=color)

        # Draw Particles
        for p in self.particles:
            # Color based on velocity
            speed = math.sqrt(p.vx**2 + p.vy**2)
            r = min(255, int(speed * 40))
            g = min(255, 100 + int(speed * 20))
            b = 255 - r
            draw.point((int(p.x), int(p.y)), fill=(r, g, b))

        # UI
        draw.text((5, 5), f"MODE: {self.modes[self.mode]}", fill="white")
        draw.text((5, 115), "K1: Mode  K3: Back", fill="gray")

        self.display.display(image)

def main(display=None):
    if display is None:
        from drivers.st7735 import ST7735
        display = ST7735()
        display.init()
        display.rotate(90)
    
    game = ParticleStorm(display)
    try:
        while True:
            game.update()
            game.draw()
            if GPIO.input(KEY3) == GPIO.LOW:
                break
            # No sleep or very short sleep for smooth animation
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
