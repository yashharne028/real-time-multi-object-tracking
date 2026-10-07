import argparse
import time
import sys
import cv2

from tracker import MultiObjectTracker
from utils import density_label, draw_tracks, draw_dashboard
from config import MODEL_NAME, CONFIDENCE_THRESHOLD


def run(source, model_name=MODEL_NAME, conf_thresh=CONFIDENCE_THRESHOLD, skip_frames=5):
    print(f"[INFO] Initializing Real-Time Multi-Object Tracking Engine...")
    print(f"[INFO] Source: {source} | Model: {model_name} | Confidence: {conf_thresh}")

    is_webcam = isinstance(source, int) or (isinstance(source, str) and source.isdigit())
    if is_webcam:
        cap = cv2.VideoCapture(int(source), cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Could not open video source: {source}")
        print(f"[HINT] Check camera permissions or verify the video file path.")
        return

    # Set Camera resolution & buffer size if webcam
    if is_webcam:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    tracker = MultiObjectTracker(model_name=model_name, conf_threshold=conf_thresh)

    last_tracks = []
    frame_count = 0

    fps_time = time.time()
    fps = 0.0

    print("[INFO] Engine Online. Press 'q' in the OpenCV window to exit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if is_webcam:
            frame = cv2.flip(frame, 1)

        frame_count += 1

        # AI processing on scheduled interval
        if frame_count % skip_frames == 0:
            last_tracks = tracker.process_frame(
                frame,
                persons_only=True,
                conf_threshold=conf_thresh
            )

        # Draw the latest AI results on EVERY camera frame
        count = len(last_tracks)
        density = density_label(count)

        # Calculate display FPS
        now = time.time()
        if now - fps_time >= 1.0:
            fps = frame_count / (now - fps_time)
            frame_count = 0
            fps_time = now

        frame = draw_tracks(frame, last_tracks, show_trajectories=True)
        frame = draw_dashboard(
            frame,
            count,
            density,
            fps
        )

        cv2.imshow(
            "AI Crowd Monitor - Real-Time Multi-Object Tracking",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Tracking session terminated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-Time Multi-Object Tracking CLI Runner")

    parser.add_argument(
        "--source",
        default="0",
        help="0 for laptop webcam, 1 for external camera, or path to a video file"
    )
    parser.add_argument(
        "--model",
        default=MODEL_NAME,
        help="YOLO model checkpoint name or path (e.g. yolov9c.pt, yolov8n.pt)"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help="Confidence threshold for person detections"
    )
    parser.add_argument(
        "--skip",
        type=int,
        default=5,
        help="Process AI detection every N frames for performance"
    )

    args = parser.parse_args()

    source = (
        int(args.source)
        if args.source.isdigit()
        else args.source
    )

    run(source, model_name=args.model, conf_thresh=args.conf, skip_frames=args.skip)