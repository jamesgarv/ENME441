import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter

GPIO.setmode(GPIO.BCM)

class Bug:
    def __init__(self, timestep = 0.1, x = 3, isWrapOn = False): # Initialize vars
        self.timestep = timestep
        self.x = x                               # Current LED position
        self.isWrapOn = isWrapOn                 # Tracks wrap
        self.__shifter = Shifter(23, 24, 25)     # Controls data, latch, clock
        self._running = False

    # Starts
    def start(self):
        self._running = True

    # Stops
    def stop(self):
        self._running = False
        self.__shifter.shiftByte(0b00000000)    # All LEDs off

    # Move bug once, if bug stopped do nothing
    def step(self, timestep):
        if not self._running:
            return

        # Display current LED position
        pattern = 1 << self.x
        self.__shifter.shiftByte(pattern)    # Sends pattern to shift register

        # Random movement step
        self.x += random.choice([-1, 1])

        # Wrap or bound at edges
        if self.isWrapOn:
            self.x %= 8
        else:
            if self.x < 0:
                self.x = 0
            elif self.x > 7:
                self.x = 7

        time.sleep(timestep)    # Time between movements

dataPin = 23        # SER
latchPin = 24       # Latch
clockPin = 25       # SR Clock

s1 = 17  # Start/Stop
s2 = 27  # Toggle wrap
s3 = 22  # Speed boost

for pin in [s1, s2, s3]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bug = Bug()

# Store wrap condition
last_s2_state = GPIO.input(s2)

# Toggles wrap
def toggle_wrap(channel):
    bug.isWrapOn = not bug.isWrapOn
    print(f"Wrap mode toggled: {bug.isWrapOn}")

GPIO.add_event_detect(s2, GPIO.RISING, callback=toggle_wrap, bouncetime=300)

try:
    while True:
        if GPIO.input(s1):
            if not bug._running:
                bug.start()
        else:
            if bug._running:
                bug.stop()
        if GPIO.input(s3):
            current_step = bug.timestep / 3    # 3x speed
        else:
            current_step = bug.timestep
        bug.step(current_step)
except KeyboardInterrupt:
    bug.stop()
    GPIO.cleanup()
