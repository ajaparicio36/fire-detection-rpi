# server.py
from flask import Flask
from flask_socketio import SocketIO
from modules.gpio_handler import GPIOHandler
from modules.alarm_handler import AlarmHandler
from modules.camera_handler import CameraHandler
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize handlers
gpio_handler = GPIOHandler()
alarm_handler = AlarmHandler(gpio_handler)
camera_handler = CameraHandler(alarm_handler)

def broadcast_status(status):
    """Broadcast status updates to all clients"""
    camera_status = camera_handler.get_camera_status()
    status.update({'camera': camera_status})
    socketio.emit('status_update', status)

# Set up alarm handler callback
alarm_handler.set_status_callback(broadcast_status)

# Set up smoke detection callback
gpio_handler.setup_smoke_detection(alarm_handler.handle_smoke_detection)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    socketio.emit('status_update', alarm_handler.get_status())

@socketio.on('get_frame')
def handle_get_frame():
    """Send current camera frame to client"""
    frame = camera_handler.get_current_frame_base64()
    if frame:
        socketio.emit('frame_update', {'frame': frame})

@socketio.on('set_enabled')
def handle_set_enabled(enabled):
    """Handle enable/disable requests from clients"""
    alarm_handler.set_enabled(enabled)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    pass

def cleanup():
    """Cleanup on shutdown"""
    camera_handler.stop()
    alarm_handler.deactivate_alarm()
    gpio_handler.cleanup()

if __name__ == '__main__':
    try:
        camera_handler.start()
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        cleanup()