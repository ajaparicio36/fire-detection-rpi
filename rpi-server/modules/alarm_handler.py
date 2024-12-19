from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable
import threading
import time

@dataclass
class AlarmEvent:
    timestamp: datetime
    type: str  # 'smoke' or 'fire'
    source: str  # 'detector' or 'camera'
    active: bool

class AlarmHandler:
    def __init__(self, gpio_handler):
        self.gpio_handler = gpio_handler
        self.alarm_active = False
        self.alarm_enabled = True
        self.last_event: Optional[AlarmEvent] = None
        self.status_callback: Optional[Callable] = None
        self._alarm_thread: Optional[threading.Thread] = None
        self._stop_thread = threading.Event()
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def handle_smoke_detection(self, is_detected: bool):
        """Handle smoke detector state change"""
        if not self.alarm_enabled:
            return
            
        self.last_event = AlarmEvent(
            timestamp=datetime.now(),
            type='smoke',
            source='detector',
            active=is_detected
        )
        
        if is_detected:
            self.activate_alarm()
        else:
            self.deactivate_alarm()
            
        if self.status_callback:
            self.status_callback(self.get_status())
    
    def handle_fire_detection(self, confidence: float):
        """Handle fire detection from camera"""
        if not self.alarm_enabled or confidence < 0.7:  # Confidence threshold
            return
            
        self.last_event = AlarmEvent(
            timestamp=datetime.now(),
            type='fire',
            source='camera',
            active=True
        )
        
        self.activate_alarm()
        
        if self.status_callback:
            self.status_callback(self.get_status())
    
    def activate_alarm(self):
        """Activate the alarm with pulsing pattern"""
        if not self.alarm_active:
            self.alarm_active = True
            self._stop_thread.clear()
            self._alarm_thread = threading.Thread(target=self._pulse_alarm)
            self._alarm_thread.start()
    
    def deactivate_alarm(self):
        """Deactivate the alarm"""
        if self.alarm_active:
            self._stop_thread.set()
            if self._alarm_thread:
                self._alarm_thread.join()
            self.alarm_active = False
            self.gpio_handler.set_alarm(False)
    
    def _pulse_alarm(self):
        """Pulse the alarm in a separate thread"""
        while not self._stop_thread.is_set():
            self.gpio_handler.set_alarm(True)
            time.sleep(0.5)
            self.gpio_handler.set_alarm(False)
            time.sleep(0.5)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the alarm system"""
        self.alarm_enabled = enabled
        if not enabled:
            self.deactivate_alarm()
        
        if self.status_callback:
            self.status_callback(self.get_status())
    
    def get_status(self):
        """Get current alarm system status"""
        return {
            'enabled': self.alarm_enabled,
            'active': self.alarm_active,
            'last_event': {
                'timestamp': self.last_event.timestamp.isoformat() if self.last_event else None,
                'type': self.last_event.type if self.last_event else None,
                'source': self.last_event.source if self.last_event else None,
                'active': self.last_event.active if self.last_event else None
            }
        }