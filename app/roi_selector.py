import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import os
import cv2
import numpy as np
from PIL import Image

def extract_first_frame(video_path):
    """Extract the first frame from the video and return it as an image."""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    return None

def select_roi(temp_video_path):
    st.title("Select ROI")

    if "roi_coords" not in st.session_state:
        st.session_state["roi_coords"] = []

    st.write("Draw your ROI on the video frame and save it.")
    
    frame = extract_first_frame(temp_video_path)
    if frame is not None:
        st.image(frame, caption="Extracted Frame for ROI", use_container_width=True)
    else:
        st.error("Could not extract a frame from the video.")

    pil_image = Image.fromarray(frame) if frame is not None else None

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  
        stroke_width=2,
        stroke_color="#FF0000",
        background_image=pil_image,
        height=400,
        width=600,
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.button("Save ROI"):
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get("objects", [])
            roi_coords = [obj["path"] for obj in objects if obj["type"] == "path"]
            
            if roi_coords:
                st.session_state["roi_coords"] = roi_coords
                save_roi_coordinates(roi_coords)
                st.success("ROI coordinates saved successfully!")
            else:
                st.error("Please draw a valid ROI before saving.")

def save_roi_coordinates(roi_coords):
    roi_file = "roi_coordinates.json"
    with open(roi_file, "w") as f:
        json.dump(roi_coords, f)

