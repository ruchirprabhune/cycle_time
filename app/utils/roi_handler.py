def handle_roi(frame, roi):
    """Crop the frame using the provided ROI coordinates."""
    x1, y1, x2, y2 = roi
    
    # Ensure the coordinates are within bounds
    height, width, _ = frame.shape
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)
    
    roi_frame = frame[y1:y2, x1:x2]
    return roi_frame

