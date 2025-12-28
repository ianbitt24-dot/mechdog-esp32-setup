# Hiwonder MechDog
# MicroPython - Combined Bluetooth + WiFi IoT Control
# This version supports BOTH Bluetooth APP control AND WiFi IoT features

import Hiwonder
import time
from time import sleep_ms
import Hiwonder_IIC
from Hiwonder_BLE import BLE
from HW_MechDog import MechDog
import machine
import struct

# Bluetooth variables
_BLE_REC_DATA = 0
_COMMAND = 0
_SEND_DATA = 0
_DATA = 0
_distance = 0
_SONER_DISTANCE = 0
_self_balancing_flag = 0
_RUN_STEP = 0
_obstacle_avoidance_flag = 0
_Pitch_angle = 0
_Roll_angle = 0
_ACTION_TYPE = 0
_ACTION_NUM = 0
_RUN_DIR = 0
_REC_PARSE_VALUE = []
_High_mm = 0
_ARM_ACTION = 0
arm_step = 0
arm_tick = 0
sonar_tick = 0
servo9_pos = 500
servo10_pos = 500
servo11_pos = 1500

# WiFi IoT variables
ESP32CAM_ADDR = 0x52
ESP32CAM_FACE = 0x01
ESP32CAM_COLOR_1 = 0x00
ESP32CAM_COLOR_2 = 0x01
ESP32CAM_COLOR_3 = 0x02

esp32s3_type = 0

onoff_face = False
onoff_undef_obj = False
onoff_hit = False

warn_face = False
warn_undef_obj = False
warn_hit = False

color_detec_flag = False
color_detec_num = 0

sensor_flag = False
sensor_distance = 0

buzzer_flag = False
buzzer_on = False

action_type = 0
action_num = 0

# Initialize hardware
mac = machine.unique_id()
ble = BLE(BLE.MODE_BLE_SLAVE,"MechDog_{:02X}".format(mac[5]))
mechdog = MechDog()

iic1 = Hiwonder_IIC.IIC(1)
iic2 = Hiwonder_IIC.IIC(2)
i2csonar = Hiwonder_IIC.I2CSonar(iic1)
esps3cam = Hiwonder_IIC.ESP32S3Cam(iic1)
buzzer = Hiwonder.Buzzer()
imu = Hiwonder_IIC.MPU()

time.sleep(1)

# Initialize WiFi hotspot
print("Initializing WiFi hotspot...")
sleep_ms(100)
iic2.writeto(0x69, "NIOT_MechDog|||12345678$$$")
sleep_ms(1000)
print("WiFi hotspot configured: SSID=NIOT_MechDog, Password=12345678")

# Detect ESP32S3 camera type
try:
  for i in range(5):
    rec = iic1.readfrom_mem(ESP32CAM_ADDR, 2, 4)
    if rec:
      values = struct.unpack('<BBBB', rec)
      if values[0] == 255 and values[1] == 255:
        esp32s3_type = 1
        print("ESP32S3 face detection module detected")
        break
      else:
        esp32s3_type = 2
        print("ESP32S3 color detection module detected")
    sleep_ms(50)
except:
  print("ESP32S3 camera module not detected")

sleep_ms(500)


# WiFi IoT communication functions
def wifi_send(buf):
  try:
    iic2.writeto(0x69, buf)
  except:
    pass

def wifi_read():
  try:
    return iic2.readfrom(0x69, 20)
  except:
    return None


