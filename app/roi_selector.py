import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import os
import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO

def extract_first_frame(video_path):
    """Extract the first frame from the video and return it as an image."""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    return None

def image_to_url(image):
    """Convert an image to a base64 URL for Streamlit Canvas."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def select_roi(temp_video_path):
    st.title("Select ROI")

    if "roi_coords" not in st.session_state:
        st.session_state["roi_coords"] = []

    st.write("Draw your ROI on the video frame and save it.")
    
    frame = extract_first_frame(temp_video_path)
    if frame is not None:
        pil_image = Image.fromarray(frame)
        image_url = image_to_url(pil_image)
        st.image(frame, caption="Extracted Frame for ROI", use_container_width=True)
    else:
        st.error("Could not extract a frame from the video.")
        return

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  
        stroke_width=2,
        stroke_color="#FF0000",
        background_image_url=image_url,
        height=400,
        width=600,
        drawing_mode="polygon",
        key="canvas",
    )

    if st.button("Save ROI") and canvas_result.json_data:
        objects = canvas_result.json_data.get("objects", [])
        roi_coords = [obj["path"] for obj in objects if obj["type"] == "path"]

        if roi_coords:
            st.session_state["roi_coords"] = roi_coords
            save_roi_coordinates(roi_coords)
            st.success("ROI coordinates saved successfully!")
        else:
            st.error("Please draw a valid ROI before saving.")

def save_roi_coordinates(roi_coords):
    """Save ROI coordinates to a JSON file."""
    with open("roi_coordinates.json", "w") as f:
        json.dump(roi_coords, f)

if __name__ == "__main__":
    if "temp_video_path" not in st.session_state:
        st.session_state["temp_video_path"] = None
    select_roi(st.session_state["temp_video_path"])

