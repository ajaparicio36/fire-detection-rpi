import RPi.GPIO as GPIO
import time

# Just test a single pin first
TEST_PIN = 17

GPIO.setwarnings(False)  # Disable warnings temporarily for testing
GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_PIN, GPIO.IN)

print(f"Testing pin {TEST_PIN}")
print(f"Current value: {GPIO.input(TEST_PIN)}")

GPIO.cleanup()