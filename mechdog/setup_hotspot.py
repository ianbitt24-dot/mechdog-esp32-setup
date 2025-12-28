#!/usr/bin/env python3
"""Quick script to setup MechDog WiFi hotspot"""

import serial
import time

# Connect to ESP32-C3-Mini-1
port = '/dev/ttyUSB0'
baudrate = 115200

print(f"Connecting to {port}...")
ser = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)

# Configure WiFi hotspot
ssid = "MechDog"
password = "12345678"
config_str = f"NIOT_{ssid}|||{password}$$$\n"

print(f"Setting up WiFi hotspot...")
print(f"  SSID: NIOT_{ssid}")
print(f"  Password: {password}")

ser.write(config_str.encode('utf-8'))
ser.flush()

print("\nWiFi hotspot configured!")
print("Waiting for hotspot to activate...")
time.sleep(3)

print("\nYou should now see 'NIOT_MechDog' when searching for WiFi networks on your phone.")
print("Password: 12345678")

# Read any response
if ser.in_waiting > 0:
    response = ser.read(ser.in_waiting)
    print(f"\nResponse: {response.decode('utf-8', errors='ignore')}")

ser.close()
print("\nDone!")
