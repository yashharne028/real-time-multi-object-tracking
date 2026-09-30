import argparse
import time
import cv2

from tracker import MultiObjectTracker
from utils import density_label, draw_tracks, draw_dashboard


def run(source):
    cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    # Camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Reduce camera buffering/latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    tracker = MultiObjectTracker()

    last_tracks = []
    frame_count = 0

    fps_time = time.time()
    fps = 0

    while True:
        ok, frame = cap.read()

        if not ok:
            break

        frame_count += 1

        # AI processing only every 5th frame
        if frame_count % 5 == 0:
            last_tracks = tracker.process_frame(
                frame,
                persons_only=True
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

        frame = draw_tracks(frame, last_tracks)
        frame = draw_dashboard(
            frame,
            count,
            density,
            fps
        )

        cv2.imshow(
            "Real-Time Multi-Object Tracking",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        default="0",
        help="0 for laptop camera, 1 for phone camera"
    )

    args = parser.parse_args()

    source = (
        int(args.source)
        if args.source.isdigit()
        else args.source
    )

    run(source)