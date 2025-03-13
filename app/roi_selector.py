import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import cv2
import numpy as np
from PIL import Image

def extract_first_frame(video_path):
    """Extract the first frame from the video and return a NumPy image array."""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        st.error("Error: Could not open video file.")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        st.error("Error: Could not extract a frame from the video.")
        return None

    # Convert frame to RGB (OpenCV loads as BGR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Debugging: Check if image is valid
    if frame is None:
        st.error("Extracted frame is None. Image conversion failed.")
    else:
        st.write("Extracted frame successfully.")

    return frame  # Return NumPy array instead of PIL Image

def select_roi(video_path):
    """Allows the user to draw a polygon ROI on the first frame of the video."""
    st.title("Select ROI")
    st.write("Draw your ROI on the video frame and save it.")

    # Ensure session state for ROI coordinates
    if "roi_coords" not in st.session_state:
        st.session_state["roi_coords"] = []

    # Extract the first frame
    frame_image = extract_first_frame(video_path)

    # Debugging: Check if image is valid before passing to st_canvas
    if frame_image is None:
        st.error("Failed to load video frame. Cannot proceed.")
        return  # Exit function if no valid image

    # Convert NumPy array to PIL Image for display in Streamlit
    pil_image = Image.fromarray(frame_image)

    # Display the extracted frame
    st.image(pil_image, caption="Extracted Frame for ROI", use_container_width=True)

    # Draw ROI using `st_canvas()`
    try:
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Transparent fill color
            stroke_width=2,
            stroke_color="#FF0000",
            background_image=frame_image,  # Use NumPy image instead of PIL
            height=frame_image.shape[0],  # Image height
            width=frame_image.shape[1],   # Image width
            drawing_mode="polygon",
            key="canvas",
        )
    except AttributeError as e:
        st.error(f"Error in st_canvas: {e}")
        return

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

def save_roi_coordinates(roi_coords):
    """Saves ROI coordinates to a JSON file."""
    roi_file = "roi_coordinates.json"
    with open(roi_file, "w") as f:
        json.dump(roi_coords, f)


