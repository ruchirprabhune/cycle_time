import streamlit as st
import cv2
import numpy as np
import os

# Global variable for storing ROI points
roi_points = []

def extract_first_frame(video_path):
    """Extracts the first frame from the given video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error: Could not open video.")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        st.error("Error: Could not read the first frame.")
        return None
    
    return frame

def click_event(event, x, y, flags, param):
    """Mouse callback function to store clicked points."""
    global roi_points
    if event == cv2.EVENT_LBUTTONDOWN and len(roi_points) < 4:
        roi_points.append((x, y))
        print(f"Point selected: {x}, {y}")

def select_roi(video_path):
    """Opens OpenCV window to select ROI and returns four selected points."""
    global roi_points
    roi_points = []  # Reset points
    
    frame = extract_first_frame(video_path)
    if frame is None:
        return None

    clone = frame.copy()  # Create a copy to draw on
    cv2.namedWindow("Select ROI - Click 4 Points")
    cv2.setMouseCallback("Select ROI - Click 4 Points", click_event)

    while True:
        temp_frame = clone.copy()
        
        # Draw selected points
        for point in roi_points:
            cv2.circle(temp_frame, point, 5, (0, 0, 255), -1)

        cv2.imshow("Select ROI - Click 4 Points", temp_frame)
        key = cv2.waitKey(1) & 0xFF

        # Break loop when 4 points are selected and user presses Enter (key 13)
        if key == 13 and len(roi_points) == 4:
            break

    cv2.destroyAllWindows()
    
    # Convert ROI points to a format usable in Streamlit
    return roi_points

# Streamlit UI
st.title("ROI Selection Tool")
video_path = st.text_input("Enter path to the video file:")

if st.button("Select ROI"):
    if os.path.exists(video_path):
        selected_points = select_roi(video_path)
        if selected_points:
            st.success(f"Selected ROI Points: {selected_points}")
        else:
            st.error("ROI selection failed.")
    else:
        st.error("Invalid video path. Please enter a correct path.")

