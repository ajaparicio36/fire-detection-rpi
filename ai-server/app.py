# model_server.py
from flask import Flask, request, jsonify
import torch
import base64
import cv2
import numpy as np
from PIL import Image
import io
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FireDetectionModel:
    def __init__(self, model_path='model/best.pt'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        try:
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                      path=model_path, force_reload=True)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def process_frame(self, frame):
        """
        Process a frame and return detections
        """
        try:
            # Inference
            results = self.model(frame)
            
            # Convert results to JSON-serializable format
            detections = []
            for pred in results.xyxy[0]:  # Get predictions for first image
                x1, y1, x2, y2, conf, cls = pred.cpu().numpy()
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': float(conf),
                    'class': int(cls)
                })
            
            # Draw boxes on frame
            annotated_frame = results.render()[0]  # BGR format
            
            return detections, annotated_frame
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return [], frame

# Initialize model
try:
    model = FireDetectionModel()
except Exception as e:
    logger.error(f"Failed to initialize model: {str(e)}")
    raise

def decode_base64_image(base64_string):
    """Decode base64 image to cv2 format"""
    try:
        # Decode base64 string
        img_data = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(img_data, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img
    except Exception as e:
        logger.error(f"Error decoding image: {str(e)}")
        return None

def encode_frame_base64(frame):
    """Encode frame to base64"""
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding frame: {str(e)}")
        return None

@app.route('/detect', methods=['POST'])
def detect_fire():
    try:
        # Get image from request
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
            
        # Decode image
        frame = decode_base64_image(data['image'])
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
            
        # Process frame
        detections, annotated_frame = model.process_frame(frame)
        
        # Encode processed frame
        processed_frame_base64 = encode_frame_base64(annotated_frame)
        
        return jsonify({
            'detections': detections,
            'processed_frame': processed_frame_base64
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)