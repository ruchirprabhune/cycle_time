import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import cv2
import numpy as np
from PIL import Image
import io
import base64

def extract_first_frame(video_path):
    """Extract the first frame from the video and return it as a Base64 encoded string."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error: Could not open video file.")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format
        pil_image = Image.fromarray(frame)  # Convert to PIL Image
        return encode_image_to_base64(pil_image)  # Convert to Base64
    else:
        st.error("Error: Could not extract frame from video.")
        return None

def encode_image_to_base64(image):
    """Convert PIL Image to a Base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def select_roi(video_path):
    """Allows the user to draw a polygon ROI on the first frame of the video."""
    st.title("Select ROI")
    st.write("Draw your ROI on the video frame and save it.")

    if "roi_coords" not in st.session_state:
        st.session_state["roi_coords"] = []

    # Extract the first frame and convert to Base64
    frame_base64 = extract_first_frame(video_path)
    if frame_base64:
        image_url = f"data:image/png;base64,{frame_base64}"
        st.image(image_url, caption="Extracted Frame for ROI", use_container_width=True)

        # Canvas for ROI selection
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Transparent fill color
            stroke_width=2,
            stroke_color="#FF0000",
            background_image=image_url,  # Pass Base64 string instead of PIL image
            height=500,  # Set fixed height
            width=800,   # Set fixed width
            drawing_mode="polygon",
            key="canvas",
        )

        # Save ROI Button
        if st.button("Save ROI"):
            if canvas_result.json_data is not None:
                objects = canvas_result.json_data.get("objects", [])
                roi_coords = []

                for obj in objects:
                    if obj["type"] == "polygon":
                        roi_coords.append(obj["path"])  # Extract ROI coordinates

                if roi_coords:
                    st.session_state["roi_coords"] = roi_coords
                    save_roi_coordinates(roi_coords)
                    st.success("ROI coordinates saved successfully!")
                else:
                    st.warning("No ROI detected. Please draw a valid region before saving.")
    else:
        st.error("Could not process video. Ensure the file is accessible and in a valid format.")

def save_roi_coordinates(roi_coords):
    """Saves ROI coordinates to a JSON file."""
    roi_file = "roi_coordinates.json"
    with open(roi_file, "w") as f:
        json.dump(roi_coords, f)

