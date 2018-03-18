import cv2
import os
import time
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import ftdi1
import thread
import sys

# Configuration variables
#########################

# Note that pin numbers 0 to 15 map to pins D0 to D7 then C0 to C7 on the board.
pinled=14 #C6
pintrip=13 #C5

MAXIT=10000000

##I will need to modify this
SLEEPCHECK=0.01 #Relaxing CPU usage
SLEEPBETWEEN=0.1 #I need to give time for the capacitor to discharge (and in the meantime the CPU rests too)
MAXCYCLESDARK=10

# Init
######

# Temporarily disable the built-in FTDI serial driver on Mac & Linux platforms.
#FT232H.use_FT232H() ##Added fake driver D2xxHelper from FTDI to avoid doing this

# Create an FT232H object that grabs the first available FT232H device found.
ft232h = FT232H.FT232H()

# Configure digital inputs and outputs using the setup function.
ft232h.setup(pinled, GPIO.OUT)   # Make pin D7 a digital output.
ft232h.setup(pintrip, GPIO.OUT)  # Make pin C0 a digital output.

#Normal state
ft232h.output(pintrip, GPIO.LOW) #Discharge capacitor
ft232h.output(pinled,GPIO.LOW) #LED off
time.sleep(1)

##testing now

ft232h.output(pinled,GPIO.HIGH) #LED off
ft232h.setup(pintrip,GPIO.IN)
start = time.time()

for i in xrange(0,int(sys.argv[1])):
    ft232h.input(pintrip)

end = time.time()
print(end - start)

exit()

##Debug

for i in xrange(0,10):
    print "Number of cycles: " , check_tripwire()
for i in xrange(0,10):
    time.sleep(1)
    print "Number of cycles after 1: " , check_tripwire()
for i in xrange(0,10):
    time.sleep(0.1)
    print "Number of cycles after 0.1: " , check_tripwire()
for i in xrange(0,10):
    time.sleep(0.01)
    print "Number of cycles after 0.01: " , check_tripwire()
for i in xrange(0,10):
    time.sleep(0.001)
    print "Number of cycles after 0.001: " , check_tripwire()


exit() ##To remove later

#Future rutine
while 1:
    n_cycles=check_tripwire()
    if n_cycles>MAXCYCLEDARK:
        thread.start_new_thread(blinkled(),()) ##New thread blinking the LED for a given number of time
        trigger_mirror()
    time.sleep(SLEEPBETWEEN) ##Reduce cpu usage

