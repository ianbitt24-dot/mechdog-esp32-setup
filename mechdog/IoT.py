#!/usr/bin/env python3
"""
MechDog IoT ESP32-C3-Mini-1 Communication Interface
Communicates with the ESP32-C3 module via serial port
"""

import serial
import time
import struct

class MechDogIoT:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        """Initialize serial connection to ESP32-C3-Mini-1"""
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for connection to stabilize
        print(f"Connected to MechDog IoT on {port} at {baudrate} baud")
    
    def setup_wifi_hotspot(self, ssid="MechDog", password="12345678"):
        """
        Configure WiFi hotspot on ESP32-C3
        Format: NIOT_<ssid>|||<password>$$$
        Note: The password must be at least 8 characters
        """
        if len(password) < 8:
            print("Error: Password must be at least 8 characters")
            return False
        
        # Format: NIOT_<ssid>|||<password>$$$
        config_str = f"NIOT_{ssid}|||{password}$$$"
        self.send_command(config_str)
        print(f"WiFi hotspot configured:")
        print(f"  SSID: NIOT_{ssid}")
        print(f"  Password: {password}")
        print("Wait a few seconds for the hotspot to activate...")
        time.sleep(3)
        return True
    
    def send_command(self, cmd):
        """Send a command string to the ESP32-C3"""
        if not cmd.endswith('\n'):
            cmd += '\n'
        self.serial.write(cmd.encode('utf-8'))
        self.serial.flush()
        print(f"Sent: {cmd.strip()}")
    
    def read_response(self, timeout=1):
        """Read response from ESP32-C3"""
        start_time = time.time()
        response = ""
        while (time.time() - start_time) < timeout:
            if self.serial.in_waiting > 0:
                data = self.serial.read(self.serial.in_waiting)
                response += data.decode('utf-8', errors='ignore')
                if '\n' in response:
                    break
            time.sleep(0.01)
        return response.strip()
    
    def send_iot_command(self, cmd_type, *params):
        """
        Send IoT command following the protocol from main.py
        Format: CMD|type|param1|param2|...|$
        
        Command types:
        0x01: Warnings (face, unknown object, impact)
        0x02: Color detection
        0x03: Sensor distance
        0x04: RGB LED control
        0x05: Buzzer control
        0x06: Action control
        0x07: ESP32S3 type query
        """
        cmd_str = f"CMD|{cmd_type}|"
        cmd_str += '|'.join(str(p) for p in params)
        cmd_str += "|$"
        self.send_command(cmd_str)
    
    def enable_face_detection(self, enable=True):
        """Enable/disable face detection warning"""
        self.send_iot_command(1, 1 if enable else 0, 0, 0)
    
    def enable_object_detection(self, enable=True):
        """Enable/disable unknown object detection"""
        self.send_iot_command(1, 0, 1 if enable else 0, 0)
    
    def enable_impact_detection(self, enable=True):
        """Enable/disable impact detection"""
        self.send_iot_command(1, 0, 0, 1 if enable else 0)
    
    def enable_color_detection(self, enable=True):
        """Enable/disable color detection"""
        self.send_iot_command(2, 1 if enable else 0)
    
    def enable_sensor_distance(self, enable=True):
        """Enable/disable distance sensor readings"""
        self.send_iot_command(3, 1 if enable else 0)
    
    def set_rgb_led(self, r, g, b):
        """Set RGB LED color (0-255 for each channel)"""
        self.send_iot_command(4, r, g, b)
    
    def set_buzzer(self, enable=True):
        """Enable/disable buzzer"""
        self.send_iot_command(5, 1 if enable else 0)
    
    def run_action(self, action_type, action_num):
        """
        Run a MechDog action
        action_type: 1=predefined action, 2=movement
        action_num: specific action ID
        """
        self.send_iot_command(6, action_type, action_num)
    
    def query_esp32s3_type(self):
        """Query ESP32S3 camera type"""
        self.send_iot_command(7)
    
    def read_sensor_data(self):
        """Read and parse sensor data from responses"""
        response = self.read_response()
        if response:
            print(f"Received: {response}")
            return response
        return None
    
    def interactive_mode(self):
        """Interactive command line interface"""
        print("\n=== MechDog IoT Interactive Mode ===")
        print("Commands:")
        print("  wifi SSID [PASS]  - Setup WiFi hotspot (default: MechDog/12345678)")
        print("  face [on/off]     - Face detection")
        print("  obj [on/off]      - Object detection")
        print("  impact [on/off]   - Impact detection")
        print("  color [on/off]    - Color detection")
        print("  distance [on/off] - Distance sensor")
        print("  rgb R G B         - Set LED color (0-255)")
        print("  buzz [on/off]     - Buzzer control")
        print("  action TYPE NUM   - Run action")
        print("  query             - Query ESP32S3 type")
        print("  read              - Read sensor data")
        print("  raw TEXT          - Send raw command")
        print("  quit              - Exit")
        print()
        
        try:
            while True:
                cmd = input("IoT> ").strip().lower()
                
                if not cmd:
                    continue
                    
                parts = cmd.split()
                
                if parts[0] == 'quit':
                    break
                elif parts[0] == 'wifi':
                    ssid = parts[1] if len(parts) > 1 else "MechDog"
                    password = parts[2] if len(parts) > 2 else "12345678"
                    self.setup_wifi_hotspot(ssid, password)
                elif parts[0] == 'face':
                    self.enable_face_detection(parts[1] == 'on' if len(parts) > 1 else True)
                elif parts[0] == 'obj':
                    self.enable_object_detection(parts[1] == 'on' if len(parts) > 1 else True)
                elif parts[0] == 'impact':
                    self.enable_impact_detection(parts[1] == 'on' if len(parts) > 1 else True)
                elif parts[0] == 'color':
                    self.enable_color_detection(parts[1] == 'on' if len(parts) > 1 else True)
                elif parts[0] == 'distance':
                    self.enable_sensor_distance(parts[1] == 'on' if len(parts) > 1 else True)
                elif parts[0] == 'rgb' and len(parts) == 4:
                    self.set_rgb_led(int(parts[1]), int(parts[2]), int(parts[3]))
                elif parts[0] == 'buzz':
                    self.set_buzzer(parts[1] == 'on' if len(parts) > 1 else True)
                elif parts[0] == 'action' and len(parts) == 3:
                    self.run_action(int(parts[1]), int(parts[2]))
                elif parts[0] == 'query':
                    self.query_esp32s3_type()
                elif parts[0] == 'read':
                    self.read_sensor_data()
                elif parts[0] == 'raw':
                    self.send_command(' '.join(parts[1:]))
                else:
                    print("Unknown command. Type 'quit' to exit.")
                
                # Check for any responses
                time.sleep(0.1)
                while self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    print(f"Response: {data.decode('utf-8', errors='ignore')}")
                    time.sleep(0.05)
                    
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.close()
    
    def close(self):
        """Close serial connection"""
        if self.serial.is_open:
            self.serial.close()
            print("Connection closed")


if __name__ == "__main__":
    import sys
    
    # Check if port is specified
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    
    try:
        iot = MechDogIoT(port=port)
        iot.interactive_mode()
    except serial.SerialException as e:
        print(f"Error: {e}")
        print(f"Make sure the ESP32-C3 is connected to {port}")
        print("Available ports:")
        import glob
        for p in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
            print(f"  {p}")
