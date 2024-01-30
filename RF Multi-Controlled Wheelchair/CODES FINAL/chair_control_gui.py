import RPi.GPIO as GPIO
import time
from tkinter import *
import tkinter.font as tkFont

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#Control pins for the motor driver
in1 = 29
in2 = 31
in3 = 33
in4 =37

GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
from gpiozero import Motor, DistanceSensor
from time import sleep

# Ultrasonic sensor pins
echo_front = 36
trigger_front = 32
echo_back = 40
trigger_back = 38
obstacle_threshold = 0.1  # 10 cm

# Create ultrasonic sensor object
ultrasonic_sensor = DistanceSensor(echo=echo_front, trigger=trigger_front)
ultrasonic_sensor2 = DistanceSensor(echo=echo_back, trigger=trigger_back)   



win = Tk()

myFont = tkFont.Font(family = 'Helvetica', size = 36, weight = 'bold')

def forward():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)

def reverse():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

def right():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    time.sleep(1)
    
def left():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    time.sleep(1)

def stop():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
try:

win.title('Wheelchair Control')
win.geometry('480x320')


frontButton = Button(win, text = 'Front', font = myFont, command = forward, height = 1, width = 4)
frontButton.pack(side = TOP)

leftButton = Button(win, text = 'Left', font = myFont, command = left, height = 1, width = 4)
leftButton.pack(side = LEFT)

rightButton = Button(win, text = 'Right', font = myFont, command = right, height = 1, width = 4)
rightButton.pack(side = RIGHT)

stopButton = Button(win, text = 'Stop', font = myFont, command = stop, height = 1, width = 4)
stopButton.pack(side = BOTTOM)

win.mainloop()

