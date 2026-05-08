# utils/extract_sprites.py
# This script is used to extract individual frames from a sprite sheet.
# Frames are separated by transparent pixels as per the USER's logic.

import os
from PIL import Image

def extract_sprites(input_path, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load image and ensure it has an alpha channel
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pix = img.load()

    print(f"Image loaded: {width}x{height}")

    # 1. Find Horizontal Rows
    # A row is non-empty if at least one pixel has alpha > 0
    row_mask = []
    for y in range(height):
        is_empty = True
        for x in range(width):
            if pix[x, y][3] > 0: # Alpha channel check
                is_empty = False
                break
        row_mask.append(not is_empty)

    # Group consecutive non-empty rows into sprite rows
    sprite_rows = []
    start_y = None
    for y in range(height):
        if row_mask[y] and start_y is None:
            start_y = y
        elif not row_mask[y] and start_y is not None:
            sprite_rows.append((start_y, y))
            start_y = None
    if start_y is not None:
        sprite_rows.append((start_y, height))

    print(f"Detected {len(sprite_rows)} rows of sprites.")

    frame_count = 0

    # 2. Find Frames in each row
    for row_idx, (y1, y2) in enumerate(sprite_rows):
        col_mask = []
        for x in range(width):
            is_empty = True
            for y in range(y1, y2):
                if pix[x, y][3] > 0:
                    is_empty = False
                    break
            col_mask.append(not is_empty)

        # Group consecutive non-empty columns into frames
        frames_in_row = []
        start_x = None
        for x in range(width):
            if col_mask[x] and start_x is None:
                start_x = x
            elif not col_mask[x] and start_x is not None:
                frames_in_row.append((start_x, x))
                start_x = None
        if start_x is not None:
            frames_in_row.append((start_x, width))

        # Save frames
        for f_x1, f_x2 in frames_in_row:
            # Crop the sprite
            sprite = img.crop((f_x1, y1, f_x2, y2))
            
            # Save to output directory
            output_path = os.path.join(output_dir, f"{frame_count}.png")
            sprite.save(output_path)
            frame_count += 1

    print(f"Successfully extracted {frame_count} frames to '{output_dir}'.")

if __name__ == "__main__":
    input_sheet = "assets/Pokemon (#001-025).png"
    output_folder = "assets/extracted_pokemon"
    extract_sprites(input_sheet, output_folder)
