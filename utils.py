import cv2
import numpy as np
from config import LOW_MAX, MEDIUM_MAX

# Enable OpenCV CPU SIMD/multithreading optimizations
cv2.setUseOptimized(True)

# Pre-allocated color constants (BGR)
COLOR_EMERALD = (60, 220, 60)
COLOR_AMBER = (0, 200, 255)
COLOR_RED = (50, 50, 255)
COLOR_CYAN = (255, 170, 0)
COLOR_ALERT = (0, 0, 230)
COLOR_BG_PANEL = (12, 17, 29)

COLOR_PALETTE = [
    (0, 230, 115),   # Neon Green
    (255, 170, 0),   # Cyan
    (0, 190, 255),   # Yellow
    (235, 100, 52),  # Blue
    (255, 105, 180), # Hot Pink
    (138, 43, 226),  # Purple
]
NUM_PALETTE = len(COLOR_PALETTE)


def density_label(count, low_max=LOW_MAX, medium_max=MEDIUM_MAX):
    """Classifies crowd count into LOW, MEDIUM, or HIGH density states."""
    if count <= low_max:
        return "LOW"
    if count <= medium_max:
        return "MEDIUM"
    return "HIGH"


def get_density_color(density):
    """Returns BGR color corresponding to density level."""
    if density == "LOW":
        return COLOR_EMERALD
    elif density == "MEDIUM":
        return COLOR_AMBER
    else:
        return COLOR_RED


