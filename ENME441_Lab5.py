# ENME441_Lab5

import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)

led_pins = [4,17,27,22,5,6,13,19,26,21]
button_pin = 23

# Sets up outputs
for pin in led_pins:
	GPIO.setup(pin, GPIO.OUT)

# Button uses pull down resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#PWN 

pwms = []
for pin in led_pins:
	pwm_obj = GPIO.PWM(pin, 500)		#500 hz
	pwm_obj.start(0)					# Starts at 0% duty cycle
	pwms.append(pwm_obj)

direction = 1

def button_callback(pin):
	global direction
	direction = direction * (-1)

# Event Detection
GPIO.add_event_detect(button_pin, GPIO.RISING, callback = button_callback, bouncetime = 200)

print("Waving, click button to switch direction")

try:
	while True:
		# Get current time
		t = time.time()

		#Update each LED
		for i in range(len(led_pins)):
			phase = i * (math.pi / 11) * direction

			# B = (sin(2 * pi * f * t - phi))^2 where f = 0.2 Hz
			brightness = (math.sin(2 * math.pi * 0.2 * t - phase))
			brightness = brightness * brightness

			duty_cycle = brightness * 100

			pwms[i].ChangeDutyCycle(duty_cycle)

except KeyboardInterrupt:
	print("\nKeeb Interrupt")

except Exception as e:
	print (f"\nError: {e}")

finally: 
	for pwm_obj in pwms:
		pwm_obj.stop()
	GPIO.cleanup()
	print("GPIO cleanup completed")



