# ai-server/app.py
from flask import Flask, request, jsonify, Response
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FireDetectionModel:
    def __init__(self, model_path='model/best.pt'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        try:
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def process_frame(self, frame):
        try:
            results = self.model(frame)
            detections = []
            for pred in results.xyxy[0]:
                x1, y1, x2, y2, conf, cls = pred.cpu().numpy()
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': float(conf),
                    'class': int(cls)
                })
            annotated_frame = results.render()[0]
            return detections, annotated_frame
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return [], frame

try:
    model = FireDetectionModel()
except Exception as e:
    logger.error(f"Failed to initialize model: {str(e)}")
    raise

def decode_base64_image(base64_string):
    try:
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
        return img
    except Exception as e:
        logger.error(f"Error decoding image: {str(e)}")
        return None

def encode_frame_base64(frame):
    try:
        if frame is None:
            raise ValueError("Frame is None")
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding frame: {str(e)}")
        return None

@app.route('/detect', methods=['POST'])
def detect_fire():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400

        frame = decode_base64_image(data['image'])
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400

        detections, annotated_frame = model.process_frame(frame)
        processed_frame_base64 = encode_frame_base64(annotated_frame)
        
        if processed_frame_base64 is None:
            return jsonify({'error': 'Failed to process frame'}), 500

        response_data = {
            'detections': detections,
            'processed_frame': processed_frame_base64
        }
        
        return Response(
            response=json.dumps(response_data),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)