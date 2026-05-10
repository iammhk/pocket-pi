# Pocket Pi 🎮
# This file is part of the actual project. It provides an overview and instructions for the Pocket Pi repository.

A lightweight handheld gaming and utility platform built for the Raspberry Pi Zero 2 W using the Waveshare 1.44" LCD HAT.

## 🚀 Features
- **Multi-Game Launcher**: A scrollable menu system to launch games and utilities.
- **Camera App**: Live preview and photo capture with 90° software rotation.
- **Photo Gallery**: Browse your clicked photos directly on the device.
- **Custom ST7735 Driver**: Optimized Python driver for the 1.44" (128x128) TFT LCD.
- **AI Assistant**: Gemini-powered chatbot for on-the-go assistance.
- **Games Suite**: Includes Pong, Snake, Tetris, Flappy Bird, and more!

## 🛠️ Hardware Requirements
- Raspberry Pi Zero / Zero 2 W
- [Waveshare 1.44inch LCD HAT](https://www.waveshare.com/wiki/1.44inch_LCD_HAT)
- Raspberry Pi Camera v1.3 (OV5647) or v2.1 (IMX219)

## 📦 Installation

### 1. Enable SPI & Camera
Open the configuration tool:
```bash
sudo raspi-config
```
1. Navigate to **Interfacing Options** > **SPI** > **Yes**.
2. Navigate to **Interfacing Options** > **Legacy Camera** > **No** (Ensure libcamera is enabled).
3. Reboot your Pi.

### 2. Configure Camera Overlay
For Pi Cam v1.3, edit `/boot/firmware/config.txt` and ensure the following:
```text
camera_auto_detect=0
dtoverlay=ov5647
gpio=6,19,5,26,13,21,20,16=pu
```

### 3. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install python3-pil python3-spidev python3-rpi.gpio python3-picamera2 -y
```

## 🎮 Usage
Start the main launcher:
```bash
sudo python3 launcher.py
```

### Camera Controls
- **Joystick Press**: Capture Photo.
- **Key 1**: Capture Photo.
- **Key 2**: Open Gallery.
- **Key 3**: Exit App.
- **Gallery Mode**: Use **UP/DOWN** to navigate, **Key 1** to return.

### AI Assistant Setup
1. Obtain a Gemini API Key from [Google AI Studio](https://aistudio.google.com/).
2. Edit `pocket_config.json` and replace the placeholder with your API Key.

## 📂 Project Structure
- `launcher.py`: Main GUI and menu system.
- `games/`: Collection of retro games ported for the 128x128 display.
- `utils/`: 
    - `camera_app.py`: Camera preview, capture, and gallery logic.
- `drivers/`:
    - `st7735.py`: Optimized ST7735 display driver.

## 📝 License
This project is open-source and free to use.
