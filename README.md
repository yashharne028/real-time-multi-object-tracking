# 🛡️ AI CROWD MONITOR
### Real-Time Multi-Object Tracking & Crowd Density Estimation Framework

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)
![YOLO](https://img.shields.io/badge/YOLO-Ultralytics%20v8%2Fv9-brightgreen.svg)
![DeepSORT](https://img.shields.io/badge/Tracker-DeepSORT%20Realtime-orange.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit%20Enterprise-red.svg)
![Plotly](https://img.shields.io/badge/Analytics-Plotly-purple.svg)

---

## 📌 Project Overview

**AI Crowd Monitor** is a computer vision surveillance and crowd analytics platform designed for public spaces, transit hubs, retail environments, and smart city infrastructure. It combines **Ultralytics YOLO** object detection with **DeepSORT** multi-object tracking to deliver real-time person tracking, crowd density estimation, directional virtual tripwire counting, threshold-based automated safety alerts, and spatial movement heatmaps.

The system features a **Dark Command-Center Web Dashboard** built with Streamlit and custom glassmorphic CSS, as well as a standalone **OpenCV High-Performance CLI Runner**.

---

## 🏗️ System Architecture

```
                       ┌──────────────────────────────┐
                       │  Camera Feed / Video Stream  │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │    Ultralytics YOLO Engine   │
                       │   (Person Detection & BBox)  │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │   DeepSORT Tracking Engine   │
                       │ (Kalman Filter + ReID Embed) │
                       └──────────────┬───────────────┘
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
┌──────────────┐              ┌──────────────┐              ┌────────────────┐
│ Track & Dwell│              │ Crowd Density│              │Virtual Tripwire│
│ Identification              │Classification│              │  Entry / Exit  │
└──────┬───────┘              └──────┬───────┘              └────────┬───────┘
       │                              │                              │
       └──────────────────────────────┼──────────────────────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │  Real-Time Analytics Engine  │
                       │  - Temporal Density Curves   │
                       │  - Spatial Movement Heatmaps │
                       │  - Automated Critical Alerts │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  AI CROWD MONITOR DASHBOARD  │
                       │    (Streamlit Web WebApp)    │
                       └──────────────────────────────┘
```

---

## ✨ Key Features

- **Real-Time Person Tracking**: High-accuracy person detection filtered from COCO classes with persistent DeepSORT IDs.
- **Explainable Crowd Density Estimation**:
  - `LOW`: 0 – 5 persons visible (`████░░░░`)
  - `MEDIUM`: 6 – 15 persons visible (`██████░░`)
  - `HIGH`: 16+ persons visible (`████████`)
- **Virtual Tripwire (Directional Entry / Exit Counting)**: Real-time trajectory crossing detection across configurable lines without double-counting.
- **Automated Crowd Alert System**: Instant visual notifications and event logging when crowd capacity reaches critical limits.
- **Spatial Crowd Movement Heatmap**: Dynamic 2D Gaussian density heatmaps generated from actual tracked person coordinates over time.
- **Batch Video Analysis**: Upload pre-recorded CCTV footage (`.mp4`, `.avi`, `.mov`, `.mkv`) for automated telemetry analysis, frame scrubbing, and peak crowd metrics.
- **Interactive Plotly Telemetry**: Real-time area charts for crowd count over time, density state transitions, and inference FPS monitoring.
- **Modular Architecture**: Clean separation between AI tracker, utilities, components, and user interfaces.

---

## 📂 Repository Structure

```
Real_Time_Multi_Object_Tracking/
├── app.py                     # Main Streamlit Web Application (AI Crowd Monitor)
├── dashboard.py               # Compatibility wrapper for Streamlit
├── main.py                    # Standalone OpenCV Real-Time CLI Runner
├── tracker.py                 # Core AI Engine (YOLO + DeepSORT + Trajectories)
├── utils.py                   # High-tech HUD overlays, drawing routines, heatmaps
├── config.py                  # Global settings, model paths, thresholds, and theme
├── requirements.txt           # Python dependencies
├── README.md                  # System documentation
│
├── components/                # Modular Dashboard UI Components
│   ├── __init__.py
│   ├── dashboard_ui.py        # Dark surveillance theme, glassmorphism CSS & badges
│   ├── metrics.py             # Top 4 dynamic metric cards & density bar
│   ├── charts.py              # Plotly real-time telemetry charts
│   ├── alerts.py              # CrowdAlertEngine & alert log renderer
│   ├── counter.py             # Directional TripwireCounter logic
│   ├── heatmap.py             # Spatial CrowdHeatmapManager
│   └── tracked_table.py       # Live active tracked objects telemetry table
│
├── assets/
│   └── sample_crowd.mp4       # Sample video for immediate testing
│
└── models/                    # Directory for YOLO model checkpoints (.pt files)
```

---

## 🚀 Quick Start & Installation

### 1. Clone & Set Up Virtual Environment

```bash
# Navigate to project directory
cd Real_Time_Multi_Object_Tracking

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🖥️ Running the Application

### Option A: Web Dashboard (Recommended)

Launch the full interactive command-center dashboard:

```bash
streamlit run app.py
```

*Or via the compatibility alias:*
```bash
streamlit run dashboard.py
```

Open your browser and navigate to `http://localhost:8501`.

### Option B: Standalone OpenCV CLI Runner

Run the lightweight, ultra-fast OpenCV video window directly from your terminal:

```bash
# Run with default laptop webcam (Source 0)
python main.py --source 0

# Run with an external USB camera (Source 1)
python main.py --source 1

# Run with a video file
python main.py --source path/to/cctv_video.mp4

# Run with a lightweight YOLO model (Fast CPU performance)
python main.py --source 0 --model yolov8n.pt --conf 0.35 --skip 3
```

*Press `q` inside the OpenCV window to exit.*

---

## ⚙️ Configuration & Customization

All core parameters can be configured either via `config.py` or directly from the **Settings** page in the Web Dashboard:

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `MODEL_NAME` | `yolov9c.pt` | Default YOLO model checkpoint |
| `CONFIDENCE_THRESHOLD` | `0.35` | Minimum confidence score for person detections |
| `LOW_MAX` | `5` | Upper limit for LOW crowd density |
| `MEDIUM_MAX` | `15` | Upper limit for MEDIUM crowd density |
| `ALERT_CROWD_LIMIT` | `15` | Capacity limit triggering critical crowd alerts |
| `DEFAULT_FRAME_SKIP` | `3` | AI inference interval (frames) for high CPU speed |

---

## ⚡ Performance Optimization

1. **Lightweight Models**: On CPU-only machines, select `YOLOv8-Nano (yolov8n.pt)` or `YOLOv8-Small (yolov8s.pt)` in the Settings tab for 30+ FPS tracking.
2. **Frame Skipping**: The dashboard processes AI detection every $N^{\text{th}}$ frame (`cfg_frame_interval`) and smoothly updates tracking on intermediate frames.
3. **Streamlit Resource Caching**: Uses `@st.cache_resource` to keep a single YOLO and DeepSORT instance in memory across reruns.

---

## 🧪 College Project / Viva Presentation Highlights

- **Detection vs Tracking**: Explains why combining YOLO (frame-by-frame spatial detector) with DeepSORT (temporal Kalman filtering + appearance ReID embeddings) reduces identity switches and computational overhead.
- **Density Estimation**: Demonstrates explainable rule-based density classification with visual HUD telemetry.
- **Directional Counting**: Explains mathematical line crossing using centroid vector displacement ($y_{t-1} \to y_t$ relative to line ratio).
- **Spatial Heatmaps**: Explains 2D Gaussian kernel accumulation to identify crowd bottleneck areas.

---

## 📄 License
This project is open-source and available under the MIT License.
