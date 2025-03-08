from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import subprocess

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Define video directory (all processed videos are stored here)
VIDEO_DIRECTORY = Path("C:/Users/Ruchir/project_directory/processed_videos").resolve()

# Route: No '/videos' prefix so that a request for a file appears as:
# http://127.0.0.1:9000/processed_video.mp4
@app.get("/{video_name}")
async def get_video(video_name: str, start: int = Query(None), end: int = Query(None)):
    """
    Serve full video or extract a segment.
    """
    file_path = (VIDEO_DIRECTORY / video_name).resolve()

    # Prevent directory traversal attack and ensure file exists.
    if not file_path.is_file() or VIDEO_DIRECTORY not in file_path.parents:
        raise HTTPException(status_code=404, detail=f"Video {video_name} not found!")

    # Stream full video if no valid segment parameters are provided.
    if start is None or end is None or start >= end:
        return StreamingResponse(open(file_path, "rb"), media_type="video/mp4")

    # Otherwise, stream the requested video segment.
    return stream_video_segment(file_path, start, end)

def stream_video_segment(file_path: Path, start: int, end: int):
    """
    Extract and stream a video segment using FFmpeg.
    """
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", str(file_path),  # Input file
        "-ss", str(start),       # Start time
        "-to", str(end),         # End time
        "-c:v", "copy", "-c:a", "copy",  # Copy streams without re-encoding
        "-movflags", "frag_keyframe+empty_moov",
        "-f", "mp4", "pipe:1"     # Output to stdout as mp4
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**6)

        def generate():
            while True:
                chunk = process.stdout.read(1024 * 64)
                if not chunk:
                    break
                yield chunk
            process.stdout.close()
            process.wait()

        return StreamingResponse(generate(), media_type="video/mp4")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg error: {str(e)}")

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)