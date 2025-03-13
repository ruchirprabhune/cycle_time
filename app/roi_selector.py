import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import os

def select_roi(temp_video_path):
    st.title("Select ROI")
    
    if "roi_coords" not in st.session_state:
        st.session_state["roi_coords"] = []
    
    st.write("Draw your ROI on the canvas and save it.")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Transparent fill
        stroke_width=2,
        stroke_color="#FF0000",
        background_color="#FFFFFF",
        height=400,
        width=600,
        drawing_mode="polygon",
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

def load_roi_coordinates():
    roi_file = "roi_coordinates.json"
    if os.path.exists(roi_file):
        with open(roi_file, "r") as f:
            return json.load(f)
    return []

if __name__ == "__main__":
    if "temp_video_path" not in st.session_state:
        st.session_state["temp_video_path"] = None
    select_roi(st.session_state["temp_video_path"])
