import cv2
import numpy as np
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os

# Initialize session state for ROI points
if "roi_points" not in st.session_state:
    st.session_state.roi_points = []

def select_roi(video_path):
    """ Allows user to select a polygonal ROI by clicking on a frame using an interactive canvas. """

    # Check if file exists
    if not os.path.exists(video_path):
        st.error(f"Error: Video file not found at {video_path}")
        return None

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        st.error("Error: Could not open video file.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        st.error("Error: Could not read the first frame of the video. Ensure the file is not corrupted.")
        return None

    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except cv2.error:
        st.error("Error: Failed to convert the frame to RGB.")
        return None

    if frame_rgb is None or frame_rgb.size == 0:
        st.error("Error: Invalid frame content.")
        return None

    # Convert OpenCV image to PIL format for Streamlit
    img = Image.fromarray(frame_rgb)

    # Display instructions
    st.write("### Click four points to define a polygonal ROI.")

    # Streamlit Canvas for ROI Selection
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Transparent red
        stroke_width=2,
        stroke_color="red",
        background_image=img,  # ✅ Fixed: Use PIL image instead of NumPy array
        height=frame.shape[0],
        width=frame.shape[1],
        drawing_mode="point",
        key="canvas",
    )

    # Capture clicked points
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if len(objects) == 4:
            st.session_state.roi_points = [(int(obj["left"]), int(obj["top"])) for obj in objects]

    # Show selected points
    if len(st.session_state.roi_points) == 4:
        st.success(f"ROI Selected: {st.session_state.roi_points}")

    # Confirm selection
    if st.button("Confirm ROI Selection"):
        if len(st.session_state.roi_points) == 4:
            return st.session_state.roi_points
        else:
            st.error("Please select exactly 4 points.")

    return None
