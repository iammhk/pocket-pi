# games/2048.py
# This file is part of the actual project. It implements a 2048 clone for the Pocket-Pi.

import time
import random
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from drivers.st7735 import ST7735

# Pins
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
KEY1, KEY2, KEY3 = 21, 20, 16

class Game2048:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.grid_size = 4
        self.cell_size = 30
        self.padding = 2
        self.offset = (self.width - (self.grid_size * self.cell_size)) // 2
        
        self.colors = {
            0: (204, 192, 179),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46)
        }
        
        self.reset()

    def reset(self):
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.score = 0
        self.game_over = False
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.grid[r][c] = 2 if random.random() < 0.9 else 4

    def compress(self, row):
        new_row = [i for i in row if i != 0]
        new_row += [0] * (len(row) - len(new_row))
        return new_row

    def merge(self, row):
        for i in range(len(row) - 1):
            if row[i] != 0 and row[i] == row[i+1]:
                row[i] *= 2
                self.score += row[i]
                row[i+1] = 0
        return row

    def move_left(self):
        moved = False
        for i in range(self.grid_size):
            old_row = self.grid[i][:]
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.merge(self.grid[i])
            self.grid[i] = self.compress(self.grid[i])
            if old_row != self.grid[i]:
                moved = True
        return moved

    def rotate_grid(self):
        self.grid = [list(row) for row in zip(*self.grid[::-1])]

    def move(self, direction):
        moved = False
        if direction == "LEFT":
            moved = self.move_left()
        elif direction == "RIGHT":
            self.rotate_grid()
            self.rotate_grid()
            moved = self.move_left()
            self.rotate_grid()
            self.rotate_grid()
        elif direction == "UP":
            self.rotate_grid()
            self.rotate_grid()
            self.rotate_grid()
            moved = self.move_left()
            self.rotate_grid()
        elif direction == "DOWN":
            self.rotate_grid()
            moved = self.move_left()
            self.rotate_grid()
            self.rotate_grid()
            self.rotate_grid()
        
        if moved:
            self.add_new_tile()
            if not self.can_move():
                self.game_over = True
        return moved

    def can_move(self):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.grid[r][c] == 0: return True
                if c < self.grid_size - 1 and self.grid[r][c] == self.grid[r][c+1]: return True
                if r < self.grid_size - 1 and self.grid[r][c] == self.grid[r+1][c]: return True
        return False

    def update(self):
        if self.game_over:
            if GPIO.input(KEY1) == GPIO.LOW:
                self.reset()
            return

        if GPIO.input(UP) == GPIO.LOW:
            self.move("UP")
            time.sleep(0.2)
        elif GPIO.input(DOWN) == GPIO.LOW:
            self.move("DOWN")
            time.sleep(0.2)
        elif GPIO.input(LEFT) == GPIO.LOW:
            self.move("LEFT")
            time.sleep(0.2)
        elif GPIO.input(RIGHT) == GPIO.LOW:
            self.move("RIGHT")
            time.sleep(0.2)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), (187, 173, 160))
        draw = ImageDraw.Draw(image)
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                val = self.grid[r][c]
                color = self.colors.get(val, (60, 58, 50))
                x1 = self.offset + c * self.cell_size + self.padding
                y1 = self.offset + r * self.cell_size + self.padding
                x2 = x1 + self.cell_size - self.padding * 2
                y2 = y1 + self.cell_size - self.padding * 2
                
                draw.rectangle([x1, y1, x2, y2], fill=color)
                if val != 0:
                    text_color = "black" if val < 8 else "white"
                    # Simple center text
                    tsize = 10 if val < 100 else 7
                    draw.text((x1 + 5, y1 + 10), str(val), fill=text_color)
        
        draw.text((5, 2), f"Score: {self.score}", fill="white")
        if self.game_over:
            draw.text((35, 60), "GAME OVER", fill="red")
            draw.text((25, 80), "Press K1 to Reset", fill="yellow")
            
        self.display.display(image)

def main(display=None):
    if display is None:
        from drivers.st7735 import ST7735
        display = ST7735()
        display.init()
        display.rotate(90)
    
    game = Game2048(display)
    try:
        while True:
            game.update()
            game.draw()
            if GPIO.input(KEY3) == GPIO.LOW:
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
