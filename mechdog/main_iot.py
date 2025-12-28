import Hiwonder
import time
from time import sleep_ms
import Hiwonder_IIC
from HW_MechDog import MechDog
from Hiwonder_BLE import BLE
import struct


mechdog = MechDog()

iic1 = Hiwonder_IIC.IIC(1)
iic2 = Hiwonder_IIC.IIC(2)
i2csonar = Hiwonder_IIC.I2CSonar(iic1)
esps3cam = Hiwonder_IIC.ESP32S3Cam(iic1)
buzzer = Hiwonder.Buzzer()
imu = Hiwonder_IIC.MPU()

sleep_ms(100)
iic2.writeto(0x69 , "NIOT_MechDog|||12345678$$$")
sleep_ms(1000)

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


try:
  for i in range(5):
    rec = iic1.readfrom_mem(ESP32CAM_ADDR , 2 , 4)
    if rec:
      values = struct.unpack('<BBBB', rec)
      print(rec)
      if values[0] == 255 and values[1] == 255:
        esp32s3_type = 1
        print("esp32s3 face.")
        break
      else:
        esp32s3_type = 2
        print("esp32s3 color.")
    sleep_ms(50)

except:
  print("esp32s3 read fail.")

sleep_ms(500)

def wifi_send(buf):
  iic2.writeto(0x69 , buf)

def wifi_read():
  try:
    return iic2.readfrom(0x69 , 20)
  except:
    return None

#wifi receive and send
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
                i2csonar.setRGB(0 , int(cmd[1]) , int(cmd[2]) , int(cmd[3]))
                
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
          print("co:{}".format(color_detec_num))

        if sensor_flag == True:
          wifi_send("CMD|3|{}|$".format(sensor_distance))

      if time.ticks_ms() > last_time_1000ms:
        last_time_1000ms += 1000
        flags = [0,0,0]
        if warn_face == True:
          # warn_face = False
          flags[0] = 1
        if warn_undef_obj == True:
          # warn_undef_obj = False
          flags[1] = 1
        if warn_hit == True:
          flags[2] = 1
        buf = "CMD|1|{}|{}|{}|$".format(flags[0],flags[1],flags[2])
        wifi_send(buf)
    except:
      print("wifi fail.")
      sleep_ms(100)


def action_run(dong_zuo):
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


def start_main():
  global sensor_distance
  global warn_undef_obj
  global action_type
  global action_num
  global warn_hit
  global onoff_hit
  
  last_time_50ms = 0
  last_time_1000ms = 0
  distance = 0
  dis_count = 0
  
  while True:
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
      
      if onoff_undef_obj == True:
        if distance < 15: # 不明物体检测
          warn_undef_obj = True
        else:
          warn_undef_obj = False
      else:
        warn_undef_obj = False
      
      if onoff_hit == True:
        # warn_hit
        angle = imu.read_angle()
        if angle[0] > 50 or angle[0] < -50:
          warn_hit = True
        else:
          warn_hit = False
      else:
        warn_hit = False
      
      if sensor_flag == True: # get sensor distance
        sensor_distance = int(distance)
      
      if action_type == 1: # action run
        action_run(action_num)
        action_type = 0
      elif action_type == 2:
        if action_num == 100:
          mechdog.move(90,0)
          time.sleep(2)
          mechdog.move(0,0)
        else:
          mechdog.action_run(str(action_num))
        action_type = 0
      
    if time.ticks_ms() > last_time_1000ms: # buzzer run
      last_time_1000ms += 1000
      if buzzer_flag == True:
        buzzer.playTone(1000 , 500 , False)






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
        # color
        rec = iic1.readfrom_mem(ESP32CAM_ADDR , color_step , 4)
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
      print("color read fail")

    try:
      if onoff_face == True:
        # face
        rec = iic1.readfrom_mem(ESP32CAM_ADDR , ESP32CAM_FACE , 4)
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
      print("s3 no face func")
    
    sleep_ms(100)



Hiwonder.startMain(wifi_main)
Hiwonder.startMain(start_main)
Hiwonder.startMain(esp32s3_main)







