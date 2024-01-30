"""
This program will be used for the nRF24L01 transceiver to receive the control commands for the wheelchair
"""

#Importing the necessary pre-made and custom-made libraries
import sys
import utime
import ustruct as struct
from machine import Pin, SPI, I2C
from nrf24l01 import NRF24L01
from micropython import const
import ultrasonic

#Define the pins to be used for the ultrasonic sensors
trig_front= Pin(21, Pin.OUT) 
echo_front = Pin(20, Pin.IN, Pin.PULL_DOWN)
trig_back = Pin(19, Pin.OUT)
echo_back = Pin(18, Pin.IN, Pin.PULL_DOWN)

#Define the pins for driving the wheelchair via the motor driver
in1 = Pin(12, Pin.OUT)
in2 = Pin(11, Pin.OUT)
in3 = Pin(10, Pin.OUT)
in4 = Pin(9, Pin.OUT)

# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)


#Check the board's platform and initialize the SPI and pins for use with nRF24L01
if sys.platform == "pyboard":
    cfg = {"spi": 2, "miso": "Y7", "mosi": "Y8", "sck": "Y6", "csn": "Y5", "ce": "Y4"}
elif sys.platform == "esp8266":  # Hardware SPI
    cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 4, "ce": 5}
elif sys.platform == "esp32":  # Software SPI
    cfg = {"spi": -1, "miso": 32, "mosi": 33, "sck": 25, "csn": 26, "ce": 27}
elif sys.platform == "rp2": # pico
    cfg = {"spi": 0, "miso": 4, "mosi": 7, "sck": 6, "csn": 17, "ce": 13}
else:
    raise ValueError("Unsupported platform {}".format(sys.platform))

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

#Define the functions for moving the wheelchair
#Stop the wheelchair
def stop():
    in1.value(0)
    in2.value(0)
    in3.value(0)
    in4.value(0)
    
#Move forward
def forward():
    in1.value(0)
    in2.value(1)
    in3.value(0)
    in4.value(1)

#Move backwards
def reverse():
    in1.value(1)
    in2.value(0)
    in3.value(1)
    in4.value(0)
    
#Turn right
def right():
    in1.value(0)
    in2.value(1)
    in3.value(1)
    in4.value(0)
    utime.sleep(1)
    stop()

#Turn left
def left():
    in1.value(1)
    in2.value(0)
    in3.value(0)
    in4.value(1)
    utime.sleep(1)
    stop()

#Function to assign the SPI configuration of the Raspberry Pi Pico for use with the nRF24L01 module
def getSPI():
    if sys.platform == "rp2":
        return  SPI(cfg['spi'],baudrate=400000,sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    else:
        if cfg["spi"] == -1:
            return SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    return SPI(cfg["spi"])


#Function to set the board as a receiver
def slave():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    spi = getSPI()
    nrf = NRF24L01(spi, csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")
    
    command = ""
    while True:      
        #Check for any transmitted signals on our channel
        if nrf.any(): 
            print("Listening...")
            while nrf.any():
                buf = nrf.recv()
                command = struct.unpack("i", buf)
                print("Message received:", command[0])
                utime.sleep_ms(_RX_POLL_DELAY) # delay before next listening
                
                #Control the wheelchair based on the RF accelerometer command
                if command[0] == 1:
                    print("Moving forward...\n")
                    forward()
                if command[0] == 2:
                    print("Moving backwards...\n")
                    reverse()
                if command[0] == 3:
                    print("Turning left...\n")
                    left()
                if command[0] == 4:
                    print("Turning right...\n")
                    right()
                if command[0] == 5:
                    print("Stopping...\n")
                    stop()
                if command[0] == 6:
                    print("Holding state...\n")

            response = command[0]%2 # preparing the response

            utime.sleep_ms(_SLAVE_SEND_DELAY) # Give the other Pico a brief time to listen
            nrf.stop_listening()
            try:
                nrf.send(struct.pack("i", response))
            except OSError:
                pass
            print("reply sent:", response)
            nrf.start_listening()
        
        #Check the distances from the wheelchair to the nearest obstacles in the front
        distance_front = ultrasonic.distance(trig_front, echo_front)
        if ((distance_front > 0) and (distance_front < 15)):
            print("Obstacle detected! Stopping...\n")
            stop()
        
        #Check the distances from the wheelchair to the nearest obstacles in the back
        distance_back = ultrasonic.distance(trig_back, echo_back)
        #Stop the wheelchair in case of an obstacle
        if ((distance_back > 0) and (distance_back < 15)):
            print("Obstacle detected! Stopping...\n")
            stop()
            
        command = ""
        
slave()