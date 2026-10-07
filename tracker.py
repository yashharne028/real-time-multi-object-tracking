import os
import time
import warnings
import cv2
import numpy as np
import torch

# Suppress benign third-party library warnings to keep console clean and fast
warnings.filterwarnings("ignore", category=UserWarning)

# Optimize PyTorch CPU threading for maximum throughput without thread contention
try:
    cpu_cores = os.cpu_count() or 4
    torch.set_num_threads(min(4, cpu_cores))
except Exception:
    pass

from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from config import MODEL_NAME, CONFIDENCE_THRESHOLD, PERSON_CLASS_ID, INFERENCE_IMGSZ


class MultiObjectTracker:
    def __init__(self, model_name=MODEL_NAME, conf_threshold=CONFIDENCE_THRESHOLD, max_age=30, n_init=2, imgsz=INFERENCE_IMGSZ):
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz
        
        # Load YOLO model
        self.model = YOLO(model_name)
        
        # DeepSORT tracker with fixed feature gallery budget (nn_budget=30)
        # Prevents memory growth and keeps cosine distance checks O(1) over long sessions
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            nms_max_overlap=1.0,
            max_cosine_distance=0.4,
            nn_budget=30,
            embedder="mobilenet",
            half=False,
            bgr=True,
            embedder_gpu=False
        )
        
        # Track history dictionary: track_id -> dict
        self.track_histories = {}
        self.max_history_len = 30

    def process_frame(self, frame, persons_only=True, conf_threshold=None):
        if frame is None or frame.size == 0:
            return []

        conf = conf_threshold if conf_threshold is not None else self.conf_threshold

        # Run inference in PyTorch inference_mode for zero memory overhead
        with torch.inference_mode():
            results = self.model.predict(
                source=frame,
                conf=conf,
                imgsz=self.imgsz,
                verbose=False
            )

        detections = []
        names = self.model.names

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                b_conf = float(box.conf[0].cpu().item())
                cls = int(box.cls[0].cpu().item())

                if persons_only and cls != PERSON_CLASS_ID:
                    continue

                x1, y1, x2, y2 = xyxy
                w, h = max(0, x2 - x1), max(0, y2 - y1)
                class_label = names[cls] if cls in names else "person"
                detections.append(([x1, y1, w, h], b_conf, class_label))

        # DeepSORT update
        tracks = self.tracker.update_tracks(detections, frame=frame)
        output = []
        current_time = time.time()
        active_ids = set()

        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            tid = str(track.track_id)
            active_ids.add(tid)
            
            # Centroid
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            class_name = track.get_det_class() or "person"

            # Update trajectory history
            if tid not in self.track_histories:
                self.track_histories[tid] = {
                    "centroids": [(cx, cy, current_time)],
                    "first_seen": current_time,
                    "last_seen": current_time,
                    "class_name": class_name,
                }
            else:
                hist = self.track_histories[tid]["centroids"]
                hist.append((cx, cy, current_time))
                if len(hist) > self.max_history_len:
                    hist.pop(0)
                self.track_histories[tid]["last_seen"] = current_time

            dwell_time = current_time - self.track_histories[tid]["first_seen"]
            history_pts = [(p[0], p[1]) for p in self.track_histories[tid]["centroids"]]

            output.append({
                "track_id": track.track_id,
                "bbox": (x1, y1, x2, y2),
                "class_name": class_name,
                "centroid": (cx, cy),
                "first_seen": self.track_histories[tid]["first_seen"],
                "dwell_time": dwell_time,
                "history": history_pts,
            })

        # Fast cleanup of stale tracks (inactive > 25 seconds)
        stale_threshold = 25.0
        stale_keys = [
            tid for tid, data in self.track_histories.items()
            if tid not in active_ids and (current_time - data["last_seen"]) > stale_threshold
        ]
        for sk in stale_keys:
            del self.track_histories[sk]

        return output

    def reset(self):
        """Reset internal tracker state and trajectory history."""
        self.tracker.delete_all_tracks()
        self.track_histories.clear()
