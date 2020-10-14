import pigpio         

#import evdev
from evdev import InputDevice, categorize, ecodes

pi = pigpio.pi()

gamepad = InputDevice('/dev/input/event10')

#Right JoyStick
leftRJoy = 2
rightRJoy = 2
upRJoy = 5
downRJoy = 5

pi.set_servo_pulsewidth(20,1950)

while True:
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_ABS:
            if -2500 <=event.value < 0:
                if event.code == upRJoy:
                    pi.set_servo_pulsewidth(20,2500)
            elif 0 < event.value <= 2500:
                if event.code == downRJoy:
                    pi.set_servo_pulsewidth(20,1950)
