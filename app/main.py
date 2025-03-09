import streamlit as st
import os
import multiprocessing
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import openai
from tkinter_gui import run_tkinter
from process_video import process_video_with_roi
from dotenv import load_dotenv
import cv2
import time
import streamlit as st
import login

# Display login page if not logged in
if not st.session_state.get("logged_in", False):
    login.login_page()
    st.stop()  # Stop execution so login page is shown

# Now the main app is accessible only after login
st.title(f"Welcome, {st.session_state['username']}!")

st.write("This is your secured dashboard.")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
            st.session_state["temp_video_path"] = live_video_path  # Save path for processing

if not live_stream_option:
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
    if uploaded_file:
        file_path = os.path.join("processed_videos", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["uploaded_video_path"] = uploaded_file.name
        st.session_state["temp_video_path"] = file_path  # Save path for processing

# Proceed if we have a video file path available
if st.session_state["temp_video_path"]:
    frame_rate = st.slider("Select frame rate (FPS)", min_value=1, max_value=30, value=10, step=1)

    if st.button("Select Region of Interest"):
        result_queue = multiprocessing.Queue()
        # Use the stored temp_video_path
        temp_video_path = st.session_state["temp_video_path"]
        process = multiprocessing.Process(target=run_tkinter, args=(temp_video_path, result_queue))
        process.start()
        process.join()

        if not result_queue.empty():
            st.session_state["roi_coords"] = result_queue.get()
            st.success(f"ROI Selected: {st.session_state['roi_coords']}")
        else:
            st.warning("No ROI was selected.")

    if st.session_state["roi_coords"] and st.button("Start Processing"):
        st.write("Processing video... Please wait.")
        temp_video_path = st.session_state["temp_video_path"]
        result = process_video_with_roi(temp_video_path, st.session_state["roi_coords"], frame_rate)
        if result is None:
            st.error("Error: Failed to process the video.")
        else:
            output_video_path, timestamps, cycle_times, max_cycle_video_path = result
            st.session_state["output_video_path"] = os.path.basename(output_video_path)
            st.success("Processing complete!")

            if cycle_times:
                df = pd.DataFrame({
                    "Cycle No.": range(1, len(cycle_times) + 1),
                    "Start Time (s)": timestamps[:-1],
                    "End Time (s)": timestamps[1:] if len(timestamps) > 1 else timestamps,
                    "Cycle Time (s)": cycle_times
                })
                st.session_state["df"] = df
                st.write("### Cycle Time Table")
                df["Video Link"] = df.apply(
                    lambda row: f'<a href="{VIDEO_SERVER_URL}/{st.session_state["uploaded_video_path"]}?start={int(row["Start Time (s)"])}&end={int(row["End Time (s)"])}" target="_blank">▶️ Play Cycle {row["Cycle No."]}</a>',
                    axis=1
                )
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

                st.plotly_chart(
                    px.bar(
                        df, 
                        x="Cycle No.", 
                        y="Cycle Time (s)", 
                        title="Cycle Time Analysis",
                        labels={"Cycle No.": "Cycle Number", "Cycle Time (s)": "Cycle Duration (s)"},
                        text_auto=True
                    ).update_traces(marker_color='blue', textposition='outside')
                )

                st.write("### Maximum Cycle Analysis")
                max_cycle_time = df["Cycle Time (s)"].max()
                max_cycles = df[df["Cycle Time (s)"] == max_cycle_time]
                st.write(f"The maximum cycle time is *{max_cycle_time:.2f} seconds*.")
                for _, row in max_cycles.iterrows():
                    st.write(f"*Cycle {row['Cycle No.']}* ran from *{row['Start Time (s)']}s* to *{row['End Time (s)']}s* with a duration of *{row['Cycle Time (s)']:.2f} seconds*.")
                    clip_link = f'<a href="{VIDEO_SERVER_URL}/{st.session_state["uploaded_video_path"]}?start={int(row["Start Time (s)"])}&end={int(row["End Time (s)"])}" target="_blank">▶️ Play Maximum Cycle {row["Cycle No."]}</a>'
                    st.markdown(clip_link, unsafe_allow_html=True)

