# games/tetris.py
# This file is part of the actual project. It implements a Tetris game for the Pocket Pi.

import time
import random
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw

# Pins (Consistent with launcher.py)
UP, DOWN, LEFT, RIGHT = 6, 19, 5, 26
PRESS, KEY1, KEY2, KEY3 = 13, 21, 20, 16

class TetrisGame:
    def __init__(self, display):
        self.display = display
        self.width, self.height = 128, 128
        self.grid_w, self.grid_h = 10, 20
        self.block_size = 5
        self.offset_x = (self.width - self.grid_w * self.block_size) // 2
        self.offset_y = 10
        
        self.shapes = [
            [[1, 1, 1, 1]], # I
            [[1, 1], [1, 1]], # O
            [[0, 1, 0], [1, 1, 1]], # T
            [[0, 1, 1], [1, 1, 0]], # S
            [[1, 1, 0], [0, 1, 1]], # Z
            [[1, 0, 0], [1, 1, 1]], # J
            [[0, 0, 1], [1, 1, 1]]  # L
        ]
        self.colors = ["cyan", "yellow", "purple", "green", "red", "blue", "orange"]
        
        self.reset_game()

    def reset_game(self):
        self.grid = [[None for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self.score = 0
        self.game_over = False
        self.new_piece()

    def new_piece(self):
        self.curr_shape_idx = random.randint(0, len(self.shapes) - 1)
        self.curr_shape = self.shapes[self.curr_shape_idx]
        self.curr_color = self.colors[self.curr_shape_idx]
        self.curr_x = self.grid_w // 2 - len(self.curr_shape[0]) // 2
        self.curr_y = 0
        
        if self.check_collision(self.curr_x, self.curr_y, self.curr_shape):
            self.game_over = True

    def rotate(self, shape):
        return [list(row) for row in zip(*shape[::-1])]

    def check_collision(self, x, y, shape):
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x, new_y = x + col_idx, y + row_idx
                    if (new_x < 0 or new_x >= self.grid_w or 
                        new_y >= self.grid_h or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False

    def freeze_piece(self):
        for row_idx, row in enumerate(self.curr_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    self.grid[self.curr_y + row_idx][self.curr_x + col_idx] = self.curr_color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = self.grid_h - len(new_grid)
        self.score += lines_cleared * 100
        while len(new_grid) < self.grid_h:
            new_grid.insert(0, [None for _ in range(self.grid_w)])
        self.grid = new_grid

    def update(self):
        if self.game_over:
            if GPIO.input(KEY1) == GPIO.LOW:
                self.reset_game()
            return

        # Input handling
        if GPIO.input(LEFT) == GPIO.LOW:
            if not self.check_collision(self.curr_x - 1, self.curr_y, self.curr_shape):
                self.curr_x -= 1
            time.sleep(0.1)
        elif GPIO.input(RIGHT) == GPIO.LOW:
            if not self.check_collision(self.curr_x + 1, self.curr_y, self.curr_shape):
                self.curr_x += 1
            time.sleep(0.1)
        elif GPIO.input(DOWN) == GPIO.LOW:
            if not self.check_collision(self.curr_x, self.curr_y + 1, self.curr_shape):
                self.curr_y += 1
            time.sleep(0.05)
        elif GPIO.input(PRESS) == GPIO.LOW or GPIO.input(KEY1) == GPIO.LOW:
            rotated = self.rotate(self.curr_shape)
            if not self.check_collision(self.curr_x, self.curr_y, rotated):
                self.curr_shape = rotated
            time.sleep(0.2)

        # Automatic drop
        if not hasattr(self, 'last_drop'): self.last_drop = time.time()
        if time.time() - self.last_drop > 0.5:
            if not self.check_collision(self.curr_x, self.curr_y + 1, self.curr_shape):
                self.curr_y += 1
            else:
                self.freeze_piece()
            self.last_drop = time.time()

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), (10, 10, 10))
        draw = ImageDraw.Draw(image)
        
        # Draw Border
        draw.rectangle([self.offset_x - 1, self.offset_y - 1, 
                        self.offset_x + self.grid_w * self.block_size, 
                        self.offset_y + self.grid_h * self.block_size], outline="gray")
        
        # Draw Grid
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    draw.rectangle([self.offset_x + x * self.block_size, 
                                    self.offset_y + y * self.block_size, 
                                    self.offset_x + (x+1) * self.block_size - 1, 
                                    self.offset_y + (y+1) * self.block_size - 1], fill=color)
        
        # Draw Current Piece
        if not self.game_over:
            for row_idx, row in enumerate(self.curr_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        draw.rectangle([self.offset_x + (self.curr_x + col_idx) * self.block_size, 
                                        self.offset_y + (self.curr_y + row_idx) * self.block_size, 
                                        self.offset_x + (self.curr_x + col_idx + 1) * self.block_size - 1, 
                                        self.offset_y + (self.curr_y + row_idx + 1) * self.block_size - 1], fill=self.curr_color)
        
        # UI
        draw.text((5, 2), f"SCORE: {self.score}", fill="white")
        if self.game_over:
            draw.text((30, 60), "GAME OVER", fill="red")
            draw.text((20, 80), "Press K1 to Reset", fill="yellow")
            
        self.display.display(image)

def main(display):
    game = TetrisGame(display)
    while True:
        game.update()
        game.draw()
        if GPIO.input(KEY3) == GPIO.LOW:
            break
        time.sleep(0.02)
