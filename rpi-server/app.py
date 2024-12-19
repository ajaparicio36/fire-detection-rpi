from flask import Flask
from flask_socketio import SocketIO
from modules.gpio_handler import GPIOHandler
from modules.alarm_handler import AlarmHandler
from modules.camera_handler import CameraHandler
import threading
import time
import json
import signal
import sys
from queue import Queue

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize handlers
gpio_handler = GPIOHandler()
alarm_handler = AlarmHandler(gpio_handler)
camera_handler = CameraHandler(alarm_handler)
# After creating camera_handler
camera_handler.socketio = socketio

# Create a queue for status updates
status_queue = Queue()

def status_broadcast_worker():
    """Worker thread to handle status broadcasts"""
    while True:
        try:
            status = status_queue.get()
            if status is None:  # Poison pill to stop the worker
                break
            camera_status = camera_handler.get_camera_status()
            status.update({'camera': camera_status})
            socketio.emit('status_update', status, namespace='/')
        except Exception as e:
            print(f"Error in status broadcast worker: {e}")
        finally:
            status_queue.task_done()

# Start the broadcast worker thread
broadcast_thread = threading.Thread(target=status_broadcast_worker)
broadcast_thread.daemon = True
broadcast_thread.start()

def broadcast_status(status):
    """Queue status updates for broadcasting"""
    try:
        status_queue.put(status)
    except Exception as e:
        print(f"Error queueing status update: {e}")

# Set up alarm handler callback
alarm_handler.set_status_callback(broadcast_status)

# Set up smoke detection callback
def setup_smoke_detection():
    try:
        gpio_handler.setup_smoke_detection(alarm_handler.handle_smoke_detection)
    except Exception as e:
        print(f"Error setting up smoke detection: {e}")
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
        # Queue status update
        broadcast_status(alarm_handler.get_status())
    except Exception as e:
        print(f"Error handling alarm control: {e}")
        socketio.emit('error', {'message': 'Failed to control alarm'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        broadcast_status(alarm_handler.get_status())
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
        # Stop the broadcast worker
        status_queue.put(None)
        broadcast_thread.join(timeout=1.0)
        
        # Cleanup handlers
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
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        cleanup()