import RPi.GPIO as GPIO          

#import evdev
from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event10')

print(gamepad)

#Dpad
up = 17
down = 17
left = 16
right = 16

in1 = 24
in2 = 23
en1 = 25
in3 = 17
in4 = 27
en2 = 22

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en1,GPIO.OUT)

GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2,GPIO.OUT)

GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)

#motor PWM
p = GPIO.PWM(en1,1000)
m = GPIO.PWM(en2,1000)

#starting motor at 25% duty cycle
p.start(25)
m.start(25)

while True:
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.value == 1:
                #Back
                if event.code == down:
                    GPIO.output(in1,GPIO.HIGH)
                    GPIO.output(in3,GPIO.HIGH)
                    p.ChangeDutyCycle(100)
                    m.ChangeDutyCycle(100)
                #Right Turn
                elif event.code == right:
                    GPIO.output(in1,GPIO.HIGH)
                    GPIO.output(in4,GPIO.HIGH)
                    p.ChangeDutyCycle(100)
                    m.ChangeDutyCycle(100)

            elif event.value == -1:
                #Forward
                if event.code == up:
                    GPIO.output(in2,GPIO.HIGH)
                    GPIO.output(in4,GPIO.HIGH)
                    p.ChangeDutyCycle(100)
                    m.ChangeDutyCycle(100)
                #Left Turn 
                if event.code == left:
                    GPIO.output(in2,GPIO.HIGH)
                    GPIO.output(in3,GPIO.HIGH)
                    p.ChangeDutyCycle(100)
                    m.ChangeDutyCycle(100)
            else:
                    GPIO.output(in1,GPIO.LOW)
                    GPIO.output(in2,GPIO.LOW)
                    GPIO.output(in3,GPIO.LOW)
                    GPIO.output(in4,GPIO.LOW)