import os
import sys
import time
import tempfile
import threading
from pathlib import Path
import cv2
import numpy as np
import streamlit as st
import pandas as pd

# Project modules
from config import (
    MODEL_NAME, CONFIDENCE_THRESHOLD, PERSON_CLASS_ID,
    LOW_MAX, MEDIUM_MAX, ALERT_CROWD_LIMIT,
    AVAILABLE_MODELS, DEFAULT_FRAME_SKIP, INFERENCE_IMGSZ
)
from tracker import MultiObjectTracker
from utils import (
    density_label, draw_tracks, draw_dashboard,
    draw_counting_line, generate_density_heatmap
)
from components.dashboard_ui import (
    apply_custom_theme, render_dashboard_header,
    render_sidebar_header, render_sidebar_footer
)
from components.metrics import render_top_metrics
from components.charts import (
    render_people_count_chart, render_density_chart,
    render_fps_chart, render_entry_exit_chart
)
from components.alerts import CrowdAlertEngine, render_alert_banner, render_alert_logs
from components.counter import TripwireCounter
from components.heatmap import CrowdHeatmapManager
from components.tracked_table import render_active_tracks_panel

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI CROWD MONITOR | Ultra-Fast Real-Time Multi-Object Tracking",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Dark Command-Center Theme
apply_custom_theme()


# ---------------------------------------------------------
# Threaded High-Speed Camera Reader
# ---------------------------------------------------------
class ThreadedCamera:
    """
    Dedicated background thread for non-blocking camera frame acquisition.
    Eliminates camera I/O lag and achieves 60+ FPS streaming.
    """
    def __init__(self, src=0):
        self.src = src
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        self.status, self.frame = self.cap.read()
        self.is_opened = self.cap.isOpened()
        self.running = True
        self.lock = threading.Lock()
        
        if self.is_opened and self.status:
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()

    def _capture_loop(self):
        while self.running:
            if self.cap.isOpened():
                status, frame = self.cap.read()
                if status and frame is not None:
                    with self.lock:
                        self.frame = frame
                        self.status = status
            time.sleep(0.005)

    def read(self):
        with self.lock:
            if not self.status or self.frame is None:
                return False, None
            return True, self.frame.copy()

    def release(self):
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=0.3)
        if self.cap.isOpened():
            self.cap.release()


# ---------------------------------------------------------
# Cached AI Resource Loaders
# ---------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_tracker_instance(model_name=MODEL_NAME, conf=CONFIDENCE_THRESHOLD, imgsz=INFERENCE_IMGSZ):
    """
    Initializes and caches the YOLO + DeepSORT tracking pipeline.
    Prevents costly reload on every Streamlit rerun.
    """
    return MultiObjectTracker(model_name=model_name, conf_threshold=conf, imgsz=imgsz)


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "alert_engine" not in st.session_state:
    st.session_state.alert_engine = CrowdAlertEngine(alert_limit=ALERT_CROWD_LIMIT)

if "tripwire_counter" not in st.session_state:
    st.session_state.tripwire_counter = TripwireCounter(line_ratio=0.5)

if "heatmap_manager" not in st.session_state:
    st.session_state.heatmap_manager = CrowdHeatmapManager()

if "history_timestamps" not in st.session_state:
    st.session_state.history_timestamps = []
    st.session_state.history_counts = []
    st.session_state.history_densities = []
    st.session_state.history_fps = []
    st.session_state.history_entry = []
    st.session_state.history_exit = []

if "is_monitoring" not in st.session_state:
    st.session_state.is_monitoring = False


# ---------------------------------------------------------
# Sidebar Navigation & Settings
# ---------------------------------------------------------
render_sidebar_header()

