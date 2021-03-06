import cv2
import os
import time
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import ftdi1
import thread
from sharedconfig import *
import requests
import simplejson as json

#Functions
##########

#Shows the camera, mirrored for a given time in the center on the screen. Then, the window is minimized
def trigger_mirror(time=5): #5 s
    cam = cv2.VideoCapture(CAM_DEVICE_NUMBER)
    cv2.startWindowThread()
    cv2.namedWindow("Tripware")
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''') #Dirty way of bringing the window automatically up front. It seems there isn't a cleaner way
    thread.start_new_thread(os.system,(applescript,)) #Centering the window and eliminating the miniaturization
    img_counter = 0
    nframes=time*25
    for i in xrange(0,nframes):
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow("Tripware", frame)
        cv2.waitKey(1)
###Problems with cv2 closing the window. In order to avoid this, I am minimizing it
    thread.start_new_thread(os.system,('''/usr/bin/osascript -e 'tell app "Python" to set miniaturized of every window to true' ''',))
    #The window needs to be refreshed for the apple-script to work
    for i in xrange(0,10):
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow("Tripware", frame)
        cv2.waitKey(1)
    cam.release()
#    for i in xrange(0,25):
#        cv2.destroyAllWindows()
#        cv2.waitKey(1)

#Function to measure the number of iterations needed to load the capacitor until reaching GPIO.HIGH
def check_tripwire():
    it=0
    level=GPIO.LOW
    ft232h.setup(pintrip,GPIO.IN)
    while (it<MAXIT and level==GPIO.LOW):
        level=ft232h.input(pintrip)
        it=it+1
    ft232h.setup(pintrip,GPIO.OUT)
    ft232h.output(pintrip,GPIO.LOW) #Start discharging the capacitor
    return it

##Blinks a led for a given time at a given frequency
def blinkled(blinking,freq=0.1,length=5):
    blinking.switchOn()
    n_blinks=length/freq #number of blink cycles (freq relates to each event, both on and off, that's why the 2)
    for i in xrange(0,int(n_blinks)):
        ft232h.output(pinled,GPIO.HIGH)
        time.sleep(freq/2)
        ft232h.output(pinled,GPIO.LOW)
        time.sleep(freq/2)
    blinking.switchOff()

##Blinks a led forever using the input pull-up as +. On and off times in seconds 
def watching(blinking,on=0.5,off=4.5):
    while 1:
        if blinking.readswitch():
            #print "Avoiding watching blinking";
            return None
    
        ft232h.setup(pinled,GPIO.IN) #Using the pull-up as a less-intense output
        #print "Hi"
        time.sleep(on)
        ft232h.setup(pinled,GPIO.OUT)
        ft232h.output(pinled,GPIO.LOW)
        if blinking.readswitch():
            #print "Avoiding watching blinking";
            return None
        time.sleep(off)

def notify():
    data = {'text': slackText, 'icon_emoji' : slackIcon, 'username' : slackUsername}
    headers = {'Content-type': 'application/json'}
    r = requests.post(slackUrl, data=json.dumps(data), headers=headers)

# Configuration variables
#########################

# Note that pin numbers 0 to 15 map to pins D0 to D7 then C0 to C7 on the board.
pinled=14 #C6
pintrip=13 #C5
SLEEPBETWEEN=0.02 #I need to give time for the capacitor to discharge (and in the meantime the CPU rests too)
MAXCYCLESDARK=1
MAXIT=100
CAM_DEVICE_NUMBER=1

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

#Class to have a global switch controled by the threads
class globalswitch:
        state=False
        def switchOn(self):
            self.state=True
        def switchOff(self):
            self.state=False
        def readswitch(self):
            return self.state

is_blinking=globalswitch()
is_blinking.switchOff()

thread.start_new_thread(watching,(is_blinking,)) ##New thread blinking the LED slowly until the alarm is activated

while 1:
    n_cycles=check_tripwire()
    if n_cycles>MAXCYCLESDARK:
        thread.start_new_thread(blinkled,(is_blinking,)) ##New thread blinking the LED for a given number of time
        trigger_mirror()
        thread.start_new_thread(notify,()) ##Notify Slack
        thread.start_new_thread(watching,(is_blinking,)) ##New thread blinking the LED slowly until the alarm is activated
    time.sleep(SLEEPBETWEEN) ##Discharge capacitor
