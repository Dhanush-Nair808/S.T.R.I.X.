
import os
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

from styles import apply_styles


                                                              
               
                                                              

API_BASE = os.getenv(
    "STRIX_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


                                                              
                    
                                                              

ICON_PATH = "D:/Major Project/strix/app/dashboard/strix-icon.png"

st.set_page_config(
    page_title="STRIX",
    page_icon=str(ICON_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


                                                              
         
                                                              

def api_get(path, timeout=2):

    try:

        response = requests.get(
            f"{API_BASE}{path}",
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:

        return None


def api_image(path, timeout=3):

    try:

        response = requests.get(
            f"{API_BASE}{path}",
            timeout=timeout,
        )

        if response.status_code == 200:
            return response.content

    except requests.RequestException:
        pass

    return None


def fmt_date(value):

    if not value:
        return "—"

    try:

        return datetime.fromisoformat(
            value
        ).strftime(
            "%d %b %Y  %H:%M:%S"
        )

    except Exception:

        return value


def level_class(level):

    level = (
        level or "PENDING"
    ).upper()

    mapping = {
        "HIGH": "level-high",
        "MEDIUM": "level-medium",
        "LOW": "level-low",
        "FALSE ALARM": "level-false",
    }

    return mapping.get(
        level,
        "level-false",
    )


def html(content):

    st.html(content)


                                                              
               
                                                              

if "page" not in st.session_state:

    st.session_state.page = "Home"


                                                              
         
                                                              

with st.sidebar:

    html(
        """
        <div class="brand">
            <div class="brand-name">STRIX</div>
            <div class="brand-subtitle">
                THREAT DETECTION SYSTEM
            </div>
        </div>
        """
    )

    html(
        '<div class="sidebar-rule"></div>'
    )

    navigation = [
        ("HOME", "Home"),
        ("EVENTS", "Events"),
        ("MAILS", "Mails"),
        ("CONTROL PANEL", "Control Panel"),
    ]

    for label, page in navigation:

        active = (
            st.session_state.page == page
        )

        button_class = (
            "nav-active"
            if active
            else "nav-button"
        )

        html(
            f"""
            <div class="{button_class}">
                {label}
            </div>
            """
        )

        if st.button(
            " ",
            key=f"nav_{page}",
            use_container_width=True,
        ):

            st.session_state.page = page
            st.rerun()

    html(
        '<div class="sidebar-rule"></div>'
    )

    health = api_get(
        "/api/health",
        timeout=1,
    )

    operational = (
        health is not None
        and health.get("status")
        == "operational"
    )

    


                                                              
           
                                                              

@st.fragment(run_every=0.5)
def live_feed():

    html(
        """
        <div class="section-head">
            <div class="section-name">
                LIVE FEED
            </div>

            <div class="live-state">
                <span class="live-dot"></span>
                LIVE
            </div>
        </div>
        """
    )

                                                              
    timestamp = int(
        time.time() * 1000
    )

    try:

        response = requests.get(
            f"{API_BASE}/api/live-feed"
            f"?t={timestamp}",
            timeout=2,
        )

        if response.status_code == 200:

            st.image(
                response.content,
                use_container_width=True,
            )

        else:

            html(
                """
                <div class="feed-placeholder">
                    <div class="feed-placeholder-title">
                        CAMERA OFFLINE
                    </div>

                    <div class="feed-placeholder-text">
                        Waiting for the STRIX camera process.
                    </div>
                </div>
                """
            )

    except requests.RequestException:

        html(
            """
            <div class="feed-placeholder">
                <div class="feed-placeholder-title">
                    CAMERA OFFLINE
                </div>

                <div class="feed-placeholder-text">
                    Waiting for the STRIX camera process.
                </div>
            </div>
            """
        )


                                                              
      
                                                              

def render_home():

    html(
        """
        <div class="page-kicker">
            SECURITY OPERATIONS
        </div>

        <div class="page-title">
            D A S H B O A R D
        </div>

        <div class="page-description">
            Real-time threat detection and event monitoring.
        </div>
        """
    )

    stats = api_get(
        "/api/stats"
    ) or {}

    metrics = [
        (
            "TOTAL EVENTS",
            stats.get(
                "total_events",
                0,
            ),
        ),
        (
            "HIGH THREATS",
            stats.get(
                "high",
                0,
            ),
        ),
        (
            "MEDIUM",
            stats.get(
                "medium",
                0,
            ),
        ),
        (
            "LOW",
            stats.get(
                "low",
                0,
            ),
        ),
        (
            "FALSE ALARMS",
            stats.get(
                "false_alarm",
                0,
            ),
        ),
    ]

    columns = st.columns(
        5,
        gap="small",
    )

    for column, (
        label,
        value,
    ) in zip(
        columns,
        metrics,
    ):

        with column:

            html(
                f"""
                <div class="metric">
                    <div class="metric-label">
                        {label}
                    </div>

                    <div class="metric-value">
                        {value}
                    </div>
                </div>
                """
            )

    html(
        '<div class="vertical-space"></div>'
    )

    left, right = st.columns(
        [1.7, 1],
        gap="large",
    )

    with left:

        live_feed()

    with right:

        html(
            """
            <div class="section-head">
                <div class="section-name">
                    RECENT EVENTS
                </div>
            </div>
            """
        )

        data = api_get(
            "/api/events?limit=6"
        )

        events = (
            data.get(
                "events",
                [],
            )
            if data
            else []
        )

        if not events:

            html(
                """
                <div class="empty-state">
                    NO RECORDED EVENTS
                </div>
                """
            )

        else:

            for event in events:

                event_id = event.get(
                    "event_id",
                    "UNKNOWN",
                )

                level = (
                    event.get(
                        "mistral_level"
                    )
                    or "PENDING"
                )

                html(
                    f"""
                    <div class="event-row">

                        <div class="event-row-top">

                            <span class="event-row-id">
                                {event_id}
                            </span>

                            <span class="{level_class(level)}">
                                {level.upper()}
                            </span>

                        </div>

                        <div class="event-row-time">
                            {fmt_date(
                                event.get(
                                    "started_at"
                                )
                            )}
                        </div>

                    </div>
                    """
                )

    html(
        '<div class="vertical-space-large"></div>'
    )

    html(
        """
        <div class="section-head">
            <div class="section-name">
                EVENT SNAPSHOTS
            </div>

            <div class="section-note">
                RECENT EVIDENCE
            </div>
        </div>
        """
    )

    snapshot_data = api_get(
        "/api/events?limit=6"
    )

    snapshots = (
        snapshot_data.get(
            "events",
            [],
        )
        if snapshot_data
        else []
    )

    snapshots = [
        event
        for event in snapshots
        if event.get(
            "snapshot_path"
        )
    ][:3]

    if not snapshots:

        html(
            """
            <div class="empty-state">
                NO EVENT SNAPSHOTS AVAILABLE
            </div>
            """
        )

    else:

        snapshot_columns = st.columns(
            len(snapshots),
            gap="medium",
        )

        for column, event in zip(
            snapshot_columns,
            snapshots,
        ):

            with column:

                image = api_image(
                    f"/api/events/"
                    f"{event['event_id']}"
                    f"/snapshot",
                    timeout=3,
                )

                if image is not None:

                    st.image(
                        image,
                        use_container_width=True,
                    )

                    level = (
                        event.get(
                            "mistral_level"
                        )
                        or "PENDING"
                    )

                    html(
                        f"""
                        <div class="snapshot-caption">

                            <div class="snapshot-id">
                                {event["event_id"]}
                            </div>

                            <div class="{level_class(level)}">
                                {level.upper()}
                            </div>

                            <div class="snapshot-time">
                                {fmt_date(
                                    event.get(
                                        "started_at"
                                    )
                                )}
                            </div>

                        </div>
                        """
                    )

                else:

                    html(
                        """
                        <div class="snapshot-missing">
                            SNAPSHOT UNAVAILABLE
                        </div>
                        """
                    )


                                                              
        
                                                              

def render_events():

    html(
        """
        <div class="page-kicker">
            EVENT MANAGEMENT
        </div>

        <div class="page-title">
            Events
        </div>

        <div class="page-description">
            Recorded detection and verification events.
        </div>
        """
    )

    data = api_get(
        "/api/events?limit=200"
    )

    events = (
        data.get(
            "events",
            [],
        )
        if data
        else []
    )

    if not events:

        html(
            """
            <div class="empty-state">
                NO EVENTS RECORDED
            </div>
            """
        )

        return

    rows = []

    for event in events:

        rows.append(
            {
                "Event ID": event.get(
                    "event_id",
                    "—",
                ),
                "Started": fmt_date(
                    event.get(
                        "started_at"
                    )
                ),
                "Ended": fmt_date(
                    event.get(
                        "ended_at"
                    )
                ),
                "Level": (
                    event.get(
                        "mistral_level"
                    )
                    or "PENDING"
                ),
                "Status": event.get(
                    "status",
                    "—",
                ),
                "Email": (
                    "Sent"
                    if event.get(
                        "email_sent"
                    )
                    else "Not sent"
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


                                                              
       
                                                              

def render_mails():

    html(
        """
        <div class="page-kicker">
            ALERT MANAGEMENT
        </div>

        <div class="page-title">
            Mails
        </div>

        <div class="page-description">
            Threat notification and alert delivery history.
        </div>
        """
    )

    data = api_get(
        "/api/events?limit=200"
    )

    events = (
        data.get(
            "events",
            [],
        )
        if data
        else []
    )

    mailed = [
        event
        for event in events
        if event.get(
            "email_sent"
        )
    ]

    if not mailed:

        html(
            """
            <div class="empty-state">
                NO ALERT EMAILS HAVE BEEN SENT
            </div>
            """
        )

        return

    rows = []

    for event in mailed:

        rows.append(
            {
                "Event ID": event.get(
                    "event_id",
                    "—",
                ),
                "Threat Level": (
                    event.get(
                        "mistral_level"
                    )
                    or "UNKNOWN"
                ),
                "Sent": "Yes",
                "Time": fmt_date(
                    event.get(
                        "started_at"
                    )
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


                                                              
               
                                                              

def render_control_panel():

    html(
        """
        <div class="page-kicker">
            SYSTEM CONTROL
        </div>

        <div class="page-title">
            Control Panel
        </div>

        <div class="page-description">
            Operational controls and unit management.
        </div>

        <div class="control-panel">
            <div class="control-title">
                OPERATIONAL CONTROL
            </div>

            <div class="control-text">
                Control functions are reserved for the
                operational control layer.
            </div>
        </div>
        """
    )


                                                              
        
                                                              

if st.session_state.page == "Home":

    render_home()

elif st.session_state.page == "Events":

    render_events()

elif st.session_state.page == "Mails":

    render_mails()

elif st.session_state.page == "Control Panel":

    render_control_panel()
