import RPi.GPIO as GPIO
from typing import Callable
import time

class GPIOHandler:
    def __init__(self):
        # Set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        
        # Pin definitions
        self.SMOKE_DETECTOR_PIN = 11  # Physical pin 11
        self.ALARM_PIN = 12          # Physical pin 12
        
        # Setup pins
        GPIO.setup(self.SMOKE_DETECTOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.ALARM_PIN, GPIO.OUT)
        GPIO.output(self.ALARM_PIN, GPIO.LOW)
        
        self._smoke_callback = None
        
    def setup_smoke_detection(self, callback: Callable[[bool], None]):
        """Set up smoke detector interrupt with debouncing"""
        self._smoke_callback = callback
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
        GPIO.output(self.ALARM_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    def cleanup(self):
        """Clean up GPIO on shutdown"""
        GPIO.cleanup()