# WiFi IoT main thread
def wifi_main():
  global warn_face
  global warn_undef_obj
  global warn_hit
  global color_detec_flag
  global color_detec_num
  global sensor_flag
  global sensor_distance
  global buzzer_flag
  global action_type
  global action_num
  global onoff_face
  global onoff_undef_obj
  global onoff_hit
  global esp32s3_type
  
  last_time_1000ms = 0
  last_time_100ms = 0
  last_time_50ms = 0
  
  last_receive = 0
  
  while True:
    try:
      # read and deal wifi
      if time.ticks_ms() > last_time_50ms:
        last_time_50ms += 100
        receive_data = wifi_read()
        if receive_data != None:
          receive_data = bytes([x for x in receive_data if x != 0xd3])
          if last_receive != receive_data:
            last_receive = receive_data
            rec = receive_data.decode('utf-8')
            if rec.find("CMD") != -1 and rec.find("$"):
              cmd = rec.split('|')[1:]
          
              if int(cmd[0]) == 1: # warn
                if int(cmd[1]) == 1:
                  onoff_face = True
                  color_detec_flag = False
                else:
                  onoff_face = False
                if int(cmd[2]) == 1:
                  onoff_undef_obj = True
                else:
                  onoff_undef_obj = False
                  
                if int(cmd[3]) == 1:
                  onoff_hit = True
                  warn_hit = False
                else:
                  onoff_hit = False
                  
              elif int(cmd[0]) == 0x02: # color detect
                if int(cmd[1]) == 0x01:
                  color_detec_flag = True
                  onoff_face = False
                else:
                  color_detec_flag = False
                  
              elif int(cmd[0]) == 0x03: # sensor distance
                if int(cmd[1]) == 0x01:
                  sensor_flag = True
                else:
                  sensor_flag = False
                  
              elif int(cmd[0]) == 0x04: # rgb
                i2csonar.setRGB(0, int(cmd[1]), int(cmd[2]), int(cmd[3]))
                
              elif int(cmd[0]) == 0x05: # buzzer
                if int(cmd[1]) == 0x01:
                  buzzer_flag = True
                else:
                  buzzer_flag = False
              elif int(cmd[0]) == 0x06:
                action_type = int(cmd[1])
                action_num = int(cmd[2])
                
              elif int(cmd[0]) == 0x07: # esp32s3 type
                wifi_send("CMD|7|{}|$".format(esp32s3_type))
                
      if time.ticks_ms() > last_time_100ms:
        last_time_100ms += 100
        if color_detec_flag == True:
          wifi_send("CMD|2|{}|$".format(color_detec_num))

        if sensor_flag == True:
          wifi_send("CMD|3|{}|$".format(sensor_distance))
          
      if time.ticks_ms() > last_time_1000ms:
        last_time_1000ms += 1000
        flags = [0,0,0]
        if warn_face == True:
          flags[0] = 1
        if warn_undef_obj == True:
          flags[1] = 1
        if warn_hit == True:
          flags[2] = 1
        buf = "CMD|1|{}|{}|{}|$".format(flags[0],flags[1],flags[2])
        wifi_send(buf)
    except:
      sleep_ms(100)


# ESP32S3 camera processing thread
def esp32s3_main():
  global color_detec_flag
  global color_detec_num
  global onoff_face
  global warn_face
  
  color_step = 0
  color_count = 0
  
  sleep_ms(1000)
  color_list = [3,1,2]
  
  while True:
    try:
      if color_detec_flag == True:
        rec = iic1.readfrom_mem(ESP32CAM_ADDR, color_step, 4)
        values = struct.unpack('<BBBB', rec)
        if values[2] > 0:
          color_detec_num = color_list[color_step]
          color_count = 0
        color_step += 1
        if color_step > 2:
          color_step = 0
        else:
          color_count += 1
          if color_count > 3:
            color_count = 0 
            color_detec_num = 0
    except:
      pass

    try:
      if onoff_face == True:
        rec = iic1.readfrom_mem(ESP32CAM_ADDR, ESP32CAM_FACE, 4)
        if len(rec) == 4:
          values = struct.unpack('<BBBB', rec)
          if values[2] > 0:
            warn_face = True
          else:
            warn_face = False
        else:
          warn_face = False
      else:
        warn_face = False
    except:
      pass
    
    sleep_ms(100)


