import RPi.GPIO as GPIO
from typing import Callable
import time

class GPIOHandler:
    def __init__(self):
        # Clean up any existing GPIO settings first
        GPIO.cleanup()
        
        # Set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        
        # Pin definitions
        self.SMOKE_DETECTOR_PIN = 27  # Physical pin 11
        self.ALARM_PIN = 18          # Physical pin 12
        
        # Setup pins with try-except blocks
        try:
            GPIO.setup(self.SMOKE_DETECTOR_PIN, GPIO.IN)
        except RuntimeError as e:
            print(f"Error setting up smoke detector pin: {e}")
            # Try to remove existing detection before setting up
            try:
                GPIO.remove_event_detect(self.SMOKE_DETECTOR_PIN)
            except:
                pass
            GPIO.setup(self.SMOKE_DETECTOR_PIN, GPIO.IN)
            
        try:
            GPIO.setup(self.ALARM_PIN, GPIO.OUT)
            GPIO.output(self.ALARM_PIN, GPIO.LOW)
        except RuntimeError as e:
            print(f"Error setting up alarm pin: {e}")
            GPIO.cleanup(self.ALARM_PIN)
            GPIO.setup(self.ALARM_PIN, GPIO.OUT)
            GPIO.output(self.ALARM_PIN, GPIO.LOW)
        
        self._smoke_callback = None
        
    def setup_smoke_detection(self, callback: Callable[[bool], None]):
        """Set up smoke detector interrupt with debouncing"""
        self._smoke_callback = callback
        try:
            # Remove any existing event detection first
            GPIO.remove_event_detect(self.SMOKE_DETECTOR_PIN)
        except:
            pass
            
        try:
            GPIO.add_event_detect(
                self.SMOKE_DETECTOR_PIN,
                GPIO.BOTH,
                callback=self._handle_smoke_event,
                bouncetime=300
            )
        except RuntimeError as e:
            print(f"Error setting up event detection: {e}")
            # If that failed, try cleaning up just this pin and retry
            GPIO.cleanup(self.SMOKE_DETECTOR_PIN)
            GPIO.setup(self.SMOKE_DETECTOR_PIN, GPIO.IN)
            GPIO.add_event_detect(
                self.SMOKE_DETECTOR_PIN,
                GPIO.BOTH,
                callback=self._handle_smoke_event,
                bouncetime=300
            )
    
    def _handle_smoke_event(self, channel):
        """Handle smoke detection event with debouncing"""
        if self._smoke_callback:
            is_smoke_detected = GPIO.input(self.SMOKE_DETECTOR_PIN)
            self._smoke_callback(is_smoke_detected)
    
    def set_alarm(self, state: bool):
        """Control the alarm output"""
        try:
            GPIO.output(self.ALARM_PIN, GPIO.HIGH if state else GPIO.LOW)
        except RuntimeError as e:
            print(f"Error setting alarm state: {e}")
            # Try to recover by resetting the pin
            GPIO.cleanup(self.ALARM_PIN)
            GPIO.setup(self.ALARM_PIN, GPIO.OUT)
            GPIO.output(self.ALARM_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    def cleanup(self):
        """Clean up GPIO on shutdown"""
        try:
            GPIO.cleanup()
        except:
            pass