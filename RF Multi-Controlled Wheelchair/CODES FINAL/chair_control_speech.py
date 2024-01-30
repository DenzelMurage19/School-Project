"""
This program will be used to control the wheelchair by voice commands.
We use the SpeechRecognition library as well as Pyaudio for this.
We may experience a lag due to the RAM or the WiFi network.
The words front, back, left, right, stop, and quit will be use for control.
"""
import RPi.GPIO as GPIO
import time
import speech_recognition as sr #Import speech recognition library

r = sr.Recognizer() #Create an instance of the SpeechRecognition library
mic = sr.MicroPhone() #Create an instance of the pyaudio library

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# Ultrasonic sensor pins
echo_front = 36
trigger_front = 32
echo_back = 40
trigger_back = 38
obstacle_threshold = 0.1  # 10 cm

# Create ultrasonic sensor object
ultrasonic_sensor = DistanceSensor(echo=echo_front, trigger=trigger_front)
ultrasonic_sensor2 = DistanceSensor(echo=echo_back, trigger=trigger_back)   




#Control pins for the motor driver
in1 = 29
in2 = 31
in3 = 33
in4 =37
#Set the motor control pins as output pins
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

#Function to move the wheelchair forward
def forward():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)

#Function to move the wheelchair backwards
def reverse():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

#Function to move the wheelchair to the right
def right():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    time.sleep(1)
    stop()
  
#Function to move the wheelchair to the left
def left():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    time.sleep(1)
    stop()

#Function to stop the wheelchair
def stop():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)

#The main program to run forever
while True:
    with mic as source:
        print("Listening to commands...")
        audio = r.listen(source)
    command = r.recognize_google(audio)
    print("You said: ", command)
    
    #Control the wheelchair based on the audio command
    if command == "front":
        print("Moving forward...\n")
        forward()
    if command == "back":
        print("Moving backwards...\n")
        reverse()
    if command == "left":
        print("Turning left...\n")
        left()
    if command == "right":
        print("Turning right...\n")
        right()
    if command == "stop":
        print("Stopping...\n")
        stop()
    if command == "quit":
        print("Bye bye! Have a great time.\n")
        break



