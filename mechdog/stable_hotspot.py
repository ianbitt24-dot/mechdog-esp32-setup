#!/usr/bin/env python3
"""
Stable WiFi hotspot setup for MechDog ESP32-C3
Sends configuration multiple times and monitors stability
"""

import serial
import time
import sys

def setup_stable_hotspot(port='/dev/ttyUSB0', ssid="MechDog", password="12345678"):
    """Setup WiFi hotspot with stability checks"""
    
    print(f"Connecting to {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)
        print("Connected!")
    except serial.SerialException as e:
        print(f"Error: {e}")
        return False
    
    # Clear any buffered data
    if ser.in_waiting > 0:
        ser.read(ser.in_waiting)
    
    config_str = f"NIOT_{ssid}|||{password}$$$"
    
    print(f"\nConfiguring WiFi hotspot (sending {len(config_str)} bytes):")
    print(f"  SSID: NIOT_{ssid}")
    print(f"  Password: {password}")
    print("\nSending configuration commands...")
    
    # Send configuration multiple times for stability
    for i in range(5):
        print(f"  Attempt {i+1}/5...", end='', flush=True)
        
        # Send the configuration
        ser.write(config_str.encode('utf-8'))
        ser.write(b'\n')
        ser.flush()
        
        # Wait and check for response
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if config_str in response or 'NIOT' in response:
                print(" ✓ Acknowledged")
            else:
                print(" Sent")
        else:
            print(" Sent")
        
        time.sleep(1)
    
    print("\n✓ Configuration commands sent!")
    print("\nMonitoring for 10 seconds...")
    
    # Monitor for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            # Filter out repetitive ARM_ACTION messages
            if 'ARM_ACTION' not in data and data.strip():
                print(f"Response: {data.strip()}")
        time.sleep(0.1)
    
    print("\n" + "="*50)
    print("Setup complete!")
    print("="*50)
    print(f"\nLook for WiFi network: NIOT_{ssid}")
    print(f"Password: {password}")
    print("\nIf the hotspot is still unstable:")
    print("1. Check ESP32-C3 power connections")
    print("2. Ensure the module has adequate power supply")
    print("3. Try power cycling the MechDog")
    print("4. Check for loose wiring connections")
    
    ser.close()
    return True

def monitor_mode(port='/dev/ttyUSB0'):
    """Continuously monitor the serial connection"""
    print(f"Monitoring {port} (Ctrl+C to stop)...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(1)
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                # Filter repetitive messages
                if 'ARM_ACTION' not in data or 'NIOT' in data:
                    timestamp = time.strftime('%H:%M:%S')
                    print(f"[{timestamp}] {data.strip()}")
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        monitor_mode()
    else:
        ssid = sys.argv[1] if len(sys.argv) > 1 else "MechDog"
        password = sys.argv[2] if len(sys.argv) > 2 else "12345678"
        setup_stable_hotspot(ssid=ssid, password=password)
        
        # Ask if user wants to monitor
        print("\nWould you like to monitor the connection? (y/n): ", end='', flush=True)