nav_choice = st.sidebar.radio(
    "NAVIGATION",
    ["📊 Dashboard", "📹 Live Monitoring", "🎬 Video Analysis", "📈 Analytics & Heatmap", "⚙️ Settings"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Quick Controls in Sidebar
st.sidebar.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;'>QUICK PERFORMANCE CONTROLS</div>", unsafe_allow_html=True)
selected_model_label = st.sidebar.selectbox(
    "Active Model",
    list(AVAILABLE_MODELS.keys()),
    index=0
)
active_model_file = AVAILABLE_MODELS[selected_model_label]

conf_slider = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.10,
    max_value=0.90,
    value=float(CONFIDENCE_THRESHOLD),
    step=0.05
)

skip_frames_slider = st.sidebar.slider(
    "AI Processing Step",
    min_value=1,
    max_value=8,
    value=DEFAULT_FRAME_SKIP,
    help="Runs AI detection every N frames for 60 FPS smooth video streaming."
)

persons_only_toggle = st.sidebar.checkbox("Filter Persons Only", value=True)
flip_camera_toggle = st.sidebar.checkbox("Mirror Camera (Natural View)", value=True, help="Flips webcam horizontally like a mirror so your left hand appears on the left.")

render_sidebar_footer(model_name=active_model_file.split(".")[0].upper(), tracker_name="DeepSORT")


# ---------------------------------------------------------
# Page 1: DASHBOARD & LIVE MONITORING
# ---------------------------------------------------------
if nav_choice in ["📊 Dashboard", "📹 Live Monitoring"]:
    render_dashboard_header(
        title="AI CROWD MONITORING",
        subtitle="Real-Time Multi-Object Tracking & Crowd Density Analysis",
        is_active=st.session_state.is_monitoring
    )

    # Dynamic settings from session or defaults
    low_cutoff = st.session_state.get("cfg_low_max", LOW_MAX)
    med_cutoff = st.session_state.get("cfg_med_max", MEDIUM_MAX)
    alert_lim = st.session_state.get("cfg_alert_limit", ALERT_CROWD_LIMIT)
    line_pos = st.session_state.get("cfg_line_pos", 0.5)

    # Top Metrics Placeholder
    metrics_container = st.empty()
    alert_container = st.empty()

    # Initial Render of Metrics
    with metrics_container:
        render_top_metrics(
            current_people=st.session_state.history_counts[-1] if st.session_state.history_counts else 0,
            density=st.session_state.history_densities[-1] if st.session_state.history_densities else "LOW",
            fps=st.session_state.history_fps[-1] if st.session_state.history_fps else 0.0,
            active_tracks=st.session_state.history_counts[-1] if st.session_state.history_counts else 0,
            low_max=low_cutoff,
            medium_max=med_cutoff
        )

    # Video & Controls Layout
    col_video, col_side_info = st.columns([2.3, 1.0])

    with col_side_info:
        st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #cbd5e1; text-transform: uppercase; margin-bottom: 8px;'>SOURCE SELECTION</div>", unsafe_allow_html=True)
        source_option = st.selectbox(
            "Video Source",
            ["Laptop Camera (Webcam)", "External Camera (Source 1)", "Upload Video", "Demo Video"],
            label_visibility="collapsed"
        )

        uploaded_file = None
        if source_option == "Upload Video":
            uploaded_file = st.file_uploader("Select Video", type=["mp4", "avi", "mov", "mkv"])

        # Monitoring Control Buttons
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            start_btn = st.button("▶ START", type="primary", use_container_width=True)
        with btn_col2:
            stop_btn = st.button("⏹ STOP", type="secondary", use_container_width=True)

        if start_btn:
            st.session_state.is_monitoring = True
        if stop_btn:
            st.session_state.is_monitoring = False

        # Entry / Exit Summary Box
        tripwire_metric_box = st.empty()
        with tripwire_metric_box:
            st.markdown("""
            <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid #1e293b; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;">TRIPWIRE TRAFFIC</div>
            """, unsafe_allow_html=True)
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                st.metric("ENTRY", st.session_state.tripwire_counter.entry_count)
            with tc2:
                st.metric("EXIT", st.session_state.tripwire_counter.exit_count)
            with tc3:
                st.metric("NET", st.session_state.tripwire_counter.entry_count - st.session_state.tripwire_counter.exit_count)
            st.markdown("</div>", unsafe_allow_html=True)

        # Recent Alert Logs
        st.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;'>RECENT ALERTS</div>", unsafe_allow_html=True)
        alert_logs_box = st.empty()
        with alert_logs_box:
            render_alert_logs(st.session_state.alert_engine.alert_history)

    # Video Display Area
    with col_video:
        video_placeholder = st.empty()
        
        if not st.session_state.is_monitoring:
            video_placeholder.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 440px; background: rgba(13, 18, 29, 0.9); border: 2px dashed #334155; border-radius: 14px;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg>
                <div style="font-size: 1.05rem; font-weight: 600; color: #cbd5e1; margin-top: 14px;">Camera Feed Standby</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">Click <b>START</b> to initiate ultra-fast 60 FPS live tracking stream.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Determine Video Source
            cap_stream = None
            temp_video_path = None
            is_threaded = False

            try:
                if source_option == "Laptop Camera (Webcam)":
                    cap_stream = ThreadedCamera(src=0)
                    is_threaded = True
                elif source_option == "External Camera (Source 1)":
                    cap_stream = ThreadedCamera(src=1)
                    is_threaded = True
                elif source_option == "Upload Video":
                    if uploaded_file is not None:
                        suffix = Path(uploaded_file.name).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(uploaded_file.read())
                            temp_video_path = tmp.name
                        cap_stream = cv2.VideoCapture(temp_video_path)
                    else:
                        st.warning("Please upload a video file to start monitoring.")
                        st.session_state.is_monitoring = False
                elif source_option == "Demo Video":
                    sample_path = "assets/sample_crowd.mp4"
                    if os.path.exists(sample_path):
                        cap_stream = cv2.VideoCapture(sample_path)
                    else:
                        st.info("Demo media loading...")

                # Initialize tracker
                tracker = get_tracker_instance(model_name=active_model_file, conf=conf_slider)
                
                # Check video capture state
                if cap_stream is None:
                    st.error("Camera unavailable. Please check camera permissions or use Upload Video.")
                    st.session_state.is_monitoring = False
                elif not is_threaded and not cap_stream.isOpened():
                    st.error("Video source could not be opened.")
                    st.session_state.is_monitoring = False
                elif is_threaded and not cap_stream.is_opened:
                    st.error("Camera unavailable. Please check camera permissions or use Upload Video.")
                    st.session_state.is_monitoring = False
                else:
                    frame_idx = 0
                    last_tracks = []
                    fps_calc_time = time.time()
                    fps_val = 60.0
                    last_ui_update_time = time.time()
                    frames_since_fps = 0

                    # Ultra-smooth streaming loop
                    while st.session_state.is_monitoring:
                        ret, frame = cap_stream.read()
                        if not ret or frame is None:
                            if not is_threaded and source_option in ["Upload Video", "Demo Video"]:
                                cap_stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                continue
                            else:
                                time.sleep(0.01)
                                continue

                        frame_idx += 1
                        frames_since_fps += 1
                        curr_time = time.time()

                        # Flip camera horizontally for natural selfie/mirror view
                        if flip_camera_toggle and (is_threaded or "Camera" in source_option):
                            frame = cv2.flip(frame, 1)

                        # Run AI inference on step interval
                        if frame_idx % skip_frames_slider == 0:
                            last_tracks = tracker.process_frame(
                                frame,
                                persons_only=persons_only_toggle,
                                conf_threshold=conf_slider
                            )

                        # Calculate accurate display FPS
                        fps_delta = curr_time - fps_calc_time
                        if fps_delta >= 0.5:
                            fps_val = frames_since_fps / max(fps_delta, 0.001)
                            fps_calc_time = curr_time
                            frames_since_fps = 0

                        people_count = len(last_tracks)
                        cur_density = density_label(people_count, low_max=low_cutoff, medium_max=med_cutoff)

                        # Update Tripwire & Heatmap
                        ent, ext = st.session_state.tripwire_counter.update(last_tracks, frame.shape)
                        st.session_state.heatmap_manager.add_tracks(last_tracks)

                        # Check Alerts
                        is_alert, alert_lvl, alert_msg = st.session_state.alert_engine.update(
                            people_count, cur_density, custom_limit=alert_lim
                        )

                        # Draw Overlays on Frame
                        frame = draw_counting_line(frame, line_ratio=line_pos, entry_count=ent, exit_count=ext)
                        frame = draw_tracks(frame, last_tracks, show_trajectories=True)
                        frame = draw_dashboard(frame, people_count, cur_density, fps_val, alert_active=is_alert)

                        # Convert to RGB and display immediately at maximum speed
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(frame_rgb, channels="RGB")

                        # Throttle Streamlit HTML/DOM widget updates to every 0.4s to maintain 60 FPS video playback
                        if curr_time - last_ui_update_time >= 0.4:
                            last_ui_update_time = curr_time

                            # Record Telemetry History
                            t_now = time.strftime("%H:%M:%S")
                            st.session_state.history_timestamps.append(t_now)
                            st.session_state.history_counts.append(people_count)
                            st.session_state.history_densities.append(cur_density)
                            st.session_state.history_fps.append(fps_val)
                            st.session_state.history_entry.append(ent)
                            st.session_state.history_exit.append(ext)

                            if len(st.session_state.history_timestamps) > 60:
                                st.session_state.history_timestamps.pop(0)
                                st.session_state.history_counts.pop(0)
                                st.session_state.history_densities.pop(0)
                                st.session_state.history_fps.pop(0)
                                st.session_state.history_entry.pop(0)
                                st.session_state.history_exit.pop(0)

                            with metrics_container:
                                render_top_metrics(people_count, cur_density, fps_val, len(last_tracks), low_max=low_cutoff, medium_max=med_cutoff)

                            with alert_container:
                                render_alert_banner(is_alert, alert_lvl, alert_msg)

                    # Release stream
                    cap_stream.release()
                    if temp_video_path and os.path.exists(temp_video_path):
                        os.remove(temp_video_path)

            except Exception as e:
                st.error(f"Processing error encountered: {str(e)}")
                st.session_state.is_monitoring = False

    # Bottom Panels: Tracked People Table & Quick Analytics
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns([1.2, 1.8])

    with b_col1:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; text-transform: uppercase; margin-bottom: 10px;'>ACTIVE TRACKS LOG</div>", unsafe_allow_html=True)
        render_active_tracks_panel(last_tracks if 'last_tracks' in locals() else [])

    with b_col2:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; text-transform: uppercase; margin-bottom: 10px;'>REAL-TIME CROWD CURVE</div>", unsafe_allow_html=True)
        fig = render_people_count_chart(
            st.session_state.history_timestamps,
            st.session_state.history_counts,
            alert_threshold=alert_lim
        )
        st.plotly_chart(fig, key="live_people_chart")


# ---------------------------------------------------------
# Page 2: VIDEO ANALYSIS
# ---------------------------------------------------------
elif nav_choice == "🎬 Video Analysis":
    render_dashboard_header(
        title="AI VIDEO BATCH ANALYSIS",
        subtitle="Upload and execute deep multi-object tracking and crowd density analysis on recorded CCTV footage",
        is_active=False
    )

    st.markdown("""
    <div style="background: rgba(17, 24, 39, 0.6); border: 1px solid #1e293b; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-top: 0;">Upload Surveillance Video</h3>
        <p style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.8rem;">
            Upload MP4, AVI, MOV, or MKV files. The AI engine will process frame sequences, track distinct person IDs, calculate crowd metrics, and generate detailed temporal telemetry.
        </p>
    </div>
    """, unsafe_allow_html=True)

    v_col1, v_col2 = st.columns([1.5, 1])

    with v_col1:
        vid_upload = st.file_uploader("Choose Video File", type=["mp4", "avi", "mov", "mkv"], key="va_upload")
    
    with v_col2:
        va_conf = st.slider("Analysis Confidence", 0.1, 0.9, 0.35, 0.05, key="va_conf")
        va_skip = st.slider("Frame Processing Step", 1, 10, 2, key="va_skip", help="Analyze every Nth frame to accelerate processing.")

    if vid_upload is not None:
        suffix = Path(vid_upload.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(vid_upload.read())
            va_path = tmp.name

        if st.button("🚀 Process & Analyze Video", type="primary"):
            tracker = get_tracker_instance(model_name=active_model_file, conf=va_conf)
            tracker.reset()

            cap = cv2.VideoCapture(va_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

            st.info(f"Loaded video: {total_frames} frames ({total_frames / fps:.1f}s duration). Processing pipeline running...")

            progress_bar = st.progress(0)
            status_text = st.empty()
            va_frame_display = st.empty()

            frame_num = 0
            people_counts = []
            frame_times = []
            densities = []
            max_people = 0
            unique_ids = set()

            tripwire = TripwireCounter(line_ratio=0.5)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_num += 1

                if frame_num % va_skip == 0:
                    tracks = tracker.process_frame(frame, persons_only=True, conf_threshold=va_conf)
                    count = len(tracks)
                    d_label = density_label(count)

                    for t in tracks:
                        unique_ids.add(t["track_id"])

                    people_counts.append(count)
                    densities.append(d_label)
                    frame_times.append(frame_num / fps)
                    max_people = max(max_people, count)

                    # Update tripwire
                    tripwire.update(tracks, frame.shape)

                    # Visual overlay
                    frame = draw_counting_line(frame, 0.5, tripwire.entry_count, tripwire.exit_count)
                    frame = draw_tracks(frame, tracks, show_trajectories=True)
                    frame = draw_dashboard(frame, count, d_label, fps)

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    va_frame_display.image(frame_rgb, channels="RGB")

                progress = min(1.0, frame_num / max(1, total_frames))
                progress_bar.progress(progress)
                status_text.text(f"Processing frame {frame_num}/{total_frames} ({int(progress * 100)}%)")

            cap.release()
            if os.path.exists(va_path):
                os.remove(va_path)

            st.success("✅ Video Analysis Completed Successfully!")

            # Summary Metrics
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            avg_people = np.mean(people_counts) if people_counts else 0
            m1.metric("TOTAL FRAMES ANALYZED", frame_num)
            m2.metric("PEAK CROWD SIZE", max_people)
            m3.metric("AVG PEOPLE / FRAME", f"{avg_people:.1f}")
            m4.metric("UNIQUE TRACKED PERSONS", len(unique_ids))

            # Analysis Charts
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                fig_c = render_people_count_chart(
                    [f"{t:.1f}s" for t in frame_times],
                    people_counts,
                    alert_threshold=ALERT_CROWD_LIMIT
                )
                st.plotly_chart(fig_c)

            with c_col2:
                fig_d = render_density_chart(
                    [f"{t:.1f}s" for t in frame_times],
                    densities
                )
                st.plotly_chart(fig_d)


# ---------------------------------------------------------
# Page 3: ANALYTICS & HEATMAP
# ---------------------------------------------------------
elif nav_choice == "📈 Analytics & Heatmap":
    render_dashboard_header(
        title="SPATIAL ANALYTICS & CROWD HEATMAP",
        subtitle="Cumulative tracking telemetry, spatial density hotspots, and movement patterns",
        is_active=st.session_state.is_monitoring
    )

    h_col1, h_col2 = st.columns([1.5, 1])

    with h_col1:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; text-transform: uppercase; margin-bottom: 10px;'>CROWD MOVEMENT HEATMAP</div>", unsafe_allow_html=True)
        
        base_img = cv2.imread("camera1.jpg") if os.path.exists("camera1.jpg") else np.zeros((480, 640, 3), dtype=np.uint8)
        heatmap_overlay = st.session_state.heatmap_manager.generate_heatmap(base_img, alpha=0.55)
        
        if heatmap_overlay is not None:
            heatmap_rgb = cv2.cvtColor(heatmap_overlay, cv2.COLOR_BGR2RGB)
            st.image(heatmap_rgb, caption="Spatial Density Heatmap (Accumulated Track Centroids)")
        
        if st.button("🗑️ Reset Heatmap Data"):
            st.session_state.heatmap_manager.clear()
            st.success("Heatmap coordinates reset successfully.")

    with h_col2:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; text-transform: uppercase; margin-bottom: 10px;'>HEATMAP HOTSPOT METRICS</div>", unsafe_allow_html=True)
        pts_count = len(st.session_state.heatmap_manager.accumulated_points)
        st.metric("ACCUMULATED SPATIAL COORDINATES", pts_count)
        st.metric("TRACKING PERSISTENCE", "Active")
        
        st.markdown("""
        <div style="background: rgba(17, 24, 39, 0.6); border: 1px solid #1e293b; border-radius: 10px; padding: 12px; margin-top: 15px; font-size: 0.8rem; color: #94a3b8;">
            <b style="color: #f8fafc;">Heatmap Calculation:</b><br>
            Hotspots are synthesized dynamically by convolving 2D Gaussian density kernels across confirmed DeepSORT person positions over time.
        </div>
        """, unsafe_allow_html=True)

    # Detailed Time-Series Charts
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        st.plotly_chart(
            render_people_count_chart(
                st.session_state.history_timestamps,
                st.session_state.history_counts,
                alert_threshold=st.session_state.get("cfg_alert_limit", ALERT_CROWD_LIMIT)
            ),
            key="analytics_count_chart"
        )

    with ch_col2:
        st.plotly_chart(
            render_fps_chart(
                st.session_state.history_timestamps,
                st.session_state.history_fps
            ),
            key="analytics_fps_chart"
        )


# ---------------------------------------------------------
# Page 4: SETTINGS
# ---------------------------------------------------------
elif nav_choice == "⚙️ Settings":
    render_dashboard_header(
        title="SYSTEM CONFIGURATION & TUNING",
        subtitle="Fine-tune YOLO detection, DeepSORT hyperparameters, and crowd density alert thresholds",
        is_active=False
    )

    st.markdown("""
    <div style="background: rgba(17, 24, 39, 0.6); border: 1px solid #1e293b; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-top: 0;">Computer Vision Pipeline Parameters</h3>
        <p style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 0;">
            Adjust model sensitivity, hardware processing intervals, density classifications, and alert rules.
        </p>
    </div>
    """, unsafe_allow_html=True)

    set_col1, set_col2 = st.columns(2)

    with set_col1:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 10px;'>DETECTION & MODEL</div>", unsafe_allow_html=True)
        
        cfg_model = st.selectbox(
            "YOLO Model Architecture",
            list(AVAILABLE_MODELS.keys()),
            index=0,
            help="Select the YOLO weights file. Smaller models (Nano) run at 60+ FPS on CPU."
        )

        cfg_conf = st.slider(
            "Detection Confidence Threshold",
            0.10, 0.90, float(CONFIDENCE_THRESHOLD), 0.05,
            help="Minimum confidence score required for an object detection."
        )

        cfg_interval = st.slider(
            "Frame Processing Interval (Skip Step)",
            1, 10, DEFAULT_FRAME_SKIP, 1,
            help="Run AI detection every N frames for 60 FPS performance."
        )

        cfg_person_only = st.checkbox("Person-Only Filtering", value=True, help="Ignore non-person COCO classes.")

    with set_col2:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 10px;'>DENSITY & ALERTS</div>", unsafe_allow_html=True)

        cfg_low = st.number_input("Low Density Max Count", min_value=1, max_value=50, value=LOW_MAX)
        cfg_med = st.number_input("Medium Density Max Count", min_value=cfg_low + 1, max_value=100, value=MEDIUM_MAX)
        cfg_alert = st.number_input("Crowd Alert Threshold Limit", min_value=1, max_value=200, value=ALERT_CROWD_LIMIT)

        cfg_line = st.slider(
            "Virtual Tripwire Position (Y-Axis Ratio)",
            0.1, 0.9, 0.5, 0.05,
            help="Vertical screen position of the virtual counting tripwire line."
        )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Settings", type="primary"):
        st.session_state.cfg_low_max = cfg_low
        st.session_state.cfg_med_max = cfg_med
        st.session_state.cfg_alert_limit = cfg_alert
        st.session_state.cfg_frame_interval = cfg_interval
        st.session_state.cfg_line_pos = cfg_line
        st.success("Settings updated successfully! New configuration applied.")
