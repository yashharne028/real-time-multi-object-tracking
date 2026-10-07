import os

# Model Settings
# Defaulting to YOLOv8 Nano for maximum real-time performance & 60 FPS streaming on CPU
MODEL_NAME = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.35
PERSON_CLASS_ID = 0

# Crowd Density Classification Thresholds (Persons visible)
LOW_MAX = 5
MEDIUM_MAX = 15

# Default Video Resolution & Inference Dimensions
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
INFERENCE_IMGSZ = 320  # 320x320 downscaled inference for 3x CPU speedup

# Crowd Alert Settings
ALERT_CROWD_LIMIT = 15  # Trigger alert when crowd count reaches or exceeds this
ALERT_COOLDOWN_SEC = 5   # Prevent alert flooding

# Performance Optimization Settings
DEFAULT_FRAME_SKIP = 4   # Run AI inference every Nth frame, interpolate on intermediate frames
TARGET_FPS = 60          # Target stream FPS

# Supported YOLO Models
AVAILABLE_MODELS = {
    "YOLOv8-Nano (Ultra Fast / 60+ FPS)": "yolov8n.pt",
    "YOLOv8-Small (Fast & Accurate)": "yolov8s.pt",
    "YOLOv9-Compact (Balanced)": "yolov9c.pt",
    "YOLOv8-Medium (High Precision)": "yolov8m.pt",
}

# Theme Colors (Dark Surveillance Palette)
THEME_COLORS = {
    "bg_dark": "#0b0f19",
    "card_bg": "#111827",
    "card_border": "#1e293b",
    "accent_cyan": "#06b6d4",
    "accent_green": "#10b981",
    "accent_yellow": "#f59e0b",
    "accent_red": "#ef4444",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
}
