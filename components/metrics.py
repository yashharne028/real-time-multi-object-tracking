import streamlit as st
from config import LOW_MAX, MEDIUM_MAX

def render_top_metrics(current_people, density, fps, active_tracks, low_max=LOW_MAX, medium_max=MEDIUM_MAX):
    """
    Renders 4 top enterprise metric cards with real-time visual density indicators.
    """
    col1, col2, col3, col4 = st.columns(4)

    # Determine density styling and progress
    if density == "LOW":
        density_color = "#10b981"  # Emerald
        density_bar_pct = min(100, int((current_people / max(1, low_max)) * 33))
        bar_text = "████░░░░"
    elif density == "MEDIUM":
        density_color = "#f59e0b"  # Amber
        density_bar_pct = min(100, 33 + int(((current_people - low_max) / max(1, medium_max - low_max)) * 34))
        bar_text = "██████░░"
    else:
        density_color = "#ef4444"  # Crimson
        density_bar_pct = 100
        bar_text = "████████"

    # Card 1: Current People
    with col1:
        st.markdown(f"""
        <div class="metric-glass-card" style="--card-accent: #38bdf8;">
            <div class="metric-label">Current People</div>
            <div class="metric-value" style="color: #38bdf8;">{current_people}</div>
            <div class="metric-subtext">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                Tracked people visible
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Card 2: Density
    with col2:
        st.markdown(f"""
        <div class="metric-glass-card" style="--card-accent: {density_color};">
            <div class="metric-label">Crowd Density</div>
            <div class="metric-value" style="color: {density_color}; font-size: 1.85rem;">{density}</div>
            <div class="metric-subtext" style="font-family: 'JetBrains Mono', monospace; letter-spacing: 1px; color: {density_color};">
                {bar_text} <span style="color: #94a3b8; font-size: 0.7rem; font-family: 'Inter', sans-serif;">({density_bar_pct}%)</span>
            </div>
            <div class="density-bar-container">
                <div class="density-bar-fill" style="width: {density_bar_pct}%; background: {density_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Card 3: FPS
    with col3:
        fps_color = "#10b981" if fps >= 15 else ("#f59e0b" if fps >= 8 else "#ef4444")
        st.markdown(f"""
        <div class="metric-glass-card" style="--card-accent: {fps_color};">
            <div class="metric-label">Processing Speed</div>
            <div class="metric-value" style="color: {fps_color};">{fps:.1f} <span style="font-size: 1rem; font-weight: 500; color: #94a3b8;">FPS</span></div>
            <div class="metric-subtext">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                Inference & Tracking
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Card 4: Active Tracks
    with col4:
        st.markdown(f"""
        <div class="metric-glass-card" style="--card-accent: #818cf8;">
            <div class="metric-label">Active Tracks</div>
            <div class="metric-value" style="color: #818cf8;">{active_tracks}</div>
            <div class="metric-subtext">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                DeepSORT confirmed IDs
            </div>
        </div>
        """, unsafe_allow_html=True)
