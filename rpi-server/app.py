from flask import Flask
from flask_socketio import SocketIO
from modules.gpio_handler import GPIOHandler
from modules.alarm_handler import AlarmHandler
from modules.camera_handler import CameraHandler
import threading
import time
import signal
import sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize handlers
gpio_handler = GPIOHandler()
alarm_handler = AlarmHandler(gpio_handler)
camera_handler = CameraHandler(alarm_handler)

def broadcast_status(status):
    """Broadcast status updates to all clients"""
    try:
        camera_status = camera_handler.get_camera_status()
        status.update({'camera': camera_status})
        socketio.emit('status_update', status)
    except Exception as e:
        print(f"Error broadcasting status: {e}")

# Set up alarm handler callback
alarm_handler.set_status_callback(broadcast_status)

# Set up smoke detection callback
def setup_smoke_detection():
    try:
        gpio_handler.setup_smoke_detection(alarm_handler.handle_smoke_detection)
    except Exception as e:
        print(f"Error setting up smoke detection: {e}")
        # Retry after a delay
        threading.Timer(5.0, setup_smoke_detection).start()

setup_smoke_detection()

@socketio.on('control_alarm')
def handle_alarm_control(active):
    """Handle manual alarm control requests from clients"""
    try:
        if active:
            alarm_handler.activate_alarm()
        else:
            alarm_handler.deactivate_alarm()
        # Broadcast updated status to all clients
        broadcast_status(alarm_handler.get_status())
    except Exception as e:
        print(f"Error handling alarm control: {e}")
        socketio.emit('error', {'message': 'Failed to control alarm'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        socketio.emit('status_update', alarm_handler.get_status())
    except Exception as e:
        print(f"Error handling connection: {e}")

@socketio.on('get_frame')
def handle_get_frame():
    """Send current camera frame to client"""
    try:
        frame = camera_handler.get_current_frame_base64()
        if frame:
            socketio.emit('frame_update', {'frame': frame})
    except Exception as e:
        print(f"Error getting frame: {e}")

@socketio.on('set_enabled')
def handle_set_enabled(enabled):
    """Handle enable/disable requests from clients"""
    try:
        alarm_handler.set_enabled(enabled)
    except Exception as e:
        print(f"Error setting enabled state: {e}")
        socketio.emit('error', {'message': 'Failed to set enabled state'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    pass

def cleanup():
    """Cleanup on shutdown"""
    print("Performing cleanup...")
    try:
        camera_handler.stop()
        alarm_handler.deactivate_alarm()
        gpio_handler.cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("Shutdown signal received...")
    cleanup()
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start camera handler
        camera_handler.start()
        
        # Start the Flask-SocketIO server
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        cleanup()