import cv2
import numpy as np
import streamlit as st
import os

def select_roi(video_path):
    """
    Selects ROI from the first frame of the given video using OpenCV.
    Returns the selected ROI coordinates (x, y, width, height).
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        st.error("Error: Could not open video file.")
        return None
    
    ret, frame = cap.read()
    cap.release()

    if not ret:
        st.error("Error: Could not read the first frame of the video.")
        return None

    # Convert frame to RGB for Streamlit display
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    st.image(frame_rgb, caption="Select ROI", use_column_width=True)

    # Let user select ROI using input fields
    st.write("### Select ROI Coordinates:")
    x = st.slider("X-coordinate", 0, frame.shape[1], int(frame.shape[1] / 4))
    y = st.slider("Y-coordinate", 0, frame.shape[0], int(frame.shape[0] / 4))
    width = st.slider("Width", 10, frame.shape[1] - x, int(frame.shape[1] / 2))
    height = st.slider("Height", 10, frame.shape[0] - y, int(frame.shape[0] / 2))

    if st.button("Confirm ROI Selection"):
        roi_coords = (x, y, width, height)
        st.success(f"ROI Selected: {roi_coords}")
        return roi_coords

    return None
