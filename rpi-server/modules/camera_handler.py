# rpi-server/modules/camera_handler.py
import cv2
import threading
import time
import requests
import base64
import numpy as np
from typing import Optional
import logging
import json

class CameraHandler:
    def __init__(self, alarm_handler, ai_service_url: str = "http://192.168.1.10:5001/detect"):
        self.alarm_handler = alarm_handler
        self.ai_service_url = ai_service_url
        self.camera = None
        self.is_running = False
        self.thread = None
        self.frame_interval = 1.0
        self.last_frame = None
        self.last_frame_time = 0
        self.last_processed_frame = None
        self.detections = []
        self.frame_count = 0
        
        # Enhanced logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        
    def start(self):
        if self.is_running:
            return
            
        self.logger.info("Attempting to start camera...")
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise RuntimeError("Could not open camera")
                
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Verify camera settings
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"Camera initialized with resolution: {actual_width}x{actual_height}, FPS: {actual_fps}")
            
            self.is_running = True
            self.thread = threading.Thread(target=self._camera_loop)
            self.thread.daemon = True
            self.thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start camera: {str(e)}")
            if self.camera is not None:
                self.camera.release()
                self.camera = None
            raise

    def _camera_loop(self):
        self.logger.info("Camera loop started")
        last_fps_time = time.time()
        frames_this_second = 0
        
        while self.is_running:
            try:
                if not self.camera.isOpened():
                    self.logger.error("Camera is not opened")
                    time.sleep(1)
                    continue

                ret, frame = self.camera.read()
                if not ret:
                    self.logger.error("Failed to capture frame")
                    time.sleep(0.1)
                    continue

                # Update FPS counter
                frames_this_second += 1
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    self.logger.debug(f"FPS: {frames_this_second}")
                    frames_this_second = 0
                    last_fps_time = current_time

                self.last_frame = frame
                self.frame_count += 1

                # Process frame if enough time has passed
                if current_time - self.last_frame_time >= self.frame_interval:
                    self.last_frame_time = current_time
                    self._process_frame(frame)

                time.sleep(0.01)  # Prevent high CPU usage

            except Exception as e:
                self.logger.error(f"Error in camera loop: {str(e)}")
                time.sleep(1)

    def _process_frame(self, frame):
        try:
            # Log frame properties
            self.logger.debug(f"Processing frame {self.frame_count} - Shape: {frame.shape}")
            
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            
            # Send to AI service
            self.logger.debug("Sending frame to AI service...")
            response = requests.post(
                self.ai_service_url,
                json={'image': base64_frame},
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            self.logger.debug(f"AI service response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.detections = result.get('detections', [])
                
                if 'processed_frame' in result:
                    processed_frame_data = base64.b64decode(result['processed_frame'])
                    nparr = np.frombuffer(processed_frame_data, np.uint8)
                    self.last_processed_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if self.last_processed_frame is None:
                        self.logger.error("Failed to decode processed frame")
                    else:
                        self.logger.debug("Successfully decoded processed frame")
                
                # Handle fire detections
                if self.detections:
                    max_confidence = max(det.get('confidence', 0) for det in self.detections)
                    self.alarm_handler.handle_fire_detection(max_confidence)
                
                # Emit frame update
                self._emit_frame_update()
            else:
                self.logger.warning(f"AI service returned status code: {response.status_code}")
                self.logger.warning(f"Response content: {response.text}")
                
        except requests.exceptions.Timeout:
            self.logger.warning("AI service request timed out")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending frame to AI service: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
    # Add this method to the CameraHandler class:

    def _emit_frame_update(self):
        """Emit frame update through socketio"""
        try:
            if hasattr(self, 'socketio'):  # Make sure socketio is available
                frame_data = {
                    'frame': self.get_current_frame_base64(),
                    'processed_frame': self.get_processed_frame_base64(),
                    'detections': self.detections
                }
                self.logger.debug("Emitting frame update")
                self.socketio.emit('frame_update', frame_data)
        except Exception as e:
            self.logger.error(f"Error emitting frame update: {str(e)}")

    def get_current_frame_base64(self) -> Optional[str]:
        """Get the latest frame as base64 string"""
        try:
            if self.last_frame is None:
                return None
            _, buffer = cv2.imencode('.jpg', self.last_frame)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encoding current frame: {str(e)}")
            return None

    def get_processed_frame_base64(self) -> Optional[str]:
        """Get the latest processed frame as base64 string"""
        try:
            if self.last_processed_frame is None:
                return None
            _, buffer = cv2.imencode('.jpg', self.last_processed_frame)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encoding processed frame: {str(e)}")
            return None

    def get_camera_status(self) -> dict:
        """Get current camera status with error handling"""
        try:
            # Default status for when camera isn't initialized
            status = {
                'running': self.is_running,
                'fps': 1 / self.frame_interval if self.frame_interval > 0 else 0,
                'resolution': {
                    'width': 0,
                    'height': 0
                },
                'detections_count': len(self.detections)
            }
            
            # Update resolution if camera is available
            if self.camera and self.camera.isOpened():
                status['resolution'] = {
                    'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                }
            
            self.logger.debug(f"Camera status: {status}")
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting camera status: {str(e)}")
            # Return a safe fallback status
            return {
                'running': False,
                'fps': 0,
                'resolution': {'width': 0, 'height': 0},
                'detections_count': 0
            }
    
    def stop(self):
        """Stop the camera capture thread and release resources"""
        self.logger.info("Stopping camera handler...")
        try:
            # Stop the camera loop
            self.is_running = False
        
            # Wait for the thread to finish if it exists
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
        
            # Release the camera if it's open
            if self.camera and self.camera.isOpened():
                self.camera.release()
                self.camera = None
            
            self.logger.info("Camera handler stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping camera handler: {str(e)}")