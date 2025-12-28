# MechDog ESP32 Setup & Control

Complete setup for MechDog robotics platform with dual Bluetooth and WiFi IoT control.

## Overview

This repository contains programs and tools for controlling the Hiwonder MechDog robot via both **Bluetooth** and **WiFi IoT** simultaneously, plus utility scripts for serial communication with the ESP32-C3-Mini-1 IoT module.

## Features

### ✅ Dual Control System
- **Bluetooth Control**: Original APP-based control with robotic arm support
- **WiFi IoT Control**: Remote IoT features including sensors, camera, and remote commands
- **Simultaneous Operation**: Both systems run concurrently without conflicts

### 🤖 Supported Capabilities

#### Bluetooth Features
- Movement control (forward, backward, turning, speed adjustment)
- Robotic arm control (3 servos: base, arm, gripper)
- Obstacle avoidance mode
- Self-balancing mode
- Ultrasonic distance sensor
- RGB LED control
- Battery monitoring

#### WiFi IoT Features
- WiFi hotspot (SSID: `NIOT_MechDog`, Password: `12345678`)
- ESP32-S3 camera integration (face detection, color recognition)
- Remote sensor monitoring (distance, impact detection)
- Remote RGB LED control
- Remote buzzer control
- Remote action commands
- Real-time sensor data streaming

## Files

### Main Programs (for MechDog)

#### `main_bluetooth_wifi.py` ⭐ **RECOMMENDED**
Combined program that runs **both Bluetooth and WiFi IoT** simultaneously.

**Upload this to your MechDog as `main.py`**

Features:
- 4 concurrent threads handling all operations
- Bluetooth app control
- WiFi hotspot with IoT features
- ESP32-S3 camera processing
- Unified sensor management
- Robotic arm control

**Usage:**
```bash
# Upload to MechDog
ampy --port /dev/ttyUSB0 put main_bluetooth_wifi.py /main.py

# Then power cycle the robot
```

#### `main_iot.py`
WiFi IoT-only version (from official Hiwonder tutorials).

Use this if you only need WiFi/IoT features without Bluetooth.

### Utility Scripts (for PC)

#### `IoT.py`
Full-featured serial communication interface for ESP32-C3-Mini-1.

Interactive commands:
- `wifi SSID [PASS]` - Configure WiFi hotspot
- `face [on/off]` - Face detection alerts
- `obj [on/off]` - Unknown object detection
- `impact [on/off]` - Impact detection
- `color [on/off]` - Color recognition
- `distance [on/off]` - Distance sensor readings
- `rgb R G B` - Set RGB LED color (0-255 each)
- `buzz [on/off]` - Buzzer control
- `action TYPE NUM` - Run predefined actions
- `query` - Query ESP32S3 camera type
- `raw TEXT` - Send custom commands

**Usage:**
```bash
python3 IoT.py
# or specify port
python3 IoT.py /dev/ttyUSB0
```

#### `setup_hotspot.py`
Quick WiFi hotspot configuration script.

**Usage:**
```bash
python3 setup_hotspot.py
```

Configures:
- SSID: `NIOT_MechDog`
- Password: `12345678`

#### `stable_hotspot.py`
Enhanced hotspot setup with stability checks and monitoring.

**Usage:**
```bash
# Setup hotspot with retries
python3 stable_hotspot.py

# Or with custom credentials
python3 stable_hotspot.py MyDog MyPassword123

# Monitor mode
python3 stable_hotspot.py monitor
```

### Legacy Programs

- `main.py` - Original Bluetooth control
- `main_working.py` - Bluetooth with robotic arm extensions
- `main_original.py` - Factory default program

## Hardware Setup

### ESP32-C3-Mini-1 IoT Module
- Connected via I2C (address 0x69)
- Serial port: `/dev/ttyUSB0` (typically)
- Baudrate: 115200

### ESP32-S3 Camera Module (Optional)
- Connected via I2C (address 0x52)
- Supports face detection and color recognition

### Ultrasonic Sensor
- Connected via I2C
- Provides distance measurements

### IMU (MPU)
- Connected via I2C
- Provides impact/tilt detection

## Installation

### Requirements
```bash
pip install pyserial adafruit-ampy
```

### Upload to MechDog

1. **Connect via USB** to the MechDog's serial port

2. **Upload the combined program:**
   ```bash
   cd /path/to/mechdog
   ampy --port /dev/ttyUSB0 put main_bluetooth_wifi.py /main.py
   ```

