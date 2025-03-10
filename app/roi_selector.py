import cv2
import numpy as np
import streamlit as st
from PIL import Image

# Initialize session state for storing ROI points
if "roi_points" not in st.session_state:
    st.session_state.roi_points = []

def select_roi(video_path):
    """ 
    Allows user to select a polygonal ROI by clicking on a frame using Streamlit's interactive image.
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

    # Convert frame to RGB for display in Streamlit
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert OpenCV image to PIL format for Streamlit
    img = Image.fromarray(frame_rgb)

    # Display instructions
    st.write("### Click four points to define a polygonal ROI.")

    # Display image for selection
    selected_points = st.session_state.roi_points

    # Use Streamlit's image-clicking function (Streamlit doesn't support native OpenCV mouse events)
    clicked = st.image(img, caption="Click to Select ROI", use_column_width=True)

    # Button to confirm selection
    if st.button("Confirm ROI Selection"):
        if len(selected_points) != 4:
            st.error("Please select exactly 4 points before confirming.")
            return None
        else:
            st.success(f"ROI Selected: {selected_points}")
            return selected_points

    return None
