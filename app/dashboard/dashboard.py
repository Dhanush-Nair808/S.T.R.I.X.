import os
import time
import math
from datetime import datetime
from html import escape as escape_html
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from app.dashboard.styles import apply_styles
except ImportError:
    from styles import apply_styles


# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------

API_BASE = os.getenv(
    "STRIX_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ----------------------------------------------------------------------
# PAGE SETUP
# ----------------------------------------------------------------------

ICON_PATH = str(Path(__file__).resolve().parent / "strix-icon.png")

st.set_page_config(
    page_title="STRIX",
    page_icon=str(ICON_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()

INTERACTIONS_JS = (
    Path(__file__).resolve().parent / "interactions.js"
).read_text(encoding="utf-8")
st.html(
    f"<script>{INTERACTIONS_JS}</script>",
    unsafe_allow_javascript=True,
)


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# SESSION
# ----------------------------------------------------------------------

if "page" not in st.session_state:

    st.session_state.page = "Home"


# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------

with st.sidebar:

    html(
        """
        <div class="brand">
            <div class="brand-name">STRIX</div>
            <div class="brand-subtitle">THREAT DETECTION SYSTEM</div>
        </div>
        """
    )

    html('<div class="sidebar-rule"></div>')

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
            <div class="{button_class}">{label}</div>
            """
        )

        if st.button(
            " ",
            key=f"nav_{page}",
            use_container_width=True,
        ):

            st.session_state.page = page
            st.rerun()

    health = api_get(
        "/api/health",
        timeout=1,
    )

    operational = (
        health is not None
        and health.get("status")
        == "operational"
    )

    html(
        f"""
        <div class="system-state">
            <div class="system-label">SYSTEM STATUS</div>
            <div class="system-value">
                <span class="state-dot {'online' if operational else 'offline'}"></span>
                {'OPERATIONAL' if operational else 'OFFLINE'}
            </div>
        </div>
        """
    )


# ----------------------------------------------------------------------
# LIVE FEED
# ----------------------------------------------------------------------

@st.fragment(run_every=0.5)
def live_feed():

    html(
        """
        <div class="section-head">
            <div class="section-name">Live feed</div>

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
                    <div class="feed-placeholder-title">CAMERA OFFLINE</div>
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
                <div class="feed-placeholder-title">CAMERA OFFLINE</div>
                <div class="feed-placeholder-text">
                    Waiting for the STRIX camera process.
                </div>
            </div>
            """
        )


# ----------------------------------------------------------------------
# HOME
# ----------------------------------------------------------------------

def render_home():

    html(
        """
        <div class="page-kicker">SECURITY OPERATIONS</div>
        <div class="page-title">Dashboard</div>
        <div class="page-description">
            Real-time threat detection and event monitoring.
        </div>
        """
    )

    stats = api_get(
        "/api/stats"
    )
    stats_available = stats is not None
    if not stats_available:
        st.error("Backend API is unavailable. Start the API on port 8000 and refresh.")
        stats = {}

    metrics = [
        ("TOTAL EVENTS", stats.get("total_events", 0 if stats_available else "—")),
        ("HIGH THREATS", stats.get("high", 0 if stats_available else "—")),
        ("MEDIUM", stats.get("medium", 0 if stats_available else "—")),
        ("LOW", stats.get("low", 0 if stats_available else "—")),
        ("FALSE ALARMS", stats.get("false_alarm", 0 if stats_available else "—")),
    ]

    columns = st.columns(
        5,
        gap="small",
    )

    for column, (label, value) in zip(columns, metrics):

        with column:

            html(
                f"""
                <div class="metric">
                    <div class="metric-label">{escape_html(str(label))}</div>
                    <div class="metric-value">{escape_html(str(value))}</div>
                </div>
                """
            )

    html('<div class="vertical-space"></div>')

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
                <div class="section-name">Recent events</div>
            </div>
            """
        )

        data = api_get(
            "/api/events?limit=6"
        )

        events = (
            data.get("events", [])
            if data
            else []
        )

        if not events:

            html(
                """
                <div class="empty-state">NO RECORDED EVENTS</div>
                """
            )

        else:

            rows = []

            for event in events:

                event_id = event.get(
                    "event_id",
                    "UNKNOWN",
                )

                level = (
                    event.get("mistral_level")
                    or "PENDING"
                )

                rows.append(
                    f"""
                    <div class="event-row">
                        <div class="event-row-top">
                            <span class="event-row-id">{escape_html(str(event_id))}</span>
                            <span class="{level_class(level)}">{escape_html(level.upper())}</span>
                        </div>
                        <div class="event-row-time">
                            {escape_html(str(fmt_date(event.get("started_at"))))}
                        </div>
                    </div>
                    """
                )

            html(
                f'<div class="event-list">{"".join(rows)}</div>'
            )

    html('<div class="vertical-space-large"></div>')

    html(
        """
        <div class="section-head">
            <div class="section-name">Event snapshots</div>
            <div class="section-note">Recent evidence</div>
        </div>
        """
    )

    snapshot_data = api_get(
        "/api/events?limit=6"
    )

    snapshots = (
        snapshot_data.get("events", [])
        if snapshot_data
        else []
    )

    snapshots = [
        event
        for event in snapshots
        if event.get("snapshot_path")
    ][:3]

    if not snapshots:

        html(
            """
            <div class="empty-state">NO EVENT SNAPSHOTS AVAILABLE</div>
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
                        event.get("mistral_level")
                        or "PENDING"
                    )

                    html(
                        f"""
                        <div class="snapshot-caption">
                            <div class="snapshot-id">{escape_html(str(event["event_id"]))}</div>
                            <div class="{level_class(level)}">{escape_html(level.upper())}</div>
                            <div class="snapshot-time">
                                {escape_html(str(fmt_date(event.get("started_at"))))}
                            </div>
                        </div>
                        """
                    )

                else:

                    html(
                        """
                        <div class="snapshot-missing">SNAPSHOT UNAVAILABLE</div>
                        """
                    )


# ----------------------------------------------------------------------
# EVENTS
# ----------------------------------------------------------------------

def render_events():

    html(
        """
        <div class="page-kicker">EVENT MANAGEMENT</div>
        <div class="page-title">Events</div>
        <div class="page-description">
            Recorded detection and verification events.
        </div>
        """
    )

    data = api_get(
        "/api/events?limit=200"
    )

    events = (
        data.get("events", [])
        if data
        else []
    )

    if data is None:
        st.error("Event records are unavailable because the backend API is not reachable.")
        return

    if not events:

        html(
            """
            <div class="empty-state">NO EVENTS RECORDED</div>
            """
        )

        return

    deletion_result = st.session_state.pop("event_deletion_result", None)
    if deletion_result:
        st.success(deletion_result)

    event_ids = [event.get("event_id") for event in events if event.get("event_id")]
    event_lookup = {event.get("event_id"): event for event in events}
    with st.expander("EVENT RECORD MANAGEMENT", expanded=False):
        selected_event_ids = st.multiselect(
            "Select event records",
            event_ids,
            format_func=lambda event_id: (
                f"{event_id}  |  "
                f"{(event_lookup[event_id].get('mistral_level') or 'PENDING').upper()}  |  "
                f"{fmt_date(event_lookup[event_id].get('started_at'))}"
            ),
            key="events_to_delete",
        )
        confirm_delete = st.checkbox(
            "I understand this permanently deletes the selected event records and evidence files."
        )
        delete_submitted = st.button(
            "Delete selected events",
            disabled=not selected_event_ids,
            key="delete_selected_events_button",
        )

        if delete_submitted:
            if not confirm_delete:
                st.error("Confirm permanent deletion before proceeding.")
            else:
                deleted_ids = []
                failed_details = []
                for event_id in selected_event_ids:
                    try:
                        response = requests.delete(
                            f"{API_BASE}/api/events/{event_id}",
                            json={"confirm": True},
                            timeout=10,
                        )
                        if response.ok:
                            deleted_ids.append(event_id)
                        else:
                            try:
                                detail = response.json().get("detail", response.text)
                            except ValueError:
                                detail = response.text
                            failed_details.append(f"{event_id}: {detail}")
                    except requests.RequestException as exc:
                        failed_details.append(f"{event_id}: {exc}")

                result = []
                if deleted_ids:
                    result.append(f"Deleted {len(deleted_ids)} event record(s).")
                if failed_details:
                    result.append("Could not delete: " + "; ".join(failed_details))
                st.session_state.event_deletion_result = " ".join(result)
                st.rerun()

    for index, event in enumerate(events):
        snapshot_path = event.get("snapshot_path") or ""
        event_id = event.get("event_id", "UNKNOWN EVENT")
        level = (event.get("mistral_level") or "PENDING").upper()
        inference = event.get("mistral_reasoning") or "Awaiting LLM verification."
        details = [
            ("STARTED", fmt_date(event.get("started_at"))),
            ("ENDED", fmt_date(event.get("ended_at"))),
            ("STATUS", event.get("status") or "—"),
            ("IMAGE FILE", os.path.basename(snapshot_path) if snapshot_path else "NOT RECORDED"),
            ("IMAGE PATH", snapshot_path or "—"),
            ("EMAIL", "SENT" if event.get("email_sent") else "NOT SENT"),
        ]
        detail_rows = "".join(
            f"<tr><th>{escape_html(label)}</th><td>{escape_html(str(value))}</td></tr>"
            for label, value in details
        )

        with st.container(border=True, key=f"card_event_{event_id}"):
            record_col, image_col = st.columns([1.05, 1.2], gap="large")
            with record_col:
                html(
                    f"""
                    <div class="event-record-heading">
                        <div>
                            <div class="event-record-kicker">EVENT RECORD</div>
                            <div class="event-record-id">{escape_html(event_id)}</div>
                        </div>
                        <span class="{level_class(level)}">{escape_html(level)}</span>
                    </div>
                    <table class="event-record-table"><tbody>{detail_rows}</tbody></table>
                    <div class="event-inference">
                        <div class="event-inference-title">LLM INFERENCE</div>
                        <div class="event-inference-text">{escape_html(str(inference))}</div>
                    </div>
                    """
                )

            with image_col:
                if snapshot_path:
                    image = api_image(f"/api/events/{event_id}/snapshot", timeout=5)
                    if image is not None:
                        st.image(image, use_container_width=True)
                    else:
                        html('<div class="snapshot-missing">IMAGE FILE UNAVAILABLE</div>')
                else:
                    html('<div class="snapshot-missing">NO EVENT IMAGE RECORDED</div>')


# ----------------------------------------------------------------------
# MAILS
# ----------------------------------------------------------------------

def render_mails():

    html(
        """
        <div class="page-kicker">ALERT MANAGEMENT</div>
        <div class="page-title">Mails</div>
        <div class="page-description">
            Threat notification and alert delivery history.
        </div>
        """
    )

    data = api_get(
        "/api/events?limit=200"
    )

    events = (
        data.get("events", [])
        if data
        else []
    )

    mailed = [
        event
        for event in events
        if event.get("email_sent")
    ]

    if not mailed:

        html(
            """
            <div class="empty-state">NO ALERT EMAILS HAVE BEEN SENT</div>
            """
        )

        return

    mail_rows = []
    for event in mailed:
        level = (event.get("mistral_level") or "UNKNOWN").upper()
        mail_rows.append(
            "<tr>"
            f"<td>{escape_html(str(event.get('event_id') or '—'))}</td>"
            f"<td><span class='{level_class(level)}'>{escape_html(level)}</span></td>"
            "<td>DELIVERED</td>"
            f"<td>{escape_html(fmt_date(event.get('started_at')))}</td>"
            "</tr>"
        )

    html(
        "<div class='mail-table-wrap'><table class='mail-table'>"
        "<thead><tr><th>EVENT ID</th><th>THREAT LEVEL</th><th>SENT</th><th>TIME</th></tr></thead>"
        f"<tbody>{''.join(mail_rows)}</tbody></table></div>"
    )


# ----------------------------------------------------------------------
# CONTROL PANEL
# ----------------------------------------------------------------------

def render_control_panel():

    html(
        """
        <div class="page-kicker">SYSTEM CONTROL</div>
        <div class="page-title">Control Panel</div>
        <div class="page-description">
            Assign active threats to operational units and dispatch via the preferred contact channel.
        </div>
        """
    )

    units_data = api_get("/api/units") or {}
    units = units_data.get("units", [])

    events_data = api_get("/api/events?limit=200") or {}
    events = events_data.get("events", [])
    assignment_data = api_get("/api/unit-assignments") or {}
    assignments = assignment_data.get("assignments", [])

    camera_data = api_get("/api/settings/camera") or {}
    camera_zone = camera_data.get("zone", "Camera")
    camera_x = float(camera_data.get("x", 50))
    camera_y = float(camera_data.get("y", 50))

    unit_lookup = {unit["id"]: unit for unit in units}
    latest_event_options = [event.get("event_id", "manual-assign") for event in events]
    if not latest_event_options:
        latest_event_options = ["manual-assign"]
    event_lookup = {event.get("event_id"): event for event in events}
    event_labels = {
        event_id: (
            f"{event_id}  |  "
            f"{os.path.basename(event_lookup[event_id].get('snapshot_path') or '') or 'IMAGE PENDING'}"
        )
        for event_id in latest_event_options
        if event_id in event_lookup
    }

    assignment_map = {}
    for assignment in assignments:
        assignment_map.setdefault(assignment.get("unit_id"), assignment)

    selected_event = None

    
    left, evidence_column, right = st.columns(
        [1.0, 1.0, 1.2],
        gap="small",
    )
    


    # Left column: event picker and dispatch form
    with left:
        html(
            """
            <div class="section-head">
                <div class="section-name">Dispatch form</div>
            </div>
            """
        )

        if not units:
            html('<div class="empty-state">NO UNITS AVAILABLE</div>')
        else:
            if st.session_state.get("dispatch_event_id") not in latest_event_options:
                st.session_state.dispatch_event_id = latest_event_options[0]

            event_id = st.selectbox(
                "Event / evidence",
                latest_event_options,
                format_func=lambda value: event_labels.get(value, value),
                key="dispatch_event_id",
            )
            selected_event = event_lookup.get(event_id)

            with st.form("unit_dispatch"):
                available_unit_names = [unit["name"] for unit in units]
                if st.session_state.get("dispatch_unit_name") not in available_unit_names:
                    st.session_state.dispatch_unit_name = units[0]["name"]
                if "dispatch_threat_level" not in st.session_state:
                    st.session_state.dispatch_threat_level = "HIGH"
                if "dispatch_channel" not in st.session_state:
                    st.session_state.dispatch_channel = "email"
                if "dispatch_priority" not in st.session_state:
                    st.session_state.dispatch_priority = "immediate"
                if "dispatch_note" not in st.session_state:
                    st.session_state.dispatch_note = "Threat requires immediate review and leader acknowledgement."

                unit_col, level_col = st.columns(2)
                with unit_col:
                    unit_name = st.selectbox("Assigned unit", [unit["name"] for unit in units], key="dispatch_unit_name")
                with level_col:
                    threat_level = st.selectbox("Threat level", ["HIGH", "MEDIUM", "LOW", "FALSE ALARM"], key="dispatch_threat_level")
                selected_unit = next(unit for unit in units if unit["name"] == unit_name)
                channel_col, priority_col = st.columns(2)
                with channel_col:
                    channel = st.selectbox("Channel", ["email", "sms", "whatsapp"], key="dispatch_channel")
                with priority_col:
                    priority = st.selectbox("Priority", ["immediate", "priority", "routine"], key="dispatch_priority")

                default_message = (
                    f"Threat level {threat_level} assigned to {selected_unit['name']}. "
                    f"Confirm deployment and alert the leader immediately."
                )
                note = st.text_area(
                    "Operational note",
                    key="dispatch_note",
                    value=st.session_state.get("dispatch_note", "Threat requires immediate review and leader acknowledgement."),
                )
                message = st.text_area(
                    "Dispatch message",
                    key="dispatch_message",
                    value=st.session_state.get("dispatch_message", default_message),
                    placeholder=default_message,
                )

                submitted = st.form_submit_button("Assign threat to unit", use_container_width=True)

                if submitted:
                    dispatch_message = (message or "").strip() or default_message
                    payload = {
                        "event_id": event_id,
                        "unit_id": selected_unit["id"],
                        "threat_level": threat_level,
                        "channel": channel,
                        "priority": priority,
                        "note": note,
                        "message": dispatch_message,
                    }
                    response = requests.post(f"{API_BASE}/api/assign-threat", json=payload, timeout=10)
                    if response.ok:
                        data = response.json()
                        st.success(f"Dispatch queued: {data.get('dispatch', {}).get('detail', 'sent')}")
                        st.rerun()
                    else:
                        st.error(f"Dispatch failed: {response.text}")

    # Evidence stays beside the dispatch controls and updates with the event picker.
    with evidence_column:
        html(
            """
            <div class="section-head">
                <div class="section-name">Selected event</div>
            </div>
            """
        )
        with st.container(border=True, key="card_evidence"):
            if selected_event and selected_event.get("snapshot_path"):
                html('<div class="form-evidence-label">EVENT EVIDENCE</div>')
                evidence_details = [
                    ("EVENT ID", selected_event.get("event_id") or "—"),
                    ("IMAGE FILE", os.path.basename(selected_event.get("snapshot_path") or "") or "—"),
                    ("THREAT", (selected_event.get("mistral_level") or "PENDING").upper()),
                    ("STATUS", selected_event.get("status") or "—"),
                ]
                evidence_html = "".join(
                    f"<div class='evidence-field'><span>{escape_html(label)}</span><strong>{escape_html(str(value))}</strong></div>"
                    for label, value in evidence_details
                )
                html(f"<div class='selected-event-fields'>{evidence_html}</div>")
                image = api_image(f"/api/events/{selected_event['event_id']}/snapshot", timeout=5)
                if image is not None:
                    st.image(image, use_container_width=True)
                else:
                    html('<div class="snapshot-missing">IMAGE FILE UNAVAILABLE</div>')
            else:
                html('<div class="snapshot-missing">NO EVENT IMAGE RECORDED</div>')

    # Map stays in its own column rather than pushing evidence below it.
    with right:
        html(
            """
            <div class="section-head">
                <div class="section-name">Unit map</div>
            </div>
            """
        )

        if not units:
            html('<div class="empty-state">NO UNITS AVAILABLE</div>')
        else:
            map_positions = []
            for unit in units:
                map_x = max(23.0, min(77.0, float(unit.get("x", 50))))
                map_y = max(22.0, min(78.0, float(unit.get("y", 50))))
                map_positions.append((unit, map_x, map_y))

            map_height = max(
                560,
                math.ceil(
                    len(units)
                    / min(4, max(2, math.ceil(math.sqrt(len(units) * 0.75))))
                )
                * 190,
            )
            route_lines = "".join(
                f"<line data-unit-id='{unit['id']}' x1='{camera_x:g}' y1='{camera_y:g}' x2='{map_x:g}' y2='{map_y:g}' />"
                for unit, map_x, map_y in map_positions
            )
            camera_label = escape_html(camera_zone)
            map_html = [
                f"<div class='unit-map' style='height:{map_height}px; min-height:{map_height}px;'>",
                "<div class='map-topline'><span>UNIT DEPLOYMENT</span><span class='map-selection'>ALL UNITS / ACTIVE ROSTER</span></div>",
                f"<svg class='map-routes' viewBox='0 0 100 100' preserveAspectRatio='none' aria-hidden='true'>"
                f"<circle cx='{camera_x:g}' cy='{camera_y:g}' r='1.5' />"
                f"{route_lines}"
                f"</svg>",
                f"<div class='camera-marker' style='left:{camera_x:g}%; top:{camera_y:g}%;' title='{camera_label}'>"
                f"<div class='camera-dot'></div>"
                f"<div class='camera-label'>{camera_label}</div>"
                f"</div>",
            ]
            for unit, map_x, map_y in map_positions:
                assignment = assignment_map.get(unit["id"])
                badge = assignment.get("threat_level", "IDLE") if assignment else "IDLE"
                status = assignment.get("status", "idle").upper() if assignment else "IDLE"
                status_key = status.lower().replace(" ", "-")
                state = f"unit-card status-{status_key}"
                badge_class = level_class(badge) if assignment else "idle"
                map_html.append(
                    f"<div class='{state}' data-unit-id='{unit['id']}' data-status='{escape_html(status)}' data-threat='{escape_html(str(badge))}' style='left:{map_x:g}%; top:{map_y:g}%;' tabindex='0' role='button' aria-pressed='false'>"
                    f"<div class='unit-name'>{escape_html(str(unit['name']))}</div>"
                    f"<div class='unit-leader'>{escape_html(str(unit['leader_name']))}</div>"
                    f"<div class='unit-badge {badge_class}'>{escape_html(str(badge))}</div>"
                    f"<div class='unit-zone'>{escape_html(str(unit['zone']))} / {escape_html(status)}</div>"
                    f"</div>"
                )
            map_html.append(
                "<div class='map-legend'><span><i class='map-key unit-key'></i>UNIT</span>"
                "<span><i class='map-key link-key'></i>COMMAND LINK</span></div>"
            )
            map_html.append("</div>")
            map_markup = "".join(map_html)
            interactions_js = (Path(__file__).resolve().parent / "interactions.js").read_text(encoding="utf-8")
            component_html = (
                "<!doctype html><html><head><meta charset='utf-8'></head><body>"
                f"{map_markup}<script>{interactions_js}</script>"
                "</body></html>"
            )
            components.html(component_html, height=map_height + 2, scrolling=False)

    # ------------------------------------------------------------------
    # Camera / threat-origin location config
    # ------------------------------------------------------------------
    

    with st.expander("UNIT ROSTER / CONTACTS", expanded=False):
        st.caption("Add units with a dispatch contact, or remove units that have no active assignment records.")
        with st.form("add_unit_form", clear_on_submit=True):
            identity_cols = st.columns(3)
            with identity_cols[0]:
                new_unit_name = st.text_input("Unit name", max_chars=50)
            with identity_cols[1]:
                new_unit_leader = st.text_input("Unit leader", max_chars=100)
            with identity_cols[2]:
                new_unit_zone = st.text_input("Operating zone", max_chars=100)

            contact_cols = st.columns(3)
            with contact_cols[0]:
                new_unit_email = st.text_input("Email address", max_chars=200)
            with contact_cols[1]:
                new_unit_phone = st.text_input("Phone number", max_chars=50)
            with contact_cols[2]:
                new_unit_whatsapp = st.text_input("WhatsApp number", max_chars=50)

            add_unit_submitted = st.form_submit_button("Add unit", use_container_width=True)
            if add_unit_submitted:
                if not any((value or "").strip() for value in (new_unit_email, new_unit_phone, new_unit_whatsapp)):
                    st.error("Provide an email address or phone number.")
                elif not new_unit_name.strip():
                    st.error("Enter a unit name.")
                else:
                    unit_response = requests.post(
                        f"{API_BASE}/api/units",
                        json={
                            "name": new_unit_name.strip(),
                            "leader_name": new_unit_leader.strip() or "Unit Lead",
                            "zone": new_unit_zone.strip() or "Unassigned",
                            "email": new_unit_email.strip() or None,
                            "phone": new_unit_phone.strip() or None,
                            "whatsapp": new_unit_whatsapp.strip() or None,
                        },
                        timeout=10,
                    )
                    if unit_response.ok:
                        st.success(f"Unit {new_unit_name.strip()} added to the roster.")
                        st.rerun()
                    else:
                        detail = unit_response.json().get("detail", unit_response.text)
                        st.error(str(detail))

        # ---- Edit existing unit ----------------------------------------
        if units:
            st.divider()
            st.caption("Edit an existing unit's zone, leader, or contact details.")
            edit_unit_ids = [unit["id"] for unit in units]
            if st.session_state.get("edit_unit_id") not in edit_unit_ids:
                st.session_state.edit_unit_id = edit_unit_ids[0]
            edit_unit_id = st.selectbox(
                "Select unit to edit",
                edit_unit_ids,
                format_func=lambda uid: (
                    f"{unit_lookup[uid]['name']}  |  "
                    f"{unit_lookup[uid].get('zone') or 'Unassigned'}"
                ),
                key="edit_unit_id",
            )
            selected_edit_unit = unit_lookup.get(edit_unit_id, {})
            with st.form("edit_unit_form"):
                edit_identity_cols = st.columns(2)
                with edit_identity_cols[0]:
                    edit_leader = st.text_input(
                        "Unit leader",
                        value=selected_edit_unit.get("leader_name", ""),
                        max_chars=100,
                    )
                with edit_identity_cols[1]:
                    edit_zone = st.text_input(
                        "Operating zone",
                        value=selected_edit_unit.get("zone") or "",
                        max_chars=100,
                        placeholder="e.g. North Sector, Gate B, Floor 3",
                    )
                edit_contact_cols = st.columns(3)
                with edit_contact_cols[0]:
                    edit_email = st.text_input(
                        "Email address",
                        value=selected_edit_unit.get("email") or "",
                        max_chars=200,
                    )
                with edit_contact_cols[1]:
                    edit_phone = st.text_input(
                        "Phone number",
                        value=selected_edit_unit.get("phone") or "",
                        max_chars=50,
                    )
                with edit_contact_cols[2]:
                    edit_whatsapp = st.text_input(
                        "WhatsApp number",
                        value=selected_edit_unit.get("whatsapp") or "",
                        max_chars=50,
                    )
                edit_submitted = st.form_submit_button("Save changes", use_container_width=True)
                if edit_submitted:
                    patch_resp = requests.patch(
                        f"{API_BASE}/api/units/{edit_unit_id}",
                        json={
                            "leader_name": edit_leader.strip() or None,
                            "zone": edit_zone.strip() or None,
                            "email": edit_email.strip() or None,
                            "phone": edit_phone.strip() or None,
                            "whatsapp": edit_whatsapp.strip() or None,
                        },
                        timeout=10,
                    )
                    if patch_resp.ok:
                        st.success(f"Unit updated successfully.")
                        st.rerun()
                    else:
                        detail = patch_resp.json().get("detail", patch_resp.text)
                        st.error(str(detail))

        if units:
            remove_unit_ids = [unit["id"] for unit in units]
            if st.session_state.get("remove_unit_id") not in remove_unit_ids:
                st.session_state.remove_unit_id = remove_unit_ids[0]
            remove_col, action_col = st.columns([3, 1], gap="small")
            with remove_col:
                remove_unit_id = st.selectbox(
                    "Remove unit",
                    remove_unit_ids,
                    format_func=lambda unit_id: (
                        f"{unit_lookup[unit_id]['name']}  |  "
                        f"{unit_lookup[unit_id].get('email') or unit_lookup[unit_id].get('phone') or unit_lookup[unit_id].get('whatsapp') or 'NO CONTACT'}"
                    ),
                    key="remove_unit_id",
                )
            with action_col:
                html('<div class="assignment-action-label">ROSTER ACTION</div>')
                if st.button("Remove unit", key="remove_unit_action", use_container_width=True):
                    remove_response = requests.delete(
                        f"{API_BASE}/api/units/{remove_unit_id}",
                        timeout=10,
                    )
                    if remove_response.ok:
                        st.success("Unit removed from roster.")
                        st.rerun()
                    else:
                        detail = remove_response.json().get("detail", remove_response.text)
                        st.error(str(detail))

    html('<div class="vertical-space-large"></div>')

    html(
        """
        <div class="section-head">
            <div class="section-name">Active assignments</div>
        </div>
        """
    )

    def render_assignment(assignment):
        unit = unit_lookup.get(assignment.get("unit_id"))
        unit_name = unit["name"] if unit else assignment.get("unit_name", "Unknown")
        threat_level = (assignment.get("threat_level") or "LOW").upper()
        css_key = "false" if threat_level == "FALSE ALARM" else threat_level.lower()
        current_status = assignment.get("status", "queued")
        assignment_id = assignment.get("id")
        status_options = ["queued", "sent", "acknowledged", "enroute", "resolved", "failed"]
        status_index = status_options.index(current_status.lower()) if current_status and current_status.lower() in status_options else 0
        metadata = [
            ("CHANNEL", (assignment.get("channel") or "email").upper()),
            ("PRIORITY", (assignment.get("priority") or "normal").upper()),
            ("STATUS", (current_status or "queued").upper()),
        ]
        metadata_html = "".join(
            f"<div><span>{label}</span><strong>{escape_html(value)}</strong></div>"
            for label, value in metadata
        )

        with st.container(border=True, key=f"card_assign_{assignment_id}"):
            html(
                f"""
                <div class="assignment-heading">
                    <div class="assignment-unit">{escape_html(str(unit_name))}</div>
                    <span class="level-{css_key}">{escape_html(threat_level)}</span>
                </div>
                <div class="assignment-meta-grid">{metadata_html}</div>
                <div class="assignment-note"><span>OPERATIONAL NOTE</span>{escape_html(str(assignment.get('note') or 'No note recorded'))}</div>
                """
            )

            action_cols = st.columns([2.2, 1, 1], gap="small")
            with action_cols[0]:
                new_status = st.selectbox(
                    "STATUS",
                    status_options,
                    index=status_index,
                    key=f"assign_status_{assignment_id}",
                )
            with action_cols[1]:
                html('<div class="assignment-action-label">ACTION</div>')
                if st.button("Update", key=f"update_assignment_{assignment_id}", use_container_width=True):
                    payload = {"status": new_status, "message": assignment.get("message"), "note": assignment.get("note")}
                    resp = requests.post(f"{API_BASE}/api/assignments/{assignment_id}/status", json=payload, timeout=10)
                    if resp.ok:
                        st.success("Assignment updated")
                        st.rerun()
                    else:
                        st.error(resp.text)
            with action_cols[2]:
                html('<div class="assignment-action-label">REMOVE</div>')
                if st.button("Delete", key=f"delete_assignment_{assignment_id}", use_container_width=True):
                    resp = requests.delete(f"{API_BASE}/api/assignments/{assignment_id}", json={"confirm": True}, timeout=10)
                    if resp.ok:
                        st.warning("Assignment deleted")
                        st.rerun()
                    else:
                        st.error(resp.text)

    if not assignments:
        html('<div class="empty-state">NO THREAT ASSIGNMENTS YET</div>')
    else:
        visible = assignments[:10]
        for row_start in range(0, len(visible), 2):
            row_cols = st.columns(2, gap="medium")
            for column, assignment in zip(row_cols, visible[row_start:row_start + 2]):
                with column:
                    render_assignment(assignment)


# ----------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------

if st.session_state.page == "Home":

    render_home()

elif st.session_state.page == "Events":

    render_events()

elif st.session_state.page == "Mails":

    render_mails()

elif st.session_state.page == "Control Panel":

    render_control_panel()