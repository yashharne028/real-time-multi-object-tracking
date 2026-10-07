import time
import streamlit as st

class CrowdAlertEngine:
    def __init__(self, alert_limit=15):
        self.alert_limit = alert_limit
        self.alert_history = []  # list of {"timestamp": str, "count": int, "density": str, "level": str}
        self.last_alert_time = 0
        self.cooldown_sec = 4

    def update(self, current_count, current_density, custom_limit=None):
        limit = custom_limit if custom_limit is not None else self.alert_limit
        now = time.time()
        is_alert = False
        alert_level = "NORMAL"
        message = "SYSTEM NORMAL - Crowd density within safe threshold limits."

        if current_count >= limit or current_density == "HIGH":
            is_alert = True
            alert_level = "HIGH_DENSITY"
            message = f"⚠ CRITICAL ALERT: High crowd density detected ({current_count} persons visible, threshold: {limit})."
        elif current_density == "MEDIUM":
            alert_level = "MODERATE"
            message = f"NOTICE: Moderate crowd density observed ({current_count} persons visible)."

        # Record to history if alert and cooled down
        if is_alert and (now - self.last_alert_time >= self.cooldown_sec):
            self.last_alert_time = now
            t_str = time.strftime("%H:%M:%S", time.localtime(now))
            self.alert_history.append({
                "time": t_str,
                "count": current_count,
                "density": current_density,
                "level": alert_level,
                "detail": f"Exceeded threshold ({current_count} >= {limit})"
            })
            if len(self.alert_history) > 20:
                self.alert_history.pop(0)

        return is_alert, alert_level, message


def render_alert_banner(is_alert, alert_level, message):
    """Renders the top live crowd status banner."""
    if is_alert:
        st.markdown(f"""
        <div class="alert-panel alert-danger">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="pulse-dot-red"></div>
                <div>
                    <span style="font-weight: 800; letter-spacing: 0.05em;">⚠ CROWD DENSITY ALERT</span>
                    <div style="font-size: 0.78rem; font-weight: 400; color: #fca5a5; margin-top: 2px;">{message}</div>
                </div>
            </div>
            <div style="font-size: 0.75rem; background: rgba(239, 68, 68, 0.25); padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.5);">
                CRITICAL LIMIT
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif alert_level == "MODERATE":
        st.markdown(f"""
        <div class="alert-panel alert-warning">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="pulse-dot-green" style="background-color: #f59e0b; box-shadow: 0 0 10px #f59e0b;"></div>
                <div>
                    <span style="font-weight: 700;">SYSTEM STATUS: MODERATE DENSITY</span>
                    <div style="font-size: 0.78rem; font-weight: 400; color: #fde68a; margin-top: 2px;">{message}</div>
                </div>
            </div>
            <div style="font-size: 0.75rem; background: rgba(245, 158, 11, 0.2); padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.4);">
                MONITORING
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-panel alert-normal">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="pulse-dot-green"></div>
                <div>
                    <span style="font-weight: 700;">SYSTEM STATUS: NORMAL</span>
                    <div style="font-size: 0.78rem; font-weight: 400; color: #a7f3d0; margin-top: 2px;">{message}</div>
                </div>
            </div>
            <div style="font-size: 0.75rem; background: rgba(16, 185, 129, 0.18); padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.35);">
                ALL CLEAR
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_alert_logs(alert_history):
    """Renders recent alert logs list."""
    if not alert_history:
        st.markdown("""
        <div style="padding: 1rem; background: rgba(15, 23, 42, 0.5); border-radius: 8px; border: 1px solid #1e293b; color: #64748b; font-size: 0.8rem; text-align: center;">
            No threshold breach events recorded in current session.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div style="max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
    """ + "".join([
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 4px; font-size: 0.78rem;">
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; color: #f87171; font-weight: 700;">[{log['time']}]</span>
                <span style="color: #cbd5e1; margin-left: 6px;">Crowd: <b>{log['count']}</b> ({log['density']})</span>
            </div>
            <span style="color: #94a3b8; font-size: 0.72rem;">{log['detail']}</span>
        </div>
        """ for log in reversed(alert_history[-6:])
    ]) + "</div>", unsafe_allow_html=True)
