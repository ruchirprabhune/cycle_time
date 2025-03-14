import streamlit as st
import os
import cv2
import time
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from process_video import process_video_with_roi
from streamlit_drawable_canvas import st_canvas
import login

# Display login page if not logged in
if not st.session_state.get("logged_in", False):
    login.login_page()
    st.stop()

st.title(f"Welcome, {st.session_state['username']}!")
st.write("This is your secured dashboard.")

load_dotenv()

VIDEO_SERVER_URL = "http://127.0.0.1:9000"

# Initialize session states
session_states = [
    "roi_coords", "selected_cycle", "df",
    "output_video_path", "uploaded_video_path", "temp_video_path"
]
for state in session_states:
    if state not in st.session_state:
        st.session_state[state] = None

st.title("AI Cycle Time Analysis")

# Option for live stream input
live_stream_option = st.checkbox("Enable Live Stream Input (Record from Webcam)")

if live_stream_option:
    if st.button("Start Live Stream Recording (10 seconds)"):
        st.write("Recording live stream for 10 seconds...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Error: Could not open webcam.")
        else:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            live_video_path = os.path.join("processed_videos", "live_stream.mp4")
            out = cv2.VideoWriter(live_video_path, fourcc, 20.0, (640, 480))
            start_time = time.time()
            frame_placeholder = st.empty()
            while time.time() - start_time < 10:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                frame_placeholder.image(frame, channels="BGR")
            cap.release()
            out.release()
            st.success("Live stream captured!")
            st.session_state["uploaded_video_path"] = "live_stream.mp4"
            st.session_state["temp_video_path"] = live_video_path

if not live_stream_option:
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
    if uploaded_file:
        file_path = os.path.join("processed_videos", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["uploaded_video_path"] = uploaded_file.name
        st.session_state["temp_video_path"] = file_path

if st.session_state["temp_video_path"]:
    frame_rate = st.slider("Select frame rate (FPS)", min_value=1, max_value=30, value=10, step=1)

    def extract_first_frame(video_path):
        if not os.path.exists(video_path):
            st.error(f"Error: Video file not found at {video_path}")
            return None

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("Error: Could not open video file.")
            return None

        ret, frame = cap.read()
        cap.release()

        if not ret:
            st.error("Error: Could not read the first frame.")
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)

    frame = extract_first_frame(st.session_state["temp_video_path"])

    if frame is None:
        st.stop()

    st.write("### Draw Region of Interest (ROI) on the frame below")

    from streamlit.components.v1 import image_to_url  # Required for conversion

    # Convert PIL image to URL for st_canvas
    frame_url = st.image(frame, use_column_width=True).image_to_url(frame)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  
        stroke_width=3,
        stroke_color="red",
        background_image=frame_url,  
        update_streamlit=True,
        height=frame.height,
        width=frame.width,
        drawing_mode="polygon",
        key="canvas",
    )

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if objects:
            roi_coords = [(int(obj["left"]), int(obj["top"])) for obj in objects]
            st.session_state["roi_coords"] = roi_coords
            st.success(f"ROI Selected: {st.session_state['roi_coords']}")
        else:
            st.warning("No ROI selected. Please draw a polygon.")

    if st.session_state.get("roi_coords") and st.button("Start Processing"):
        st.write("Processing video... Please wait.")
        temp_video_path = st.session_state["temp_video_path"]
        result = process_video_with_roi(temp_video_path, st.session_state["roi_coords"], frame_rate)

        if result is None:
            st.error("Error: Failed to process the video.")
        else:
            output_video_path, timestamps, cycle_times, max_cycle_video_path = result
            st.session_state["output_video_path"] = os.path.basename(output_video_path)
            st.success("Processing complete!")
