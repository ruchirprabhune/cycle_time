import cv2
import numpy as np
import streamlit as st
import os

# Global variable to store points
polygon_points = []

def mouse_callback(event, x, y, flags, param):
    """Handles mouse click events to capture four points."""
    global polygon_points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(polygon_points) < 4:
            polygon_points.append((x, y))
        if len(polygon_points) == 4:
            cv2.destroyAllWindows()

def select_roi(video_path):
    """
    Selects a polygonal ROI from the first frame of the given video using OpenCV.
    Returns the selected ROI coordinates as a list of four (x, y) points.
    """
    global polygon_points
    polygon_points = []  # Reset points
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error: Could not open video file.")
        return None
    
    ret, frame = cap.read()
    cap.release()

    if not ret:
        st.error("Error: Could not read the first frame of the video.")
        return None
    
    clone = frame.copy()
    cv2.namedWindow("Select ROI")
    cv2.setMouseCallback("Select ROI", mouse_callback)

    st.write("### Click on four points to define the ROI in the OpenCV window.")
    st.write("Close the window after selecting four points.")
    
    while len(polygon_points) < 4:
        temp_frame = clone.copy()
        for point in polygon_points:
            cv2.circle(temp_frame, point, 5, (0, 0, 255), -1)
        if len(polygon_points) == 4:
            cv2.polylines(temp_frame, [np.array(polygon_points)], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.imshow("Select ROI", temp_frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
            break
    
    cv2.destroyAllWindows()
    
    if len(polygon_points) == 4:
        st.success(f"ROI Selected: {polygon_points}")
        return polygon_points
    else:
        st.warning("ROI selection was not completed.")
        return None

