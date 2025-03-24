import streamlit as st
import os
import multiprocessing
import pandas as pd
import plotly.express as px
from tkinter_gui import run_tkinter
from process_video import process_video_with_rois
from dotenv import load_dotenv
import cv2
import login
import threading

from supabase import create_client, Client

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define directories
OUTPUT_DIR = "processed_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Video Server URL
VIDEO_SERVER_URL = "http://127.0.0.1:9000"

# Display login page if not logged in
if not st.session_state.get("logged_in", False):
    login.login_page()
    st.stop()

st.title(f"Welcome, {st.session_state['username']}!")
st.write("This is your secured dashboard.")

# Initialize session state variables
for state in ["roi1_coords", "roi2_coords", "df", "sub_df", "output_video_path", 
              "uploaded_video_path", "temp_video_path", "full_cycle_df", "half_cycle_df",
              "max_full_cycle_video_path", "max_half_cycle_video_path"]:
    if state not in st.session_state:
        st.session_state[state] = None

st.title("AI Cycle Time Analysis")

def record_webcam():
    """Records video from the webcam for 20 seconds and saves it as an MP4 file."""
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec
    video_path = os.path.join(OUTPUT_DIR, "webcam_recording.mp4")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

    st.session_state["recording"] = True  # Set recording status
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or not st.session_state["recording"]:
            break

        # Flip frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)
        out.write(frame)

        # Display the webcam feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, channels="RGB", use_column_width=True)

        # Stop recording after 20 seconds
        if time.time() - start_time >= 20:
            break

    cap.release()
    out.release()
    st.session_state["recording"] = False
    st.session_state["uploaded_video_path"] = "webcam_recording.mp4"
    st.session_state["temp_video_path"] = video_path
    st.success("Webcam recording saved!")

# Webcam Controls
st.write("### 🎥 Live Webcam Recording")
if st.button("Start Recording"):
    st.session_state["recording"] = True
    threading.Thread(target=record_webcam, daemon=True).start()

# Function to store cycle data in Supabase
def store_cycle_data_in_supabase(df):
    """Inserts processed cycle data into the Supabase database."""
    if df is not None and not df.empty:
        # Rename DataFrame columns to match Supabase table schema
        df = df.rename(columns={
            "Cycle No.": "cycle_no",
            "Start Time (s)": "start_time",
            "End Time (s)": "end_time",
            "Cycle Time (s)": "cycle_time",
            "Video Link": "video_link"
        })
        
        # Add username column (from session state)
        df["username"] = st.session_state["username"]

        # Convert DataFrame to list of dictionaries
        data = df.to_dict(orient="records")  

        try:
            response = supabase.table("cycle_analysis").insert(data).execute()
            if "error" in response:
                st.error(f"Error storing data in Supabase: {response['error']}")
            else:
                st.success("Cycle data successfully stored in Supabase!")
        except Exception as e:
            st.error(f"Error storing data in Supabase: {e}")


# Upload Video
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
if uploaded_file:
    file_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state["uploaded_video_path"] = uploaded_file.name
    st.session_state["temp_video_path"] = file_path

# Proceed if a video file exists
if "temp_video_path" not in st.session_state:
    st.session_state["temp_video_path"] = None

