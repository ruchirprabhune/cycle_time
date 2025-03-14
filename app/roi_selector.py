import cv2
import numpy as np
import streamlit as st
from PIL import Image

def select_roi(video_path):
    """ Allows the user to click on four points in Streamlit to define a polygonal ROI """

    # Extract the first frame of the video
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        st.error("Failed to extract frame from video.")
        return None

    # Convert the OpenCV image (BGR) to RGB for Streamlit
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)

    # Display the extracted frame in Streamlit
    st.write("### Click exactly four points to define the ROI.")
    st.image(img, use_column_width=True)

    # Initialize or reset selection
    if "roi_points" not in st.session_state:
        st.session_state.roi_points = []

    # Collect user clicks
    clicked_point = st.text_input("Enter ROI points (e.g., '100,200') and press Enter:")

    if clicked_point:
        try:
            x, y = map(int, clicked_point.split(","))
            if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                st.session_state.roi_points.append((x, y))
                st.success(f"Point {len(st.session_state.roi_points)} added: ({x}, {y})")
            else:
                st.error("Point out of bounds. Try again.")
        except ValueError:
            st.error("Invalid format. Enter coordinates as 'x,y'.")

    # Display the selected points
    if st.session_state.roi_points:
        st.write(f"Selected Points: {st.session_state.roi_points}")

    # Check if exactly 4 points were selected
    if len(st.session_state.roi_points) == 4:
        st.success("ROI selection complete.")
        return st.session_state.roi_points

    return None




