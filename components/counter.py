import cv2
import numpy as np

class TripwireCounter:
    """
    Virtual tripwire line crossing counter based on tracked centroid trajectories.
    Detects directional crossing (Entry vs Exit) across a configurable line.
    """
    def __init__(self, line_ratio=0.5):
        self.line_ratio = line_ratio
        self.entry_count = 0
        self.exit_count = 0
        
        # State tracking: track_id -> "ABOVE" | "BELOW"
        self.track_positions = {}
        # Set of track_ids that have already crossed in a specific direction
        self.crossed_ids = set()

    def update(self, tracks, frame_shape):
        """
        Updates line crossing counts given active tracks.
        tracks: list of dicts with 'track_id' and 'centroid' (cx, cy)
        """
        if not tracks or frame_shape is None:
            return self.entry_count, self.exit_count

        h, w = frame_shape[:2]
        line_y = int(h * self.line_ratio)

        for track in tracks:
            tid = str(track.get("track_id"))
            centroid = track.get("centroid")
            if centroid is None:
                continue

            cx, cy = centroid
            current_side = "BELOW" if cy > line_y else "ABOVE"

            if tid in self.track_positions:
                prev_side = self.track_positions[tid]

                if prev_side == "ABOVE" and current_side == "BELOW":
                    # Crossed from Above to Below -> Entry
                    crossing_key = f"{tid}_ENTRY"
                    if crossing_key not in self.crossed_ids:
                        self.entry_count += 1
                        self.crossed_ids.add(crossing_key)
                elif prev_side == "BELOW" and current_side == "ABOVE":
                    # Crossed from Below to Above -> Exit
                    crossing_key = f"{tid}_EXIT"
                    if crossing_key not in self.crossed_ids:
                        self.exit_count += 1
                        self.crossed_ids.add(crossing_key)

            self.track_positions[tid] = current_side

        return self.entry_count, self.exit_count

    def reset(self):
        self.entry_count = 0
        self.exit_count = 0
        self.track_positions.clear()
        self.crossed_ids.clear()
