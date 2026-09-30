import cv2
from config import LOW_MAX, MEDIUM_MAX


def density_label(count):
    if count <= LOW_MAX:
        return "LOW"
    if count <= MEDIUM_MAX:
        return "MEDIUM"
    return "HIGH"


def draw_tracks(frame, tracks):
    for item in tracks:
        x1, y1, x2, y2 = item["bbox"]
        track_id = item["track_id"]
        label = f"Person #{track_id}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 2)
        cv2.putText(
            frame, label, (x1, max(25, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2
        )

    return frame


def draw_dashboard(frame, count, density, fps):
    cv2.rectangle(frame, (10, 10), (330, 120), (20, 20, 20), -1)

    lines = [
        f"People: {count}",
        f"Crowd Density: {density}",
        f"FPS: {fps:.1f}",
    ]

    for i, line in enumerate(lines):
        cv2.putText(
            frame, line, (25, 40 + i * 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2
        )

    return frame
