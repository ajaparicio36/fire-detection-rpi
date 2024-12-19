import RPi.GPIO as GPIO
from typing import Callable
import time

class GPIOHandler:
    def __init__(self):
        # Disable warnings since we know we're handling cleanup properly
        GPIO.setwarnings(False)
        
        # Set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        
        # Pin definitions
        self.SMOKE_DETECTOR_PIN = 27  # Physical pin 11
        self.ALARM_PIN = 18          # Physical pin 12
        
        # Setup pins
        GPIO.setup(self.SMOKE_DETECTOR_PIN, GPIO.IN)
        GPIO.setup(self.ALARM_PIN, GPIO.OUT)
        GPIO.output(self.ALARM_PIN, GPIO.LOW)
        
        self._smoke_callback = None
        self._is_monitoring = False
        
    def setup_smoke_detection(self, callback: Callable[[bool], None]):
        """Set up smoke detector monitoring"""
        self._smoke_callback = callback
        self._is_monitoring = True
        
        # Start monitoring in a more basic way
        self._last_state = GPIO.input(self.SMOKE_DETECTOR_PIN)
        self._monitor_smoke_detector()
    
    def _monitor_smoke_detector(self):
        """Monitor the smoke detector state"""
        if not self._is_monitoring:
            return
            
        current_state = GPIO.input(self.SMOKE_DETECTOR_PIN)
        if current_state != self._last_state:
            if self._smoke_callback:
                self._smoke_callback(current_state)
            self._last_state = current_state
            time.sleep(0.3)  # Simple debounce
            
        # Schedule the next check
        if self._is_monitoring:
            time.sleep(0.1)  # Check every 100ms
            self._monitor_smoke_detector()
    
    def set_alarm(self, state: bool):
        """Control the alarm output"""
        GPIO.output(self.ALARM_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    def cleanup(self):
        """Clean up GPIO on shutdown"""
        self._is_monitoring = False  # Stop the monitoring loop
        GPIO.cleanup()