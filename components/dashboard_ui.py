import streamlit as st

def apply_custom_theme():
    """
    Injects high-end surveillance and AI command-center styling.
    Features dark glassmorphism, glowing status indicators, and clean cards.
    """
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

        /* Global Theme */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #080b11;
            color: #f1f5f9;
        }

        /* Top Header Area */
        header[data-testid="stHeader"] {
            background-color: rgba(8, 11, 17, 0.85);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0d121d;
            border-right: 1px solid #1e293b;
        }

        section[data-testid="stSidebar"] div.block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }

        /* Main Container Spacing */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 96%;
        }

        /* Brand Title */
        .brand-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.2rem 1.6rem;
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(15, 23, 42, 0.8));
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 14px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        }

        .brand-title {
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-subtitle {
            font-size: 0.82rem;
            color: #94a3b8;
            font-weight: 500;
            margin-top: 3px;
        }

        /* Glowing Status Badge */
        .status-badge-online {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .pulse-dot-green {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 2s infinite;
        }

        .pulse-dot-red {
            width: 8px;
            height: 8px;
            background-color: #ef4444;
            border-radius: 50%;
            box-shadow: 0 0 10px #ef4444;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 14px currentColor; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* Glassmorphism Cards */
        .metric-glass-card {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
            transition: all 0.2s ease-in-out;
            position: relative;
            overflow: hidden;
        }

        .metric-glass-card:hover {
            border-color: rgba(56, 189, 248, 0.35);
            transform: translateY(-2px);
        }

        .metric-glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--card-accent, #38bdf8);
        }

        .metric-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #94a3b8;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.1rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.1;
        }

        .metric-subtext {
            font-size: 0.75rem;
            color: #64748b;
            margin-top: 0.4rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        /* Density Progress Bar */
        .density-bar-container {
            width: 100%;
            height: 8px;
            background-color: #1e293b;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }

        .density-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        /* Video Container Panel */
        .cctv-panel-wrapper {
            background: #0d121d;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            margin-bottom: 1.5rem;
        }

        .cctv-panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 0.75rem;
        }

        .cctv-live-tag {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #ef4444;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Sidebar Logo */
        .sidebar-brand {
            padding: 0.5rem 0.5rem 1.2rem 0.5rem;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 1.2rem;
        }

        .sidebar-brand-title {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .sidebar-brand-sub {
            font-size: 0.72rem;
            color: #38bdf8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 2px;
        }

        /* Sidebar Footer */
        .sidebar-footer {
            margin-top: 2.5rem;
            padding: 1rem;
            background: rgba(17, 24, 39, 0.6);
            border: 1px solid #1e293b;
            border-radius: 10px;
            font-size: 0.78rem;
        }

        .sidebar-footer-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.4rem;
            color: #94a3b8;
        }

        .sidebar-footer-row span.val {
            color: #e2e8f0;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Alert Panel */
        .alert-panel {
            padding: 0.85rem 1.2rem;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.2rem;
            font-size: 0.88rem;
            font-weight: 600;
        }

        .alert-normal {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
            color: #34d399;
        }

        .alert-warning {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fbbf24;
        }

        .alert-danger {
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
        }

        /* Streamlit Native Elements Override */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.02em;
            transition: all 0.2s;
        }
        
        div[data-testid="stFileUploader"] {
            border: 1px dashed #334155;
            border-radius: 12px;
            padding: 1rem;
            background: rgba(15, 23, 42, 0.4);
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_dashboard_header(title="AI CROWD MONITORING", subtitle="Real-Time Multi-Object Tracking & Crowd Density Analysis", is_active=True):
    """Renders the top enterprise command-center dashboard header."""
    status_html = """
    <div class="status-badge-online">
        <div class="pulse-dot-green"></div>
        SYSTEM ONLINE
    </div>
    """ if is_active else """
    <div class="status-badge-online" style="background: rgba(239, 68, 68, 0.12); color: #f87171; border-color: rgba(239, 68, 68, 0.3);">
        <div class="pulse-dot-red"></div>
        SYSTEM STANDBY
    </div>
    """

    st.markdown(f"""
    <div class="brand-header">
        <div>
            <h1 class="brand-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M3 7V5a2 2 0 0 1 2-2h2"></path>
                    <path d="M17 3h2a2 2 0 0 1 2 2v2"></path>
                    <path d="M21 17v2a2 2 0 0 1-2 2h-2"></path>
                    <path d="M7 21H5a2 2 0 0 1-2-2v-2"></path>
                </svg>
                {title}
            </h1>
            <div class="brand-subtitle">{subtitle}</div>
        </div>
        <div>
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_header():
    """Renders the brand sidebar header."""
    st.sidebar.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            AI CROWD MONITOR
        </div>
        <div class="sidebar-brand-sub">Computer Vision Engine</div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_footer(model_name="YOLOv9c", tracker_name="DeepSORT"):
    """Renders the system status sidebar footer."""
    st.sidebar.markdown(f"""
    <div class="sidebar-footer">
        <div class="sidebar-footer-row" style="margin-bottom: 0.7rem;">
            <span style="display: flex; align-items: center; gap: 6px; color: #34d399; font-weight: 700;">
                <div class="pulse-dot-green" style="width: 6px; height: 6px;"></div>
                AI Engine Online
            </span>
        </div>
        <div class="sidebar-footer-row">
            <span>Model:</span>
            <span class="val">{model_name}</span>
        </div>
        <div class="sidebar-footer-row">
            <span>Tracker:</span>
            <span class="val">{tracker_name}</span>
        </div>
        <div class="sidebar-footer-row" style="margin-bottom: 0;">
            <span>Inference:</span>
            <span class="val">Real-Time</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
