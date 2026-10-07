import cv2
import numpy as np

class CrowdHeatmapManager:
    """
    Accumulates real tracked coordinates and generates spatial crowd density heatmaps.
    """
    def __init__(self, decay_factor=0.995):
        self.accumulated_points = []
        self.decay_factor = decay_factor
        self.max_points = 5000

    def add_tracks(self, tracks):
        """Adds current active track centroids to the heatmap accumulator."""
        for t in tracks:
            if "centroid" in t:
                self.accumulated_points.append(t["centroid"])

        if len(self.accumulated_points) > self.max_points:
            self.accumulated_points = self.accumulated_points[-self.max_points:]

    def generate_heatmap(self, base_frame, alpha=0.5):
        """Generates overlaid heatmap onto the provided frame."""
        if base_frame is None:
            return None

        h, w = base_frame.shape[:2]
        if not self.accumulated_points:
            return base_frame.copy()

        # Build 2D heat matrix
        heat_matrix = np.zeros((h, w), dtype=np.float32)
        radius = 28

        for cx, cy in self.accumulated_points:
            if 0 <= cx < w and 0 <= cy < h:
                x1 = max(0, cx - radius)
                x2 = min(w, cx + radius)
                y1 = max(0, cy - radius)
                y2 = min(h, cy + radius)
                heat_matrix[y1:y2, x1:x2] += 1.0

        # Gaussian blur
        heat_matrix = cv2.GaussianBlur(heat_matrix, (45, 45), 0)
        max_val = np.max(heat_matrix)

        if max_val > 0:
            norm_heat = (heat_matrix / max_val * 255).astype(np.uint8)
        else:
            norm_heat = np.zeros((h, w), dtype=np.uint8)

        # Colormap
        color_heat = cv2.applyColorMap(norm_heat, cv2.COLORMAP_JET)
        
        # Alpha blend with base frame
        blended = cv2.addWeighted(color_heat, alpha, base_frame, 1.0 - alpha, 0)
        return blended

    def clear(self):
        """Resets the accumulated heatmap data."""
        self.accumulated_points.clear()
