import cv2
import numpy as np
from ultralytics import YOLO
import os

# Define the output directory for processed videos
OUTPUT_VIDEO_DIR = "processed_videos"
os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)

def process_video_with_rois(video_path, roi1_coords, roi2_coords, frame_rate):
    """
    Processes the video to detect object crossings at two ROIs:
    - Full cycle ROI
    - Half cycle ROI

    Returns:
        tuple: (output_video_path, timestamps_full, cycle_times_full, timestamps_half, cycle_times_half, max_full_cycle_video_path, max_half_cycle_video_path)
    """

    # Load YOLO model
    model = YOLO(r"C:\Users\Ruchir\project_directory\cycle_time.v5i.yolov8\runs\detect\train4\weights\best.pt").to("cpu")

    # Check if the video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found.")
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return None

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_fps = cap.get(cv2.CAP_PROP_FPS)  # Actual FPS of the video

    # Define output video paths
    output_video_path = os.path.join(OUTPUT_VIDEO_DIR, "processed_video.mp4")
    max_full_cycle_video_path = os.path.join(OUTPUT_VIDEO_DIR, "max_full_cycle_clip.mp4")
    max_half_cycle_video_path = os.path.join(OUTPUT_VIDEO_DIR, "max_half_cycle_clip.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, original_fps, (width, height))

    # Tracking cycle data
    timestamps_full = []
    cycle_times_full = []
    object_inside_roi1 = False
    last_entry_time_full = None
    max_full_cycle_time = 0
    max_full_cycle_clip = None

    timestamps_half = []
    cycle_times_half = []
    object_inside_roi2 = False
    last_entry_time_half = None
    max_half_cycle_time = 0
    max_half_cycle_clip = None

    frame_interval = int(original_fps / frame_rate)  # Frame skip interval

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_interval != 0:
            continue  # Skip frames based on user selection

        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        timestamp = frame_number / original_fps  # Accurate timestamp calculation

        results = model(frame)

        # Process detected objects
        for result in results:
            for box in result.boxes:
                if box.xyxy is None:
                    continue  # Skip if no bounding box

                x1, y1, x2, y2 = box.xyxy[0]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                inside_roi1 = cv2.pointPolygonTest(np.array(roi1_coords, np.int32), (int(center_x), int(center_y)), False) >= 0
                inside_roi2 = cv2.pointPolygonTest(np.array(roi2_coords, np.int32), (int(center_x), int(center_y)), False) >= 0

                # Full Cycle ROI processing
                if inside_roi1 and not object_inside_roi1:
                    object_inside_roi1 = True
                    timestamps_full.append(timestamp)

                    if last_entry_time_full is not None:
                        cycle_time_full = timestamp - last_entry_time_full
                        cycle_times_full.append(cycle_time_full)

                        if cycle_time_full > max_full_cycle_time:
                            max_full_cycle_time = cycle_time_full
                            max_full_cycle_clip = (last_entry_time_full, timestamp)

                    last_entry_time_full = timestamp

                elif not inside_roi1:
                    object_inside_roi1 = False

                # Half Cycle ROI processing
                if inside_roi2 and not object_inside_roi2:
                    object_inside_roi2 = True
                    timestamps_half.append(timestamp)

                    if last_entry_time_half is not None:
                        cycle_time_half = timestamp - last_entry_time_half
                        cycle_times_half.append(cycle_time_half)

                        if cycle_time_half > max_half_cycle_time:
                            max_half_cycle_time = cycle_time_half
                            max_half_cycle_clip = (last_entry_time_half, timestamp)

                    last_entry_time_half = timestamp

                elif not inside_roi2:
                    object_inside_roi2 = False

                # Draw the ROIs and bounding boxes
                cv2.polylines(frame, [np.array(roi1_coords, np.int32)], isClosed=True, color=(0, 0, 255), thickness=2)  # Full cycle ROI in Red
                cv2.polylines(frame, [np.array(roi2_coords, np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)  # Half cycle ROI in Blue
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"Processed video saved at: {output_video_path}")

    # Extract max full cycle segment
    if max_full_cycle_clip:
        start_time, end_time = max_full_cycle_clip
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        out_clip = cv2.VideoWriter(max_full_cycle_video_path, fourcc, original_fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_MSEC) > end_time * 1000:
                break
            out_clip.write(frame)

        cap.release()
        out_clip.release()
        print(f"Max full cycle segment saved at: {max_full_cycle_video_path}")

    # Extract max half cycle segment
    if max_half_cycle_clip:
        start_time, end_time = max_half_cycle_clip
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        out_clip = cv2.VideoWriter(max_half_cycle_video_path, fourcc, original_fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_MSEC) > end_time * 1000:
                break
            out_clip.write(frame)

        cap.release()
        out_clip.release()
        print(f"Max half cycle segment saved at: {max_half_cycle_video_path}")

    return (
        output_video_path, 
        timestamps_full, cycle_times_full, 
        timestamps_half, cycle_times_half, 
        max_full_cycle_video_path, max_half_cycle_video_path
    )
