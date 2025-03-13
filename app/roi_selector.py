import tempfile  # Add this import

def select_roi(video_path):
    """ Allows user to select a polygonal ROI by clicking on a frame using an interactive canvas. """

    if not os.path.exists(video_path):
        st.error(f"Error: Video file not found at {video_path}")
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error: Could not open video file.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        st.error("Error: Could not read the first frame of the video. Ensure the file is not corrupted.")
        return None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)

    # Save image as a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        img.save(temp_file.name)
        temp_img_path = temp_file.name  # Get file path

    st.write("### Click exactly four points to define a polygonal ROI.")

    # Load the saved image in st_canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        stroke_color="red",
        background_image=temp_img_path,  # ✅ Now a valid file path
        height=frame.shape[0],
        width=frame.shape[1],
        drawing_mode="point",
        key="canvas",
    )

    if canvas_result.json_data:
        objects = canvas_result.json_data["objects"]
        roi_points = [(int(obj["left"]), int(obj["top"])) for obj in objects]

        if len(roi_points) == 4:
            st.success(f"ROI Selected: {roi_points}")
            return roi_points
        elif len(roi_points) > 4:
            st.error("Please select exactly 4 points.")

    return None


