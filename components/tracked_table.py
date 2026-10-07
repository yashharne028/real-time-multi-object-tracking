import time
import streamlit as st

def render_active_tracks_panel(tracks):
    """
    Renders a live table / panel showing currently active tracked targets.
    Displays ID, Class, Position, Dwell Time, and Status.
    """
    if not tracks:
        st.markdown("""
        <div style="padding: 1.2rem; background: rgba(15, 23, 42, 0.4); border-radius: 8px; border: 1px solid #1e293b; color: #64748b; text-align: center; font-size: 0.82rem;">
            No active targets currently tracked in frame.
        </div>
        """, unsafe_allow_html=True)
        return

    table_rows = []
    for item in tracks:
        tid = item.get("track_id", "?")
        cls = item.get("class_name", "person").capitalize()
        cx, cy = item.get("centroid", (0, 0))
        dwell = item.get("dwell_time", 0.0)
        
        table_rows.append(f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.82rem;">
            <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #38bdf8;">#{tid}</td>
            <td style="padding: 8px 12px; color: #e2e8f0;">{cls}</td>
            <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace; color: #94a3b8;">({cx}, {cy})</td>
            <td style="padding: 8px 12px; font-family: 'JetBrains Mono', monospace; color: #cbd5e1;">{dwell:.1f}s</td>
            <td style="padding: 8px 12px;">
                <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                    ACTIVE
                </span>
            </td>
        </tr>
        """)

    table_html = f"""
    <div style="max-height: 240px; overflow-y: auto; background: rgba(17, 24, 39, 0.6); border: 1px solid #1e293b; border-radius: 10px;">
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="border-bottom: 1px solid #334155; color: #94a3b8; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; background: rgba(15, 23, 42, 0.8);">
                    <th style="padding: 8px 12px;">ID</th>
                    <th style="padding: 8px 12px;">Class</th>
                    <th style="padding: 8px 12px;">Position</th>
                    <th style="padding: 8px 12px;">Dwell Time</th>
                    <th style="padding: 8px 12px;">Status</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)
