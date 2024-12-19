# camera_handler.py
import cv2
import threading
import time
import requests
import base64
import numpy as np
from typing import Optional, Callable
import logging
import json

class CameraHandler:
    def __init__(self, alarm_handler, ai_service_url: str = "http://192.168.1.10:5001/detect"):
        self.alarm_handler = alarm_handler
        self.ai_service_url = ai_service_url
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_interval = 1.0  # Process one frame per second
        self.last_frame = None
        self.last_frame_time = 0
        self.logger = logging.getLogger(__name__)
        self.last_processed_frame = None
        self.detections = []
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)

    def start(self):
        """Start the camera capture thread"""
        if self.is_running:
            return

        self.camera = cv2.VideoCapture(0)  # Use default camera
        if not self.camera.isOpened():
            raise RuntimeError("Could not start camera")

        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_running = True
        self.thread = threading.Thread(target=self._camera_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Camera handler started")

    def stop(self):
        """Stop the camera capture thread"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.camera:
            self.camera.release()
        self.camera = None
        self.logger.info("Camera handler stopped")

    def _camera_loop(self):
        """Main camera capture and processing loop"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.error("Failed to capture frame")
                    time.sleep(1)
                    continue

                self.last_frame = frame
                
                # Process frame if enough time has passed
                if current_time - self.last_frame_time >= self.frame_interval:
                    self.last_frame_time = current_time
                    self._process_frame(frame)
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.01)

            except Exception as e:
                self.logger.error(f"Error in camera loop: {str(e)}")
                time.sleep(1)

    def _process_frame(self, frame):
        """Process frame and send to AI service"""
        try:
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')

            # Send to AI service
            response = requests.post(
                self.ai_service_url,
                json={'image': base64_frame},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                self.detections = result.get('detections', [])
                
                # Decode and store processed frame
                if 'processed_frame' in result:
                    processed_frame_data = base64.b64decode(result['processed_frame'])
                    nparr = np.frombuffer(processed_frame_data, np.uint8)
                    self.last_processed_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Handle fire detections
                if self.detections:
                    max_confidence = max(
                        det.get('confidence', 0) 
                        for det in self.detections
                    )
                    self.alarm_handler.handle_fire_detection(max_confidence)
                    
                # Emit frame update through socketio
                self._emit_frame_update()

            else:
                self.logger.warning(f"AI service returned status code: {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.warning("AI service request timed out")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending frame to AI service: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
    
    def _emit_frame_update(self):
        """Emit frame update through socketio"""
        if hasattr(self, 'socketio'):  # Make sure socketio is available
            frame_data = {
                'frame': self.get_current_frame_base64(),
                'processed_frame': self.get_processed_frame_base64(),
                'detections': self.detections
            }
            self.socketio.emit('frame_update', frame_data)


    def get_current_frame_base64(self) -> Optional[str]:
        """Get the latest frame as base64 string"""
        if self.last_frame is None:
            return None
            
        _, buffer = cv2.imencode('.jpg', self.last_frame)
        return base64.b64encode(buffer).decode('utf-8')
    
    def get_processed_frame_base64(self) -> Optional[str]:
        """Get the latest processed frame as base64 string"""
        if self.last_processed_frame is None:
            return None
            
        _, buffer = cv2.imencode('.jpg', self.last_processed_frame)
        return base64.b64encode(buffer).decode('utf-8')

    def get_camera_status(self) -> dict:
        """Get current camera status"""
        status = {
            'running': self.is_running,
            'fps': 1 / self.frame_interval if self.frame_interval > 0 else 0,
            'resolution': {
                'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)) if self.camera else 0,
                'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) if self.camera else 0
            },
            'detections_count': len(self.detections)
        }
        return status