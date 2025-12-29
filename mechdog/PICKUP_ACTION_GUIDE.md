# MechDog Pick Up Object Action

## Custom Action 16: Autonomous Object Pickup

### Overview
A fully automated sequence that makes MechDog walk forward, detect an object using its ultrasonic sensor, and pick it up with the robotic arm.

## Files Created

### 1. `pickup_object_action.py` (Standalone)
Can be uploaded and run independently on MechDog for testing.

**Features:**
- Complete pickup sequence
- Helper functions: `release_object()`, `reset_arm()`
- Configurable parameters
- LED status indicators
- Error handling

**Usage:**
```bash
# Upload to MechDog
ampy --port /dev/ttyUSB0 put pickup_object_action.py

# Run via REPL
>>> import pickup_object_action
>>> pickup_object_action.pickup_object()
```

### 2. `main_bluetooth_wifi.py` (Integrated)
Updated with Custom Action 16 built-in.

**How to Trigger:**
- Via Bluetooth APP: Select "Custom Action" → Action Type 1, Number 16
- Via WiFi IoT: Send command `CMD|6|1|16|$`

## Action Sequence

### Step-by-Step:

1. **Initialize** (1 sec)
   - Move arm to default position
   - Open gripper
   - LED: 🟢 Green (searching)

2. **Scan & Walk** (max 10 sec)
   - Walk forward at speed 60
   - Scan with ultrasonic sensor
   - Stop when object < 15cm
   - LED: 🟡 Yellow (object found)

3. **Approach** (max 5 sec)
   - Slow approach at speed 30
   - Stop at ideal distance (8cm)
   - Fine positioning

4. **Lower Arm** (1.2 sec)
   - Servo 10 moves to 800
   - Arm reaches down
   - LED: 🔵 Cyan (picking up)

5. **Grab** (0.8 sec)
   - Close gripper (servo 11 → 1000)
   - Secure object

6. **Lift** (1.2 sec)
   - Raise arm (servo 10 → 2000)
   - Object lifted

7. **Success** (1 sec)
   - LED: 🟢 Green (success)
   - Victory nod animation
   - Action complete

### Total Duration: ~6-8 seconds (depending on object distance)

## Configuration

### Distance Settings
```python
DETECTION_DISTANCE = 15  # cm - when to stop walking
PICKUP_DISTANCE = 8      # cm - ideal grab distance
```

### Speed Settings
```python
FORWARD_SPEED = 60       # Walking speed while searching
APPROACH_SPEED = 30      # Slow approach speed
```

### Arm Positions
```python
ARM_BASE_DEFAULT = 500      # Servo 9 - center position
ARM_ELBOW_UP = 2000         # Servo 10 - raised position
ARM_ELBOW_DOWN = 800        # Servo 10 - lowered to grab
GRIPPER_OPEN = 1500         # Servo 11 - open
GRIPPER_CLOSED = 1000       # Servo 11 - closed
```

## LED Status Indicators

| Color | Meaning | Phase |
|-------|---------|-------|
| 🟢 Green | Searching/Success | Scanning or completed |
| 🟡 Yellow | Object detected | Found target |
| 🔵 Cyan | Grabbing | Arm lowering/closing |
| 🔴 Red | Error/Failed | No object found |
| 🟣 Blue | Reset | Arm resetting |

## Object Requirements

### Best Results:
- **Size**: 3-8 cm wide (fits in gripper)
- **Height**: 5-12 cm tall
- **Weight**: < 100g (light objects)
- **Shape**: Cylindrical or box-shaped
- **Surface**: Flat floor, no obstacles

### Ideal Test Objects:
- Small plastic bottles
- Cardboard boxes
- Plastic cups
- Small toys
- Foam blocks

## How to Use in APP

### Bluetooth APP:
1. Connect to MechDog via Bluetooth
2. Navigate to "Actions" menu
3. Select "Custom Action Group"
4. Choose **Action Type: 1** (predefined actions)
5. Choose **Action Number: 16**
6. Press "Execute"

### WiFi IoT (via serial):
```bash
python3 IoT.py
IoT> action 1 16
```

Or send directly:
```
CMD|6|1|16|$
```

## Testing

### Test Procedure:
1. **Setup**:
   - Place object 30-50cm in front of MechDog
   - Object should be 8-10cm tall
   - Clear path to object

2. **Run Action**:
   - Trigger via APP or command
   - Watch LED colors for status
   - MechDog should walk, stop, grab, lift

3. **Success Indicators**:
   - Green LED at end
   - Object held in gripper
   - Victory nod animation

### Troubleshooting:

**Red LED - No Object Found**
- Check object is in front path
- Object might be too small/short
- Try placing object closer (20-30cm)

**Stops Too Early/Late**
- Adjust `DETECTION_DISTANCE` parameter
- Calibrate ultrasonic sensor

**Misses Object**
- Adjust `ARM_ELBOW_DOWN` position
- Object might be too low/high
- Check gripper alignment

**Doesn't Grip**
- Adjust `GRIPPER_CLOSED` value
- Object might be too small/slippery
- Check gripper servo operation

## Advanced Customization

### Adding to Other Programs:

```python
# Import the function
from pickup_object_action import pickup_object, release_object, reset_arm

# Use in your code
if user_wants_pickup:
    success = pickup_object()
    if success:
        # Do something with held object
        pass
    release_object()
```

### Modifying Behavior:

```python
# Change detection range
DETECTION_DISTANCE = 20  # More sensitive

# Adjust approach distance
PICKUP_DISTANCE = 10     # Grab from further

# Speed up action
FORWARD_SPEED = 80       # Walk faster
```

### Adding Voice/Sound:
```python
# After successful pickup
buzzer.playTone(1000, 200, False)  # Success beep
buzzer.playTone(1200, 200, False)
```

## Action Number Reference

| Number | Action Name | Type |
|--------|-------------|------|
| 1 | Left foot kick | Standard |
| 2 | Right foot kick | Standard |
| 3 | Stand four legs | Standard |
| 4 | Sit down | Standard |
| 5 | Go prone | Standard |
| 6 | Stand two legs | Standard |
| 7 | Handshake | Standard |
| 8 | Scrape a bow | Standard |
| 9 | Nodding motion | Standard |
| 10 | Boxing | Standard |
| 11 | Stretch oneself | Standard |
| 12 | Pee | Standard |
| 13 | Press up | Standard |
| 14 | Rotation pitch | Standard |
| 15 | Rotation roll | Standard |
| **16** | **Pick up object** | **Custom ⭐** |

## Demo Video Script

1. Place small bottle 40cm in front of MechDog
2. Trigger action 16 via APP
3. Watch as MechDog:
   - Walks forward (green LED)
   - Detects bottle (yellow LED)
   - Approaches slowly
   - Lowers arm (cyan LED)
   - Grabs bottle
   - Lifts it up (green LED)
   - Does victory nod!

## Safety Notes

⚠️ **Important:**
- Clear workspace of obstacles
- Don't use with heavy objects
- Monitor first few runs
- Keep fingers away from gripper
- Place object on flat surface
- Ensure battery is charged

## Future Enhancements

Possible improvements:
- Add object size detection
- Multiple pickup attempts
- Color-based object selection
- Place object at designated location
- Stack multiple objects
- Integration with camera recognition

---

**Ready to test?** Upload the updated `main_bluetooth_wifi.py` and try action 16! 🤖✨