# Bluetooth APP control thread
def start_main():
  global ble
  global _BLE_REC_DATA
  global _COMMAND
  global _SEND_DATA
  global _DATA
  global _distance
  global _SONER_DISTANCE
  global _self_balancing_flag
  global _RUN_STEP
  global _obstacle_avoidance_flag
  global _Pitch_angle
  global _Roll_angle
  global mechdog
  global _ACTION_TYPE
  global _ACTION_NUM
  global _RUN_DIR
  global _REC_PARSE_VALUE
  global _High_mm
  global _ARM_ACTION
  
  dir_flag = 1
  while True:
    if ble.is_connected():
      if ble.contains_data("CMD"):
        _BLE_REC_DATA = ble.read_uart_cmd()
        if not _BLE_REC_DATA:
          continue
        _REC_PARSE_VALUE = ble.parse_uart_cmd(_BLE_REC_DATA)
        _COMMAND = _REC_PARSE_VALUE[0]
        _COMMAND = int(_COMMAND)
        print("BLE Received command:", _COMMAND, "Data:", _REC_PARSE_VALUE)
        if (_COMMAND==6):
          _SEND_DATA = "CMD|6|{}|$".format(Hiwonder.Battery_power())
          ble.send_data(_SEND_DATA)
          continue
        if (_COMMAND==4):
          _DATA = int(_REC_PARSE_VALUE[1])
          if (_DATA==1):
            _distance = round((_SONER_DISTANCE*10))
            if (_distance>5000):
              _distance = 5000
            _SEND_DATA = "CMD|4|{}|$".format(_distance)
            ble.send_data(_SEND_DATA)
          elif ((_DATA==2) and (_self_balancing_flag==0)):
            if ((int(_REC_PARSE_VALUE[2]))==1):
              mechdog.set_default_pose()
              _Pitch_angle = 0
              _Roll_angle = 0
              _High_mm = 0
              time.sleep(1)
              _RUN_STEP = 41
            else:
              _RUN_STEP = 40
          elif (_DATA==3):
            i2csonar.setRGB(0,(int(_REC_PARSE_VALUE[2])),(int(_REC_PARSE_VALUE[3])),(int(_REC_PARSE_VALUE[4])))
          continue
        if (_COMMAND==7):
          print("ARM COMMAND RECEIVED! Action:", _REC_PARSE_VALUE[1], "Full data:", _REC_PARSE_VALUE)
          _ARM_ACTION = int(_REC_PARSE_VALUE[1])
        if ((_COMMAND==1) and (_obstacle_avoidance_flag==0)):
          _DATA = int(_REC_PARSE_VALUE[1])
          if (_DATA==3):
            _DATA = int(_REC_PARSE_VALUE[2])
            if (_DATA==1):
              mechdog.set_default_pose()
              _Pitch_angle = 0
              _Roll_angle = 0
              _High_mm = 0
              time.sleep(1)
              _RUN_STEP = 131
            else:
              _RUN_STEP = 130
          if ((_obstacle_avoidance_flag==0) and (_self_balancing_flag==0)):
            if (_DATA==1):
              _DATA = int(_REC_PARSE_VALUE[2])
              if (_DATA==1):
                if (_Roll_angle<17):
                  _Roll_angle+=1
                  mechdog.transform([0, 0, 0], [-1, 0, 0], 80)
              else:
                if (_Roll_angle>-17):
                  _Roll_angle-=1
                  mechdog.transform([0, 0, 0], [1, 0, 0], 80)
            if (_DATA==2):
              _DATA = int(_REC_PARSE_VALUE[2])
              if (_DATA==1):
                if (_Pitch_angle<17):
                  _Pitch_angle+=1
                  mechdog.transform([0, 0, 0], [0, 1, 0], 80)
              else:
                if (_Pitch_angle>-17):
                  _Pitch_angle-=1
                  mechdog.transform([0, 0, 0], [0, -1, 0], 80)
            if (_DATA==4):
              _DATA = int(_REC_PARSE_VALUE[2])
              if (_DATA==1):
                if (_High_mm < 15):
                  _High_mm += 1
                  mechdog.transform([0, 0, 1], [0, 0, 0], 80)
              else:
                if _High_mm > -25:
                  _High_mm -= 1
                  mechdog.transform([0, 0, -1], [0, 0, 0], 80)
            if (_DATA==5):
              mechdog.set_default_pose()
              _Pitch_angle = 0
              _Roll_angle = 0
              _High_mm = 0
              time.sleep(1)
            continue
        if (_COMMAND==2) and (_obstacle_avoidance_flag==0) and (_self_balancing_flag==0):
          _RUN_STEP = 2
          _ACTION_TYPE = int(_REC_PARSE_VALUE[1])
          _ACTION_NUM = int(_REC_PARSE_VALUE[2])
        if (_COMMAND==3) and (_obstacle_avoidance_flag==0) and (_self_balancing_flag==0):
          _RUN_STEP = 3
          _RUN_DIR = int(_REC_PARSE_VALUE[1])
          if _RUN_DIR < 6:
            if dir_flag != 1:
              dir_flag = 1
              mechdog.transform([10 , 0 , 0] , [0 , 0 , 0] , 100)
          else:
            if dir_flag != -1:
              dir_flag = -1
              mechdog.transform([-10 , 0 , 0] , [0 , 0 , 0] , 100)
      else:
        time.sleep(0.03)


