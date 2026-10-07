import plotly.graph_objects as go
import streamlit as st

def get_dark_layout(title="", y_title=""):
    """Returns a unified enterprise dark mode layout for Plotly figures."""
    return go.Layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family="Inter, sans-serif", size=14, color="#f1f5f9"),
            x=0.02,
            y=0.95
        ),
        paper_bgcolor="rgba(17, 24, 39, 0.7)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=11),
        margin=dict(l=45, r=25, t=45, b=35),
        height=260,
        xaxis=dict(
            showgrid=True,
            gridcolor="#1e293b",
            zeroline=False,
            showline=True,
            linecolor="#334155",
            tickfont=dict(color="#64748b", size=10)
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=11, color="#94a3b8")),
            showgrid=True,
            gridcolor="#1e293b",
            zeroline=False,
            showline=True,
            linecolor="#334155",
            tickfont=dict(color="#64748b", size=10)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)"
        )
    )


def render_people_count_chart(timestamps, counts, alert_threshold=15):
    """Renders real-time people count area chart."""
    if not timestamps or not counts:
        fig = go.Figure(layout=get_dark_layout("PEOPLE COUNT OVER TIME", "People Count"))
        fig.add_annotation(
            text="Awaiting live detection telemetry...",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748b", size=12)
        )
        return fig

    fig = go.Figure(layout=get_dark_layout("PEOPLE COUNT OVER TIME", "Persons"))
    
    # Area curve
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=counts,
        mode="lines",
        name="Tracked People",
        line=dict(color="#38bdf8", width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(56, 189, 248, 0.12)"
    ))

    # Alert threshold reference line
    fig.add_hline(
        y=alert_threshold,
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.5,
        annotation_text=f"Alert Limit ({alert_threshold})",
        annotation_position="top right",
        annotation_font=dict(color="#f87171", size=10)
    )

    return fig


def render_density_chart(timestamps, densities):
    """Renders crowd density level progression over time."""
    if not timestamps or not densities:
        fig = go.Figure(layout=get_dark_layout("CROWD DENSITY OVER TIME", "Density State"))
        fig.add_annotation(
            text="Awaiting density telemetry...",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748b", size=12)
        )
        return fig

    # Map density labels to numerical scale for plotting
    density_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    numeric_densities = [density_map.get(d, 1) for d in densities]

    fig = go.Figure(layout=get_dark_layout("CROWD DENSITY OVER TIME", "Density Level"))
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=numeric_densities,
        mode="lines+markers",
        name="Density Level",
        line=dict(color="#f59e0b", width=2, shape="hv"),
        marker=dict(size=4, color="#fbbf24")
    ))

    fig.update_layout(
        yaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3],
            ticktext=["LOW", "MEDIUM", "HIGH"],
            range=[0.5, 3.5]
        )
    )

    return fig


def render_fps_chart(timestamps, fps_values):
    """Renders processing FPS performance chart."""
    if not timestamps or not fps_values:
        fig = go.Figure(layout=get_dark_layout("PROCESSING FPS OVER TIME", "Frames / Sec"))
        fig.add_annotation(
            text="Awaiting FPS telemetry...",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748b", size=12)
        )
        return fig

    fig = go.Figure(layout=get_dark_layout("PROCESSING FPS OVER TIME", "FPS"))
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=fps_values,
        mode="lines",
        name="Inference FPS",
        line=dict(color="#10b981", width=2),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.08)"
    ))

    return fig


def render_entry_exit_chart(timestamps, entry_series, exit_series):
    """Renders cumulative Entry vs Exit flow comparison."""
    if not timestamps or not entry_series:
        fig = go.Figure(layout=get_dark_layout("ENTRY / EXIT FLOW OVER TIME", "Cumulative Count"))
        fig.add_annotation(
            text="Awaiting tripwire flow data...",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748b", size=12)
        )
        return fig

    fig = go.Figure(layout=get_dark_layout("ENTRY / EXIT FLOW OVER TIME", "Cumulative"))
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=entry_series,
        mode="lines",
        name="Total Entered",
        line=dict(color="#34d399", width=2.2)
    ))

    fig.add_trace(go.Scatter(
        x=timestamps,
        y=exit_series,
        mode="lines",
        name="Total Exited",
        line=dict(color="#f87171", width=2.2)
    ))

    return fig
