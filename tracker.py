from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from config import MODEL_NAME, CONFIDENCE_THRESHOLD, PERSON_CLASS_ID


class MultiObjectTracker:
    def __init__(self, model_name=MODEL_NAME):
        self.model = YOLO(model_name)
        self.tracker = DeepSort(
            max_age=30,
            n_init=2,
            nms_max_overlap=1.0,
            max_cosine_distance=0.4,
        )

    def process_frame(self, frame, persons_only=True):
        results = self.model.predict(
            source=frame,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        detections = []
        names = self.model.names

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                conf = float(box.conf[0].cpu().item())
                cls = int(box.cls[0].cpu().item())

                if persons_only and cls != PERSON_CLASS_ID:
                    continue

                x1, y1, x2, y2 = xyxy
                w, h = x2 - x1, y2 - y1
                detections.append(([x1, y1, w, h], conf, names[cls]))

        tracks = self.tracker.update_tracks(detections, frame=frame)
        output = []

        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)

            output.append({
                "track_id": track.track_id,
                "bbox": (x1, y1, x2, y2),
                "class_name": track.get_det_class() or "object",
            })

        return output
