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
from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize handlers
gpio_handler = GPIOHandler()
alarm_handler = AlarmHandler(gpio_handler)
camera_handler = CameraHandler(
    alarm_handler,
    ai_service_url="http://192.168.1.10:5001/detect"  # Ensure this matches your AI server address
)
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
            status.update({
                'camera': camera_status,
                'detections': camera_handler.detections  # Include current detections in status
            })
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

def setup_smoke_detection():
    """Set up smoke detection with retry mechanism"""
    def smoke_callback(is_detected):
        # Check if there are any recent fire detections with high confidence
        recent_detections = camera_handler.detections
        if recent_detections:
            max_confidence = max(det.get('confidence', 0) for det in recent_detections)
            if max_confidence >= 0.7 and is_detected:  # Both smoke and fire detected
                alarm_handler.handle_smoke_detection(True)
                print(f"Alarm triggered - Smoke detected with fire confidence: {max_confidence}")
            else:
                print(f"Smoke detected but fire confidence too low: {max_confidence}")
        else:
            # Handle smoke detection without fire detection
            alarm_handler.handle_smoke_detection(is_detected)
            
    try:
        gpio_handler.setup_smoke_detection(smoke_callback)
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
            socketio.emit('frame_update', {
                'frame': frame,
                'processed_frame': camera_handler.get_processed_frame_base64(),
                'detections': camera_handler.detections
            })
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

def cleanup():
    """Cleanup on shutdown"""
    print("Performing cleanup...")
    try:
        status_queue.put(None)  # Stop the broadcast worker
        broadcast_thread.join(timeout=1.0)
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
        camera_handler.start()
        socketio.run(app, 
                    host='0.0.0.0',
                    port=5000, 
                    debug=False,
                    allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        cleanup()