if st.session_state["temp_video_path"]:
    st.markdown(
        """
        <style>
            .fps-slider .stSlider > div[data-baseweb="slider"] > div {
                background: linear-gradient(
                    to right, 
                    red 0%, red 17%, 
                    yellow 17%, yellow 50%, 
                    green 50%, green 100%
                );
                border-radius: 8px;
                height: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    frame_rate = st.slider("Select frame rate (FPS)", min_value=1, max_value=30, value=10, step=1, key="fps_slider")

    # Display selected FPS color category
    if frame_rate <= 5:
        st.markdown("**🟥 Low FPS (1-5) Lower Accuracy - Red**")
    elif frame_rate <= 15:
        st.markdown("**🟨 Medium FPS (6-15) - Yellow**")
    else:
        st.markdown("**🟩 High FPS (16-30) Higher Accuracy - Green**")

    if st.button("Select Region of Interest"):
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=run_tkinter, args=(st.session_state["temp_video_path"], result_queue))
        process.start()
        process.join()

        if not result_queue.empty():
            roi_selection = result_queue.get()
            if len(roi_selection) == 2:
                st.session_state["roi1_coords"], st.session_state["roi2_coords"] = roi_selection
                st.success(f"ROIs Selected: ROI1: {st.session_state['roi1_coords']}, ROI2: {st.session_state['roi2_coords']}")
            else:
                st.warning("Incorrect ROI selection format.")
        else:
            st.warning("No ROI was selected.")

    if st.session_state["roi1_coords"] and st.session_state["roi2_coords"] and st.button("Start Processing"):
        st.write("Processing video... Please wait.")

        # Run the video processing function
        result = process_video_with_rois(
            st.session_state["temp_video_path"],
            st.session_state["roi1_coords"],
            st.session_state["roi2_coords"],
            frame_rate
        )

        # Unpacking the correct 7 values
        if len(result) == 7:
            (output_video_path, timestamps_full, cycle_times_full, 
             timestamps_half, cycle_times_half, 
             max_full_cycle_video_path, max_half_cycle_video_path) = result
        else:
            st.error(f"Error: Unexpected number of values ({len(result)}) returned from process_video_with_rois.")
            st.stop()

        st.session_state["output_video_path"] = os.path.basename(output_video_path)
        st.session_state["max_full_cycle_video_path"] = os.path.basename(max_full_cycle_video_path)
        st.session_state["max_half_cycle_video_path"] = os.path.basename(max_half_cycle_video_path)
        st.success("Processing complete!")

        # Full Cycle Data
        if cycle_times_full:
            df = pd.DataFrame({
                "Cycle No.": range(1, len(cycle_times_full) + 1),
                "Start Time (s)": timestamps_full[:-1] if len(timestamps_full) > 1 else timestamps_full,
                "End Time (s)": timestamps_full[1:] if len(timestamps_full) > 1 else timestamps_full,
                "Cycle Time (s)": cycle_times_full,
            })
            st.session_state["df"] = df

            # Display Cycle Time Table
            st.write("### Cycle Time Table")
            df["Video Link"] = df.apply(
                lambda row: f'<a href="{VIDEO_SERVER_URL}/{st.session_state["uploaded_video_path"]}?start={int(row["Start Time (s)"])}&end={int(row["End Time (s)"])}" target="_blank">▶️ Play Cycle {row["Cycle No."]}</a>',
                axis=1
            )
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # Cycle Time Analysis Bar Graph
            st.write("### Cycle Time Analysis")
            fig = px.bar(df, x="Cycle No.", y="Cycle Time (s)", title="Cycle Time Analysis",
                        labels={"Cycle No.": "Cycle Number", "Cycle Time (s)": "Cycle Duration (s)"},
                        text_auto=True)
            fig.update_traces(marker_color='blue', textposition='outside')
            st.plotly_chart(fig)
             # Display link to longest cycle
            max_cycle_index = df["Cycle Time (s)"].idxmax()
            max_cycle_video_link = df.loc[max_cycle_index, "Video Link"]
            st.write("### 🚀 Longest Cycle")
            st.write(f"The longest cycle was Cycle {max_cycle_index + 1}, lasting {df.loc[max_cycle_index, 'Cycle Time (s)']:.2f} seconds.")
            st.markdown(max_cycle_video_link, unsafe_allow_html=True)


            
            # Store the full cycle data in Supabase
            store_cycle_data_in_supabase(st.session_state["full_cycle_df"])

        # Half Cycle Data
        if cycle_times_half:
            
            df = pd.DataFrame({
                "Cycle No.": range(1, len(cycle_times_half) + 1),
                "Start Time (s)": timestamps_half[:-1] if len(timestamps_half) > 1 else timestamps_half,
                "End Time (s)": timestamps_half[1:] if len(timestamps_half) > 1 else timestamps_half,
                "Cycle Time (s)": cycle_times_half,
            })
            st.session_state["df"] = df

            # Display Cycle Time Table
            st.write("### Cycle Time Table")
            df["Video Link"] = df.apply(
                lambda row: f'<a href="{VIDEO_SERVER_URL}/{st.session_state["uploaded_video_path"]}?start={int(row["Start Time (s)"])}&end={int(row["End Time (s)"])}" target="_blank">▶️ Play Cycle {row["Cycle No."]}</a>',
                axis=1
            )
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

            st.write("### Cycle Time Analysis")
            fig = px.bar(df, x="Cycle No.", y="Cycle Time (s)", title="Cycle Time Analysis",
                        labels={"Cycle No.": "Cycle Number", "Cycle Time (s)": "Cycle Duration (s)"},
                        text_auto=True)
            fig.update_traces(marker_color='green', textposition='outside')
            st.plotly_chart(fig)

            


# Display Full Cycle Time Table
if st.session_state.get("full_cycle_df") is not None and not st.session_state["full_cycle_df"].empty:
    st.write("### Full Cycle Time Table")
    st.dataframe(st.session_state["full_cycle_df"], use_container_width=True)

    # Full Cycle Time Graph
    full_cycle_fig = px.bar(st.session_state["full_cycle_df"], x="Cycle No.", y="Cycle Time (s)",
                            title="Full Cycle Time Analysis",
                            labels={"Cycle No.": "Cycle Number", "Cycle Time (s)": "Cycle Duration (s)"},
                            text_auto=True)
    full_cycle_fig.update_traces(marker_color='blue', textposition='outside')
    st.plotly_chart(full_cycle_fig)

# Display Half Cycle Time Table
if st.session_state.get("half_cycle_df") is not None and not st.session_state["half_cycle_df"].empty:
    st.write("### Half Cycle Time Table")
    st.dataframe(st.session_state["half_cycle_df"], use_container_width=True)

    # Half Cycle Time Graph
    half_cycle_fig = px.bar(st.session_state["half_cycle_df"], x="Sub-Cycle No.", y="Sub-Cycle Time (s)",
                            title="Half Cycle Time Analysis",
                            labels={"Sub-Cycle No.": "Sub-Cycle Number", "Sub-Cycle Time (s)": "Sub-Cycle Duration (s)"},
                            text_auto=True)
    half_cycle_fig.update_traces(marker_color='green', textposition='outside')
    st.plotly_chart(half_cycle_fig)