def draw_corner_rect(img, pt1, pt2, color, thickness=2, corner_len=12):
    """Draws a surveillance-style bounding box with accentuated corners."""
    x1, y1 = pt1
    x2, y2 = pt2

    # Fast 1px base rectangle
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)

    cl = min(corner_len, (x2 - x1) // 3, (y2 - y1) // 3)
    if cl <= 2:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
        return

    # Corners
    cv2.line(img, (x1, y1), (x1 + cl, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + cl), color, thickness)
    cv2.line(img, (x2, y1), (x2 - cl, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + cl), color, thickness)
    cv2.line(img, (x1, y2), (x1 + cl, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - cl), color, thickness)
    cv2.line(img, (x2, y2), (x2 - cl, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - cl), color, thickness)


def draw_tracks(frame, tracks, show_trajectories=True, show_labels=True):
    """Renders tracking bounding boxes, ID badges, and trajectory trails efficiently."""
    if frame is None or not tracks:
        return frame

    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX

    for item in tracks:
        x1, y1, x2, y2 = item["bbox"]
        track_id = item["track_id"]

        try:
            tid_int = int(track_id)
            color = COLOR_PALETTE[tid_int % NUM_PALETTE]
        except Exception:
            color = COLOR_PALETTE[0]

        # Draw trajectory tail if available
        if show_trajectories and "history" in item:
            pts = item["history"]
            n_pts = len(pts)
            if n_pts > 1:
                for i in range(1, n_pts):
                    cv2.line(frame, pts[i - 1], pts[i], color, 2)

        # Draw bounding box
        draw_corner_rect(frame, (x1, y1), (x2, y2), color, thickness=2, corner_len=14)

        # Draw Centroid
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        cv2.circle(frame, (cx, cy), 3, color, -1)

        # Draw Label Badge
        if show_labels:
            label = f"ID #{track_id}"
            badge_y1 = max(0, y1 - 22)
            badge_y2 = max(20, y1)
            badge_x2 = min(w, x1 + 65)

            # Badge box
            cv2.rectangle(frame, (x1, badge_y1), (badge_x2, badge_y2), (20, 24, 33), -1)
            cv2.rectangle(frame, (x1, badge_y1), (badge_x2, badge_y2), color, 1)

            # Text
            cv2.putText(
                frame, label, (x1 + 4, badge_y2 - 5),
                font, 0.45, (255, 255, 255), 1
            )

    return frame


def draw_dashboard(frame, count, density, fps, alert_active=False):
    """
    Renders telemetry HUD overlay onto frame using fast ROI alpha blending.
    Avoids copying the full frame image buffer.
    """
    if frame is None:
        return frame

    panel_x1, panel_y1 = 15, 15
    panel_w, panel_h = 340, 105
    panel_x2, panel_y2 = panel_x1 + panel_w, panel_y1 + panel_h

    # Fast in-place ROI blend
    roi = frame[panel_y1:panel_y2, panel_x1:panel_x2]
    if roi.shape[0] == panel_h and roi.shape[1] == panel_w:
        dark_rect = np.full((panel_h, panel_w, 3), 16, dtype=np.uint8)
        cv2.addWeighted(dark_rect, 0.82, roi, 0.18, 0, roi)
        frame[panel_y1:panel_y2, panel_x1:panel_x2] = roi

    # Border with density accent
    d_color = get_density_color(density)
    border_color = COLOR_ALERT if alert_active else (50, 60, 80)
    cv2.rectangle(frame, (panel_x1, panel_y1), (panel_x2, panel_y2), border_color, 1)
    cv2.line(frame, (panel_x1, panel_y1), (panel_x2, panel_y1), d_color, 3)

    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Title
    cv2.putText(frame, "AI CROWD MONITOR", (28, 38), font, 0.55, (200, 220, 240), 2)
    
    # Live dot
    dot_color = (0, 60, 240) if alert_active else (0, 230, 115)
    cv2.circle(frame, (330, 33), 5, dot_color, -1)

    # Metrics
    cv2.putText(frame, f"People: {count}", (28, 68), font, 0.65, (255, 255, 255), 2)
    cv2.putText(frame, f"Density: {density}", (180, 68), font, 0.65, d_color, 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (28, 98), font, 0.55, (160, 180, 200), 1)

    if alert_active:
        cv2.putText(frame, "[ALERT ACTIVE]", (180, 98), font, 0.55, (0, 50, 255), 2)

    return frame


def draw_counting_line(frame, line_ratio=0.5, entry_count=0, exit_count=0):
    """Draws a virtual tripwire counting line across the frame."""
    if frame is None:
        return frame

    h, w = frame.shape[:2]
    line_y = int(h * line_ratio)

    # Dashed line
    dash_len = 20
    for x in range(0, w, dash_len * 2):
        cv2.line(frame, (x, line_y), (min(x + dash_len, w), line_y), COLOR_AMBER, 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"TRIPWIRE (Entry: {entry_count} | Exit: {exit_count})", 
                (20, max(25, line_y - 8)), font, 0.5, COLOR_AMBER, 1)

    return frame


def generate_density_heatmap(base_frame, trajectories_dict, alpha=0.5):
    """Generates a spatial crowd density heatmap from accumulated tracking coordinates."""
    if base_frame is None:
        return None

    h, w = base_frame.shape[:2]
    points = []
    
    if isinstance(trajectories_dict, dict):
        for tid, data in trajectories_dict.items():
            if "centroids" in data:
                for pt in data["centroids"]:
                    points.append((pt[0], pt[1]))
    elif isinstance(trajectories_dict, list):
        for item in trajectories_dict:
            if isinstance(item, dict) and "centroid" in item:
                points.append(item["centroid"])
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                points.append((item[0], item[1]))

    if not points:
        return base_frame.copy()

    heat_matrix = np.zeros((h, w), dtype=np.float32)
    radius = 25
    for cx, cy in points:
        if 0 <= cx < w and 0 <= cy < h:
            x_min = max(0, cx - radius)
            x_max = min(w, cx + radius)
            y_min = max(0, cy - radius)
            y_max = min(h, cy + radius)
            heat_matrix[y_min:y_max, x_min:x_max] += 1.0

    heat_matrix = cv2.GaussianBlur(heat_matrix, (41, 41), 0)
    max_val = np.max(heat_matrix)
    if max_val > 0:
        norm_heat = (heat_matrix / max_val * 255).astype(np.uint8)
    else:
        norm_heat = np.zeros((h, w), dtype=np.uint8)

    color_heat = cv2.applyColorMap(norm_heat, cv2.COLORMAP_JET)
    return cv2.addWeighted(color_heat, alpha, base_frame, 1.0 - alpha, 0)
