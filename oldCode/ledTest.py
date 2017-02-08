import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
print "LED On :)"
GPIO.output(18, GPIO.HIGH)
time.sleep(5)
print "LED Off :("
GPIO.output(18, GPIO.LOW)
