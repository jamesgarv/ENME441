import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class Shifter:
    def __init__(self, dataPin, latchPin, clockPin):
        self.dataPin = dataPin         # Pin 14 (SER)
        self.latchPin = latchPin       # Pin 12 (RCLK)
        self.clockPin = clockPin       # Pin 11 (SRCLK)
    
        # initialize pins as LOW
        GPIO.setup(self.dataPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT, initial=0)
        GPIO.setup(self.clockPin, GPIO.OUT, initial=0)
    
    def _ping(self, pin):
        GPIO.output(pin, 1)    # HIGH
        time.sleep(0.00001)    # wait 10ms
        GPIO.output(pin, 0)    # LOW
        time.sleep(0.00001)    # wait 10ms

    # Sends 8 bit pattern to shift register starting with LSB
    def shiftByte(self, pattern):
        for i in range(8):
            GPIO.output(self.dataPin, (pattern >> i) & 1)
            self._ping(self.clockPin)    # Pulse clock to shift the bit into the register
        self._ping(self.latchPin)        # Pulse latch to transfer data from shift register to output register