3. **Power cycle the MechDog** (turn off and on)

4. **Verify both systems:**
   - Bluetooth: Look for `MechDog_XX` in Bluetooth devices
   - WiFi: Look for `NIOT_MechDog` in WiFi networks (password: `12345678`)

## Usage

### Bluetooth Control
1. Install the official MechDog app on your phone
2. Enable Bluetooth
3. Connect to `MechDog_XX` (where XX is the device MAC suffix)
4. Use the app for direct robot control

### WiFi IoT Control
1. Connect your phone/PC to the `NIOT_MechDog` WiFi network
2. Password: `12345678`
3. Use the IoT Control app or send commands via serial

### Serial Communication
Use the PC utility scripts to:
- Configure WiFi settings
- Monitor sensor data
- Send test commands
- Debug the robot

## Architecture

### Thread Structure
The combined program runs 4 concurrent threads:

1. **`wifi_main()`** - WiFi IoT communication
   - Handles WiFi commands from IoT app
   - Manages sensor data transmission
   - Processes ESP32S3 requests

2. **`esp32s3_main()`** - Camera processing
   - Face detection
   - Color recognition
   - Camera data streaming

3. **`start_main()`** - Bluetooth control
   - APP command processing
   - Direct robot control
   - Battery monitoring

4. **`start_main1()`** - Motion & sensors
   - Movement execution
   - Sensor reading
   - Robotic arm control
   - Obstacle avoidance
   - Self-balancing

### Communication Protocols

#### WiFi IoT Commands
Format: `CMD|type|param1|param2|...|$`

Command types:
- `0x01` - Warnings (face, object, impact)
- `0x02` - Color detection
- `0x03` - Sensor distance
- `0x04` - RGB LED control
- `0x05` - Buzzer control
- `0x06` - Action control
- `0x07` - ESP32S3 type query

#### Bluetooth Commands
Standard Hiwonder MechDog protocol via BLE UART.

## Troubleshooting

### WiFi Hotspot Unstable
- Check ESP32-C3 power connections
- Ensure battery is fully charged
- Verify proper IoT module wiring
- Try re-running `stable_hotspot.py`
- Make sure `main_bluetooth_wifi.py` is running on the MechDog

### Can't Upload to MechDog
```bash
# Check available ports
ls -la /dev/ttyUSB* /dev/ttyACM*

# Test connection
ampy --port /dev/ttyUSB0 ls

# If busy, try resetting
# Disconnect any serial monitors first
```

### Both Systems Not Working
1. Verify `main_bluetooth_wifi.py` is uploaded as `/main.py`
2. Power cycle the robot completely
3. Wait 10-15 seconds after boot for initialization
4. Check serial output for errors

### Serial Permission Denied
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Then log out and back in
```

## Development

### Project Structure
```
mechdog/
├── main_bluetooth_wifi.py   # Combined BT + WiFi (MAIN)
├── main_iot.py              # IoT-only version
├── IoT.py                   # PC serial interface
├── setup_hotspot.py         # Quick WiFi setup
├── stable_hotspot.py        # Enhanced WiFi setup
├── main_working.py          # Legacy BT with arm
└── main_original.py         # Factory default
```

### Adding New Features

To add features to the combined program:
1. Add shared variables at the top
2. Implement logic in appropriate thread
3. Use global keyword for shared state
4. Avoid blocking operations in threads

### Testing

```bash
# Monitor MechDog output
python3 -m serial.tools.miniterm /dev/ttyUSB0 115200

# Test WiFi setup
python3 stable_hotspot.py

# Interactive testing
python3 IoT.py
```

## Credits

- Based on Hiwonder MechDog tutorials and examples
- Combined implementation by GitHub Copilot
- ESP32-C3 and ESP32-S3 integration

## License

This project uses Hiwonder's official code as a base. Please refer to Hiwonder's licensing for commercial use.

## Support

For issues specific to:
- **Hardware**: Consult Hiwonder MechDog documentation
- **Software modifications**: Open an issue in this repository
- **Original firmware**: Contact Hiwonder support

## Changelog

### 2025-12-28
- ✨ Created combined Bluetooth + WiFi IoT program
- ✨ Added PC serial communication utilities
- ✨ Implemented stable WiFi hotspot configuration
- ✨ Integrated ESP32-S3 camera support
- 📝 Comprehensive documentation
- 🐛 Fixed WiFi hotspot stability issues

---

**Happy robot hacking! 🤖**
