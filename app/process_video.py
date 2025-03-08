import cv2
import numpy as np
from ultralytics import YOLO
import os

# Define a public directory where processed videos will be saved
OUTPUT_VIDEO_DIR = "processed_videos"

os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)

def process_video_with_roi(video_path, roi_coords, frame_rate):
    """
    Processes the video to detect object crossings at the ROI boundary,
    calculates cycle times, and extracts the longest cycle segment.

    Returns:
        tuple: (output_video_path, timestamps, cycle_times, max_cycle_video_path)
    """
    model = YOLO(r"C:\Users\Ruchir\project_directory\cycle_time.v5i.yolov8\runs\detect\train4\weights\best.pt").to("cpu")

    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found.")
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_fps = cap.get(cv2.CAP_PROP_FPS)  # Get the actual FPS of the video

    # Save output videos
    output_video_path = os.path.join(OUTPUT_VIDEO_DIR, "processed_video.mp4")
    max_cycle_video_path = os.path.join(OUTPUT_VIDEO_DIR, "max_cycle_clip.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, original_fps, (width, height))

    timestamps = []
    cycle_times = []
    object_inside_roi = False
    last_entry_time = None
    max_cycle_time = 0
    max_cycle_clip = None

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
        timestamp = frame_number / original_fps  # Use original FPS for accurate timestamps
        results = model(frame)

        cycle_time = None  

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                inside_roi = cv2.pointPolygonTest(np.array(roi_coords, np.int32), (int(center_x), int(center_y)), False) >= 0

                if inside_roi and not object_inside_roi:
                    object_inside_roi = True
                    timestamps.append(timestamp)

                    if last_entry_time is not None:
                        cycle_time = timestamp - last_entry_time
                        cycle_times.append(cycle_time)

                        if cycle_time > max_cycle_time:
                            max_cycle_time = cycle_time
                            max_cycle_clip = (last_entry_time, timestamp)

                    last_entry_time = timestamp

                elif not inside_roi:
                    object_inside_roi = False  

                cv2.polylines(frame, [np.array(roi_coords, np.int32)], isClosed=True, color=(0, 0, 255), thickness=2)

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                if cycle_time is not None:
                    cv2.putText(frame, f"Cycle Time: {cycle_time:.2f}s", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"Processed video saved at: {output_video_path}")

    # Extract and save the max cycle segment
    if max_cycle_clip:
        start_time, end_time = max_cycle_clip

        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

        out_clip = cv2.VideoWriter(max_cycle_video_path, fourcc, original_fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_MSEC) > end_time * 1000:
                break
            out_clip.write(frame)

        cap.release()
        out_clip.release()

        print(f"Max cycle segment saved at: {max_cycle_video_path}")

    return output_video_path, timestamps, cycle_times, max_cycle_video_path