# Motion and sensor processing thread
def start_main1():
  global ble
  global _SONER_DISTANCE
  global _self_balancing_flag
  global _RUN_STEP
  global _obstacle_avoidance_flag
  global mechdog
  global _ACTION_TYPE
  global _ACTION_NUM
  global _RUN_DIR
  global i2csonar
  global _Pitch_angle
  global _Roll_angle
  global _High_mm
  global _ARM_ACTION
  global arm_step
  global arm_tick
  global sonar_tick
  global servo9_pos
  global servo10_pos
  global servo11_pos
  global _REC_PARSE_VALUE
  global sensor_distance
  global warn_undef_obj
  global action_type
  global action_num
  global warn_hit
  global onoff_hit
  global sensor_flag
  global buzzer_flag
  global buzzer

  step = 0
  distance = 0
  dis_count = 0
  last_time_50ms = 0
  last_time_1000ms = 0
  
  while True:
    # Sensor reading and IoT processing
    if time.ticks_ms() > last_time_50ms:
      last_time_50ms += 50
      rec_distance = i2csonar.getDistance()
      if rec_distance < 500:
        distance = rec_distance
        dis_count = 0
      else:
        dis_count += 1
        if dis_count > 4:
          distance = 500
          dis_count = 0
      
      _SONER_DISTANCE = distance
      
      if onoff_undef_obj == True:
        if distance < 15:
          warn_undef_obj = True
        else:
          warn_undef_obj = False
      else:
        warn_undef_obj = False
      
      if onoff_hit == True:
        angle = imu.read_angle()
        if angle[0] > 50 or angle[0] < -50:
          warn_hit = True
        else:
          warn_hit = False
      else:
        warn_hit = False
      
      if sensor_flag == True:
        sensor_distance = int(distance)
      
      # WiFi IoT action control
      if action_type == 1:
        dong_zuo_zu_yun_xing(action_num)
        action_type = 0
      elif action_type == 2:
        if action_num == 100:
          mechdog.move(90,0)
          time.sleep(2)
          mechdog.move(0,0)
        else:
          mechdog.action_run(str(action_num))
        action_type = 0
    
    if time.ticks_ms() > last_time_1000ms:
      last_time_1000ms += 1000
      if buzzer_flag == True:
        buzzer.playTone(1000, 500, False)
    
    # Bluetooth sonar tick
    if time.ticks_ms() > sonar_tick:
      sonar_tick = time.ticks_ms() + 80
      
    # Arm control
    if time.ticks_ms() > arm_tick:
      if arm_step == 0:
        if _ARM_ACTION == 3:
          if len(_REC_PARSE_VALUE) > 2:
            direction = int(_REC_PARSE_VALUE[2])
            if direction == 1:
              servo9_pos = min(servo9_pos + 100, 2500)
            elif direction == -1:
              servo9_pos = max(servo9_pos - 100, 500)
            mechdog.set_servo(9, servo9_pos, 200)
            print("Servo 9 position:", servo9_pos)
          arm_tick = time.ticks_ms() + 100
          _ARM_ACTION = 0
        elif _ARM_ACTION == 4:
          if len(_REC_PARSE_VALUE) > 2:
            direction = int(_REC_PARSE_VALUE[2])
            if direction == 1:
              servo10_pos = min(servo10_pos + 100, 2500)
            elif direction == -1:
              servo10_pos = max(servo10_pos - 100, 500)
            mechdog.set_servo(10, servo10_pos, 200)
            print("Servo 10 position:", servo10_pos)
          arm_tick = time.ticks_ms() + 100
          _ARM_ACTION = 0
        elif _ARM_ACTION == 6:
          servo11_pos = 1500
          mechdog.set_servo(11, servo11_pos, 500)
          print("Gripper opened - Servo 11 position:", servo11_pos)
          arm_tick = time.ticks_ms() + 600
          _ARM_ACTION = 0
        elif _ARM_ACTION == 7:
          servo11_pos = 1000
          mechdog.set_servo(11, servo11_pos, 500)
          print("Gripper closed - Servo 11 position:", servo11_pos)
          arm_tick = time.ticks_ms() + 600
          _ARM_ACTION = 0
          
    if (step==0):
      step = _RUN_STEP
      _RUN_STEP = 0
      time.sleep(0.05)
    else:
      if (step==41):
        _obstacle_avoidance_flag = 1
        forward_flag = 1
        while True:
          if ((_RUN_STEP==40) or (_obstacle_avoidance_flag==0)):
            _obstacle_avoidance_flag = 0
            mechdog.move(0,0)
            i2csonar.setRGB(0,0x33,0x33,0xff)
            if forward_flag == 0:
                forward_flag = 1
                mechdog.transform([10 , 0 , 0] , [0 , 0 , 0] , 100)
            time.sleep(1)
            break
          if (_SONER_DISTANCE<10):
            i2csonar.setRGB(0,0xff,0x00,0x00)
            if forward_flag == 1:
              forward_flag = 0
              mechdog.transform([-10 , 0 , 0] , [0 , 0 , 0] , 100)
            mechdog.move(-40,0)
            for count in range(30):
              if (_RUN_STEP==40):
                break
              time.sleep(0.1)
          else:
            if forward_flag == 0:
                forward_flag = 1
                mechdog.transform([10 , 0 , 0] , [0 , 0 , 0] , 100)
            if (_SONER_DISTANCE<40):
              i2csonar.setRGB(0,0xff,0xcc,0x00)
              mechdog.move(80,-50)
              for count in range(50):
                if (_RUN_STEP==40):
                  break
                time.sleep(0.1)
            else:
              i2csonar.setRGB(0,0xcc,0x33,0xcc)
              mechdog.move(120,0)
          time.sleep(0.02)
      if (step==131):
        _self_balancing_flag = 1
        mechdog.homeostasis(True)
        time.sleep(2)
        while True:
          if (_RUN_STEP==130):
            _self_balancing_flag = 0
            mechdog.homeostasis(False)
            time.sleep(2)
            break
          if not (mechdog.read_homeostasis_status()):
            ble.send_data("CMD|1|3|0|$")
            _self_balancing_flag = 0
            break
      if (step==2):
        if (_ACTION_TYPE==1):
          mechdog.set_default_pose(duration = 500)
          _Pitch_angle = 0
          _Roll_angle = 0
          _High_mm = 0
          time.sleep(1)
          dong_zuo_zu_yun_xing(_ACTION_NUM)
        else:
          mechdog.set_default_pose(duration = 500)
          _Pitch_angle = 0
          _Roll_angle = 0
          _High_mm = 0
          time.sleep(1)
          mechdog.action_run(str(_ACTION_NUM))
      if (step==3):
        while True:
          if (_RUN_DIR==0):
            mechdog.move(0,0)
            break
          elif (_RUN_DIR==1):
            mechdog.move(80,-40)
            continue
          elif (_RUN_DIR==2):
            mechdog.move(90,-25)
            continue
          elif (_RUN_DIR==3):
            mechdog.move(120,0)
            continue
          elif (_RUN_DIR==4):
            mechdog.move(90,25)
            continue
          elif (_RUN_DIR==5):
            mechdog.move(80,40)
            continue
          elif (_RUN_DIR==6):
            mechdog.move(-40,-20)
            continue
          elif (_RUN_DIR==7):
            mechdog.move(-40,0)
            continue
          elif (_RUN_DIR==8):
            mechdog.move(-40,20)
            continue
      step = 0


