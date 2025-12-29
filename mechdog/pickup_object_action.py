# MechDog Pick Up Object Action
# Custom action that walks forward, detects object, and picks it up with robotic arm

import Hiwonder
import time
import Hiwonder_IIC
from HW_MechDog import MechDog

# Configuration
DETECTION_DISTANCE = 15  # Stop when object is within 15cm
PICKUP_DISTANCE = 8      # Ideal distance for pickup (8-10cm)
FORWARD_SPEED = 60       # Walking speed
APPROACH_SPEED = 30      # Slow approach speed

# Arm positions
ARM_BASE_DEFAULT = 500      # Servo 9 - base rotation (500-2500)
ARM_ELBOW_UP = 2000         # Servo 10 - arm up position
ARM_ELBOW_DOWN = 800        # Servo 10 - arm down to grab
GRIPPER_OPEN = 1500         # Servo 11 - gripper open
GRIPPER_CLOSED = 1000       # Servo 11 - gripper closed


def pickup_object():
    """
    Custom action: Walk forward, detect object, and pick it up
    
    Sequence:
    1. Reset arm to default position
    2. Walk forward while scanning
    3. Stop when object detected
    4. Approach slowly to ideal distance
    5. Lower arm
    6. Close gripper
    7. Raise arm
    8. Return to default pose
    """
    
    mechdog = MechDog()
    i2c1 = Hiwonder_IIC.IIC(1)
    i2csonar = Hiwonder_IIC.I2CSonar(i2c1)
    
    print("=== Pick Up Object Action Started ===")
    
    # Step 1: Initialize arm position
    print("Step 1: Initializing arm...")
    mechdog.set_servo(9, ARM_BASE_DEFAULT, 500)   # Base center
    mechdog.set_servo(10, ARM_ELBOW_UP, 500)       # Arm up
    mechdog.set_servo(11, GRIPPER_OPEN, 500)       # Gripper open
    time.sleep(1)
    i2csonar.setRGB(0, 0x00, 0xff, 0x00)  # Green LED - searching
    
    # Step 2: Walk forward while scanning for object
    print("Step 2: Walking forward, scanning...")
    mechdog.move(FORWARD_SPEED, 0)
    
    object_detected = False
    timeout = 100  # 10 seconds timeout (100 * 0.1s)
    
    for i in range(timeout):
        distance = i2csonar.getDistance()
        
        if distance < DETECTION_DISTANCE and distance > 2:
            print(f"Object detected at {distance}cm!")
            object_detected = True
            mechdog.move(0, 0)  # Stop
            i2csonar.setRGB(0, 0xff, 0xff, 0x00)  # Yellow - object found
            break
        
        time.sleep(0.1)
    
    if not object_detected:
        print("No object detected. Aborting.")
        mechdog.move(0, 0)
        i2csonar.setRGB(0, 0xff, 0x00, 0x00)  # Red - failed
        time.sleep(1)
        return False
    
    # Step 3: Approach to ideal pickup distance
    print("Step 3: Approaching object...")
    approach_complete = False
    
    for i in range(50):  # 5 second timeout
        distance = i2csonar.getDistance()
        
        if distance <= PICKUP_DISTANCE:
            mechdog.move(0, 0)
            approach_complete = True
            print(f"Reached pickup position at {distance}cm")
            break
        elif distance > PICKUP_DISTANCE + 5:
            mechdog.move(APPROACH_SPEED, 0)  # Move forward slowly
        else:
            mechdog.move(0, 0)
            approach_complete = True
            break
        
        time.sleep(0.1)
    
    mechdog.move(0, 0)  # Ensure stopped
    time.sleep(0.3)
    
    if not approach_complete:
        print("Could not reach pickup position. Aborting.")
        i2csonar.setRGB(0, 0xff, 0x00, 0x00)  # Red
        return False
    
    # Step 4: Lower arm to grab position
    print("Step 4: Lowering arm...")
    i2csonar.setRGB(0, 0x00, 0xff, 0xff)  # Cyan - picking up
    mechdog.set_servo(10, ARM_ELBOW_DOWN, 1000)
    time.sleep(1.2)
    
    # Step 5: Close gripper to grab object
    print("Step 5: Closing gripper...")
    mechdog.set_servo(11, GRIPPER_CLOSED, 500)
    time.sleep(0.8)
    
    # Step 6: Lift arm with object
    print("Step 6: Lifting object...")
    mechdog.set_servo(10, ARM_ELBOW_UP, 1000)
    time.sleep(1.2)
    
    # Step 7: Success indication
    print("Step 7: Object picked up successfully!")
    i2csonar.setRGB(0, 0x00, 0xff, 0x00)  # Green - success
    
    # Celebrate with a small movement
    mechdog.transform([0, 0, 0], [0, 5, 0], 200)  # Nod forward
    time.sleep(0.3)
    mechdog.transform([0, 0, 0], [0, -5, 0], 200)  # Nod back
    time.sleep(0.3)
    mechdog.transform([0, 0, 0], [0, 0, 0], 200)  # Return to neutral
    
    print("=== Pick Up Object Action Complete ===")
    return True


def release_object():
    """
    Helper function: Release the held object
    """
    mechdog = MechDog()
    i2c1 = Hiwonder_IIC.IIC(1)
    i2csonar = Hiwonder_IIC.I2CSonar(i2c1)
    
    print("Releasing object...")
    i2csonar.setRGB(0, 0xff, 0xff, 0x00)  # Yellow
    
    # Lower arm slightly
    mechdog.set_servo(10, 1500, 500)
    time.sleep(0.6)
    
    # Open gripper
    mechdog.set_servo(11, GRIPPER_OPEN, 500)
    time.sleep(0.6)
    
    # Raise arm back up
    mechdog.set_servo(10, ARM_ELBOW_UP, 500)
    time.sleep(0.6)
    
    i2csonar.setRGB(0, 0x00, 0x00, 0xff)  # Blue
    print("Object released")


def reset_arm():
    """
    Helper function: Reset arm to default position
    """
    mechdog = MechDog()
    
    print("Resetting arm to default position...")
    mechdog.set_servo(9, ARM_BASE_DEFAULT, 500)
    mechdog.set_servo(10, ARM_ELBOW_UP, 500)
    mechdog.set_servo(11, GRIPPER_OPEN, 500)
    time.sleep(1)
    print("Arm reset complete")


# Run the action if executed directly
if __name__ == "__main__":
    try:
        success = pickup_object()
        
        if success:
            print("\nObject is held. Waiting 3 seconds...")
            time.sleep(3)
            
            print("\nReleasing object...")
            release_object()
            
            time.sleep(1)
            reset_arm()
        else:
            print("\nPickup failed. Resetting arm...")
            reset_arm()
            
    except KeyboardInterrupt:
        print("\n\nAction interrupted!")
        mechdog = MechDog()
        mechdog.move(0, 0)
        reset_arm()
