# Pocket Pi 🎮
# This file is part of the actual project. It provides an overview and instructions for the Pocket Pi repository.

A lightweight handheld gaming and utility platform built for the Raspberry Pi Zero 2 W using the Waveshare 1.44" LCD HAT.

## 🚀 Features
- **Custom ST7735 Driver**: Optimized Python driver for the 1.44" (128x128) TFT LCD.
- **Rotation Support**: Easy screen orientation management (0, 90, 180, 270 degrees).
- **Pong Demo**: A smooth 50 FPS implementation of the classic Ping-Pong game using the HAT's joystick and buttons.
- **AI Assistant**: Integrated Gemini 3 Flash Preview chatbot for on-the-go assistance (requires WiFi and API Key).

## 🛠️ Hardware Requirements
- Raspberry Pi Zero / Zero 2 W
- [Waveshare 1.44inch LCD HAT](https://www.waveshare.com/wiki/1.44inch_LCD_HAT) (ST7735S controller)

## 📦 Installation

### 1. Enable SPI
Open the configuration tool:
```bash
sudo raspi-config
```
Navigate to **Interfacing Options** > **SPI** > **Yes**. Reboot your Pi.

### 2. Configure GPIO Pull-ups
For the buttons to work correctly, add the following line to the bottom of your `/boot/config.txt` (or `/boot/firmware/config.txt`):
```text
gpio=6,19,5,26,13,21,20,16=pu
```

### 3. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install python3-pil python3-spidev python3-rpi.gpio -y
```

## 🎮 Usage
To run the Pong game demo:
```bash
sudo python3 launcher.py
```

### AI Assistant Setup
To use the AI Assistant:
1. Obtain a Gemini API Key from the [Google AI Studio](https://aistudio.google.com/).
2. Edit `pocket_config.json` in the root directory.
3. Replace `YOUR_API_KEY_HERE` with your actual API Key.
4. Ensure your Pocket Pi is connected to WiFi.

### Controls
- **Joystick UP/DOWN**: Move the player paddle.
- **Key 1**: Reset the game after a Game Over.

## 📂 Project Structure
- `pong.py`: Main game logic and entry point.
- `drivers/`:
    - `st7735.py`: Display driver with SPI communication and initialization logic.
- `test_pattern.py`: Simple diagnostic script to verify display output.

## 📝 License
This project is open-source and free to use.
