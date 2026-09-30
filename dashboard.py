import tempfile
from pathlib import Path
import cv2
import streamlit as st

from tracker import MultiObjectTracker
from utils import density_label, draw_tracks, draw_dashboard

st.set_page_config(
    page_title="CrowdTrack AI",
    page_icon="👥",
    layout="wide"
)

st.title("👥 CrowdTrack AI")
st.caption("Real-Time Multi-Object Tracking & Crowd Density Estimation")

uploaded = st.file_uploader(
    "Upload a video",
    type=["mp4", "avi", "mov", "mkv"]
)

confidence = st.slider("Detection confidence", 0.10, 0.90, 0.35, 0.05)

if uploaded:
    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        video_path = tmp.name

    tracker = MultiObjectTracker()
    tracker.model.overrides["conf"] = confidence

    cap = cv2.VideoCapture(video_path)
    output = st.empty()

    total_frames = 0
    total_people = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        tracks = tracker.process_frame(frame, persons_only=True)
        count = len(tracks)
        density = density_label(count)

        total_frames += 1
        total_people += count

        frame = draw_tracks(frame, tracks)
        frame = draw_dashboard(frame, count, density, 0.0)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output.image(frame, channels="RGB", use_container_width=True)

    cap.release()

    st.success("Video processing completed.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Frames Processed", total_frames)
    c2.metric("Average People / Frame", round(total_people / max(total_frames, 1), 2))
    c3.metric("Final Density", density)
else:
    st.info("Upload a video to start the tracking demonstration.")
