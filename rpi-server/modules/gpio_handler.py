import RPi.GPIO as GPIO
from typing import Callable
import time
import threading

class GPIOHandler:
    def __init__(self):
        GPIO.setwarnings(False)
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
        self._monitor_thread = None
        
    def setup_smoke_detection(self, callback: Callable[[bool], None]):
        """Set up smoke detector monitoring"""
        self._smoke_callback = callback
        self._is_monitoring = True
        
        # Start monitoring in a separate thread
        self._monitor_thread = threading.Thread(target=self._monitor_smoke_detector)
        self._monitor_thread.daemon = True  # Thread will stop when main program stops
        self._monitor_thread.start()
    
    def _monitor_smoke_detector(self):
        """Monitor the smoke detector state"""
        last_state = GPIO.input(self.SMOKE_DETECTOR_PIN)
        
        while self._is_monitoring:
            current_state = GPIO.input(self.SMOKE_DETECTOR_PIN)
            if current_state != last_state:
                if self._smoke_callback:
                    self._smoke_callback(current_state)
                last_state = current_state
                time.sleep(0.3)  # Simple debounce
            
            time.sleep(0.1)  # Check every 100ms
    
    def set_alarm(self, state: bool):
        """Control the alarm output"""
        GPIO.output(self.ALARM_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    def cleanup(self):
        """Clean up GPIO on shutdown"""
        self._is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)  # Wait for monitoring to stop
        GPIO.cleanup()