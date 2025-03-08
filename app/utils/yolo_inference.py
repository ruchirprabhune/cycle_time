import torch
from ultralytics import YOLO

# Initialize the YOLO model with the trained weights
model = YOLO("C:/Users/Ruchir/project_directory/cycle_time.v5i.yolov8/runs/detect/train4/weights/best.pt").to('cpu')


def run_yolo_inference(frame):
    """
    Perform YOLO inference on a single frame.
    Returns a list of detected bounding boxes [(x1, y1, x2, y2), ...].
    """
    # Perform inference on the frame
    results = model(frame)

    # Check if results is a valid object and contains bounding box data
    detections = []
    
    # If results contains multiple images (in case of batch inference), access the first image's results
    if isinstance(results, list):
        results = results[0]
    
    # Loop through each detection (e.g., for every object detected in the frame)
    for det in results.boxes:  # 'boxes' contains the bounding boxes information
        # Extract bounding box coordinates, confidence score, and class ID
        x1, y1, x2, y2 = det.xyxy[0]  # Extracting the bounding box coordinates (x1, y1, x2, y2)
        conf = det.conf[0]  # Confidence score
        cls = det.cls[0]  # Class ID
        
        # Append the detection result (bounding box as integers)
        detections.append((int(x1), int(y1), int(x2), int(y2)))

    return detections
