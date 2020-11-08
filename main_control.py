import pygame
import pigpio
import RPi.GPIO as GPIO

pygame.init()
pi = pigpio.pi()

in1 = 24
in2 = 23
en1 = 25
in3 = 17
in4 = 27
en2 = 22

temp1 = 1

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en1,GPIO.OUT)

GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2,GPIO.OUT)

GPIO.setup(26, GPIO.OUT)

GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)

GPIO.output(26, GPIO.LOW)

pi.set_servo_pulsewidth(21,2200)

#motor PWM
p = GPIO.PWM(en1,1000)
m = GPIO.PWM(en2,1000)

#starting motor at 25% duty cycle
p.start(25)
m.start(25)

win = pygame.display.set_mode((200, 200))
pygame.display.set_caption("Motor Controls")
pygame.key.set_repeat(100, 100)

run = True 
 
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            #Forward
            if event.key == pygame.K_UP:
                GPIO.output(in2,GPIO.HIGH)
                GPIO.output(in4,GPIO.HIGH)
                p.ChangeDutyCycle(100)
                m.ChangeDutyCycle(100)
            #Reverse
            if event.key == pygame.K_DOWN:
                GPIO.output(in1,GPIO.HIGH)
                GPIO.output(in3,GPIO.HIGH)
                p.ChangeDutyCycle(100)
                m.ChangeDutyCycle(100)
            #Turn Left
            if event.key == pygame.K_LEFT:
                GPIO.output(in2,GPIO.HIGH)
                GPIO.output(in3,GPIO.HIGH)
                p.ChangeDutyCycle(100)
                m.ChangeDutyCycle(100)
            #Turn Right
            if event.key == pygame.K_RIGHT:
                GPIO.output(in1,GPIO.HIGH)
                GPIO.output(in4,GPIO.HIGH)
                p.ChangeDutyCycle(100)
                m.ChangeDutyCycle(100)
            #Servo Up
            if event.key == pygame.K_w:
                pi.set_servo_pulsewidth(21,2500)
            #Servo Down
            if event.key == pygame.K_s:
                pi.set_servo_pulsewidth(21,2200)
            #Turn Lights On
            if event.key == pygame.K_1:
                GPIO.output(26,GPIO.HIGH)
            #Turn Lights Off
            if event.key == pygame.K_2:
                GPIO.output(26,GPIO.LOW)
        if event.type == pygame.KEYUP:
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.LOW)
            GPIO.output(in3,GPIO.LOW)
            GPIO.output(in4,GPIO.LOW)
            
            
            
            