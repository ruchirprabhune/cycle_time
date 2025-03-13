import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
import json

def load_video_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        st.error("Failed to load video frame.")
        return None
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def save_roi_coordinates(coordinates, file_path="roi_coordinates.json"):
    with open(file_path, "w") as f:
        json.dump(coordinates, f)

def main():
    st.title("Select ROI")
    video_path = st.text_input("Enter video file path:")
    
    if video_path:
        frame = load_video_frame(video_path)
        if frame is not None:
            st.image(frame, caption="Original Frame", use_column_width=True)
            
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.5)",
                stroke_width=3,
                stroke_color="#FF0000",
                background_image=frame,
                update_streamlit=True,
                drawing_mode="polygon",
                key="canvas",
            )
            
            if st.button("Save ROI"):
                if canvas_result.json_data:
                    objects = canvas_result.json_data["objects"]
                    if objects:
                        polygon_coords = [obj["path"] for obj in objects if obj["type"] == "path"]
                        save_roi_coordinates(polygon_coords)
                        st.success("ROI coordinates saved successfully.")
                    else:
                        st.warning("No ROI selected.")

if __name__ == "__main__":
    main()


