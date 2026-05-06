# drivers/st7735.py
# This file is part of the actual project. It provides a driver for the ST7735S 1.44" LCD.

import time
import spidev
import RPi.GPIO as GPIO

class ST7735:
    def __init__(self):
        # Pin definitions (Waveshare 1.44" LCD HAT)
        self.DC = 25
        self.RST = 27
        self.CS = 8
        self.BL = 24
        
        # SPI setup
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 9000000
        self.spi.mode = 0b00
        
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.DC, GPIO.OUT)
        GPIO.setup(self.RST, GPIO.OUT)
        GPIO.setup(self.CS, GPIO.OUT)
        GPIO.setup(self.BL, GPIO.OUT)
        GPIO.output(self.BL, GPIO.HIGH)
        
        self.width = 128
        self.height = 128
        self.column_offset = 2 # As per Waveshare wiki for 128x128
        self.row_offset = 1

    def command(self, cmd):
        GPIO.output(self.DC, GPIO.LOW)
        self.spi.writebytes([cmd])

    def data(self, val):
        GPIO.output(self.DC, GPIO.HIGH)
        self.spi.writebytes([val])

    def reset(self):
        GPIO.output(self.RST, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.RST, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.RST, GPIO.HIGH)
        time.sleep(0.01)

    def init(self):
        self.reset()
        
        # Initialization sequence for ST7735S
        self.command(0x11) # Sleep out
        time.sleep(0.12)
        
        # ST7735S Specific initialization
        self.command(0xB1); self.data(0x01); self.data(0x2C); self.data(0x2D)
        self.command(0xB2); self.data(0x01); self.data(0x2C); self.data(0x2D)
        self.command(0xB3); self.data(0x01); self.data(0x2C); self.data(0x2D); self.data(0x01); self.data(0x2C); self.data(0x2D)
        
        self.command(0xB4); self.data(0x07) # Column inversion
        
        self.command(0xC0); self.data(0xA2); self.data(0x02); self.data(0x84)
        self.command(0xC1); self.data(0xC5)
        self.command(0xC2); self.data(0x0A); self.data(0x00)
        self.command(0xC3); self.data(0x8A); self.data(0x2A)
        self.command(0xC4); self.data(0x8A); self.data(0xEE)
        
        self.command(0xC5); self.data(0x0E) # VCOM
        
        self.command(0x36); self.data(0xC0) # MX, MY, RGB mode (C0 = 128x128 default)
        
        self.command(0xE0) # Gamma +
        self.data(0x02); self.data(0x1c); self.data(0x07); self.data(0x12)
        self.data(0x37); self.data(0x32); self.data(0x29); self.data(0x2d)
        self.data(0x29); self.data(0x25); self.data(0x2B); self.data(0x39)
        self.data(0x00); self.data(0x01); self.data(0x03); self.data(0x10)
        
        self.command(0xE1) # Gamma -
        self.data(0x03); self.data(0x1d); self.data(0x07); self.data(0x06)
        self.data(0x2E); self.data(0x2C); self.data(0x29); self.data(0x2D)
        self.data(0x2E); self.data(0x2E); self.data(0x37); self.data(0x3F)
        self.data(0x00); self.data(0x00); self.data(0x02); self.data(0x10)
        
        self.command(0x3A); self.data(0x05) # 16-bit color
        self.command(0x29) # Display ON

    def set_window(self, x0, y0, x1, y1):
        x0 += self.column_offset
        x1 += self.column_offset
        y0 += self.row_offset
        y1 += self.row_offset
        
        self.command(0x2A) # Column address set
        self.data(0x00); self.data(x0)
        self.data(0x00); self.data(x1)
        
        self.command(0x2B) # Row address set
        self.data(0x00); self.data(y0)
        self.data(0x00); self.data(y1)
        
        self.command(0x2C) # Write to RAM

    def display(self, image):
        """ image: PIL Image object """
        im_width, im_height = image.size
        if im_width != self.width or im_height != self.height:
            image = image.resize((self.width, self.height))
            
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Convert RGB888 to RGB565
        pix = image.load()
        buffer = []
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = pix[x, y]
                # RGB565: 5 bits Red, 6 bits Green, 5 bits Blue
                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                buffer.append((color >> 8) & 0xFF)
                buffer.append(color & 0xFF)
        
        # Send in chunks to SPI
        chunk_size = 4096
        for i in range(0, len(buffer), chunk_size):
            self.spi.writebytes(buffer[i:i+chunk_size])

    def clear(self, color=(0, 0, 0)):
        from PIL import Image
        image = Image.new("RGB", (self.width, self.height), color)
        self.display(image)