def dong_zuo_zu_yun_xing(dong_zuo):
  global mechdog

  if (dong_zuo==1):
    mechdog.action_run("left_foot_kick")
    time.sleep(3)
    return
  if (dong_zuo==2):
    mechdog.action_run("right_foot_kick")
    time.sleep(3)
    return
  if (dong_zuo==3):
    mechdog.action_run("stand_four_legs")
    time.sleep(2)
    return
  if (dong_zuo==4):
    mechdog.action_run("sit_dowm")
    time.sleep(2)
    return
  if (dong_zuo==5):
    mechdog.action_run("go_prone")
    time.sleep(2)
    return
  if (dong_zuo==6):
    mechdog.action_run("stand_two_legs")
    time.sleep(4)
    return
  if (dong_zuo==7):
    mechdog.action_run("handshake")
    time.sleep(4)
    return
  if (dong_zuo==8):
    mechdog.action_run("scrape_a_bow")
    time.sleep(4)
    return
  if (dong_zuo==9):
    mechdog.action_run("nodding_motion")
    time.sleep(2)
    return
  if (dong_zuo==10):
    mechdog.action_run("boxing")
    time.sleep(2)
    return
  if (dong_zuo==11):
    mechdog.action_run("stretch_oneself")
    time.sleep(2)
    return
  if (dong_zuo==12):
    mechdog.action_run("pee")
    time.sleep(2)
    return
  if (dong_zuo==13):
    mechdog.action_run("press_up")
    time.sleep(2)
    return
  if (dong_zuo==14):
    mechdog.action_run("rotation_pitch")
    time.sleep(2)
    return
  if (dong_zuo==15):
    mechdog.action_run("rotation_roll")
    time.sleep(2)
    return


# Start all threads
print("Starting MechDog with Bluetooth and WiFi IoT support...")
print("Bluetooth: MechDog_{:02X}".format(mac[5]))
print("WiFi: SSID=NIOT_MechDog, Password=12345678")

Hiwonder.startMain(wifi_main)        # WiFi IoT communication
Hiwonder.startMain(esp32s3_main)      # ESP32S3 camera processing
Hiwonder.startMain(start_main)        # Bluetooth control
Hiwonder.startMain(start_main1)       # Motion and sensors
