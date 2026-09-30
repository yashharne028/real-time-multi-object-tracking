# Real-Time Multi-Object Tracking Framework for Crowd Density Estimation

## Capstone Project
A computer-vision system that detects and continuously tracks multiple objects in video streams and estimates crowd density.

### Technology
- Python
- YOLOv9 for object detection
- DeepSORT for multi-object tracking
- OpenCV for video processing
- Streamlit for the demonstration dashboard

### Core Features
- Video-file tracking
- Webcam tracking
- Persistent tracking IDs
- Object counting
- Crowd-density estimation
- FPS display
- Confidence filtering
- Class filtering (person / vehicle / all supported classes)

## Quick Start

### 1. Create environment
```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

### 2. Install packages
```bash
pip install -r requirements.txt
```

### 3. Run the real-time tracker
```bash
python main.py
```

Press `Q` to stop.

### 4. Run the dashboard
```bash
streamlit run dashboard.py
```

Upload an MP4/AVI/MOV video and the application will process it.

## Model
The application uses the YOLOv9 model through the Ultralytics interface. The first run may download the selected model automatically.

## Crowd Density
The demo uses a simple, explainable density classification:
- LOW: 0–5 persons
- MEDIUM: 6–15 persons
- HIGH: 16+ persons

These thresholds are configurable in `config.py`.

## Project Architecture
Camera / Video
    -> YOLOv9 Detection
    -> DeepSORT Tracking
    -> Track IDs
    -> Person Count
    -> Crowd Density
    -> Dashboard / Alerts

## Future Scope
- Heatmap generation
- Entry/exit line crossing
- Restricted-zone alerts
- Multiple camera feeds
- Edge deployment
- Crowd anomaly detection
