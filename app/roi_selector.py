import streamlit as st
import cv2
import numpy as np
import os
from streamlit_drawable_canvas import st_canvas

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

    # Convert BGR to RGB for Streamlit display
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    return frame

# Streamlit UI
st.title("Web-Based ROI Selection Tool")

video_path = st.text_input("Enter path to the video file:")

if video_path and os.path.exists(video_path):
    frame = extract_first_frame(video_path)

    if frame is not None:
        st.write("### Draw your ROI on the image below")
        
        # Display image in Streamlit Drawable Canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Transparent fill
            stroke_width=3,
            stroke_color="red",
            background_image=frame,
            update_streamlit=True,
            height=frame.shape[0],
            width=frame.shape[1],
            drawing_mode="polygon",
            key="canvas",
        )

        # Extract ROI points
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data["objects"]
            if objects:
                roi_points = [(int(obj["left"]), int(obj["top"])) for obj in objects]
                st.success(f"Selected ROI Points: {roi_points}")
            else:
                st.warning("No ROI selected. Please draw a polygon.")

else:
    st.warning("Please enter a valid video file path.")
