from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from datetime import datetime
import base64
from ultralytics import YOLO
import io
from PIL import Image

app = FastAPI(title="Raspberry Pi Object Detection API")

# Initialize YOLO model (using YOLOv8n for better performance on RPi)
try:
    model = YOLO('yolov8n.pt')  # nano model for Raspberry Pi
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

def capture_image():
    """Capture image from webcam"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Could not open webcam")
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise HTTPException(status_code=500, detail="Could not capture image")
    
    return frame

def detect_objects(image):
    """Run YOLO detection on image"""
    if model is None:
        raise HTTPException(status_code=500, detail="YOLO model not loaded")
    
    results = model(image)
    return results[0]

def render_detections(image, results):
    """Draw bounding boxes and labels on image"""
    annotated_image = results.plot()
    return annotated_image

def image_to_base64(image):
    """Convert image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

@app.get("/")
async def root():
    return {"message": "Raspberry Pi Object Detection API", "endpoint": "/detect"}

@app.post("/detect")
async def detect():
    """
    Capture image from webcam, detect objects, and return results
    """
    try:
        # Capture image
        frame = capture_image()
        
        # Get timestamp
        timestamp = datetime.now().isoformat()
        
        # Detect objects
        results = detect_objects(frame)
        
        # Render detections on image
        annotated_image = render_detections(frame, results)
        
        # Extract detection information
        detections = []
        object_counts = {}
        
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            
            detections.append({
                "class": class_name,
                "confidence": round(confidence, 2),
                "bounding_box": {
                    "x1": round(bbox[0], 2),
                    "y1": round(bbox[1], 2),
                    "x2": round(bbox[2], 2),
                    "y2": round(bbox[3], 2)
                }
            })
            
            # Count objects
            object_counts[class_name] = object_counts.get(class_name, 0) + 1
        
        # Convert annotated image to base64
        annotated_base64 = image_to_base64(annotated_image)
        
        # Prepare response
        response = {
            "timestamp": timestamp,
            "total_objects": len(detections),
            "object_counts": object_counts,
            "detections": detections,
            "annotated_image": f"data:image/jpeg;base64,{annotated_base64}"
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check if camera and model are working"""
    camera_ok = False
    model_ok = model is not None
    
    try:
        cap = cv2.VideoCapture(0)
        camera_ok = cap.isOpened()
        cap.release()
    except:
        pass
    
    return {
        "camera": "ok" if camera_ok else "error",
        "model": "ok" if model_ok else "error"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)