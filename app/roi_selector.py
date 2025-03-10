import cv2
import numpy as np
import streamlit as st

# Store the selected points in session state
if "roi_points" not in st.session_state:
    st.session_state.roi_points = []

def select_roi(video_path):
    """ 
    Allows user to select an ROI by clicking on a frame using Streamlit's interactive image.
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

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Display image for selection
    st.write("### Click four points to define a polygonal ROI.")
    selected_points = st.session_state.roi_points

    # Streamlit interactive image click
    clicked = st.image(frame_rgb, caption="Click to Select ROI", use_column_width=True)

    # Mouse click event
    def register_click(x, y):
        if len(selected_points) < 4:
            selected_points.append((x, y))
            st.session_state.roi_points = selected_points  # Store in session state

    # Get clicks
    coords = st.button("Confirm ROI Selection")
    if coords:
        if len(selected_points) != 4:
            st.error("Please select exactly 4 points.")
            return None
        else:
            st.success(f"ROI Selected: {selected_points}")
            return selected_points

    return None
