import streamlit as st


def apply_styles():

    st.markdown(
        """
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ============================================================
           TOKENS
           Square corners. Solid grey surfaces with no outlines.
           White blocks carry titles, grey blocks carry content,
           and the page ground fades from black to white.
           ============================================================ */

        :root {
            --side: #0a0a0c;
            --side-item: #151518;
            --side-item-hover: #202024;

            --surface: #232327;
            --surface-hover: #2b2b30;
            --sunken: #101012;
            --control: #34343a;
            --control-hover: #44444b;
            --rule: #35353b;

            --text: #f1f1f3;
            --text-2: #cbcbd1;
            --text-3: #9a9aa2;
            --text-4: #70707a;

            --on-white: #09090b;
            --on-white-2: #3f3f45;
            --on-white-3: #55555b;

            --button-light: linear-gradient(180deg, #f4f4f5 0%, #c4c4ca 100%);

            --nav-h: 3rem;

            --font: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
            --mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
        }

        html {
            font-size: 16px;
        }

        html, body, .stApp {
            font-family: var(--font);
            -webkit-font-smoothing: antialiased;
        }

        /* ============================================================
           APP SHELL: black to white gradient ground
           ============================================================ */

        .stApp {
            color: var(--text);
            background-color: #000000;
            background-image: black;
            background-attachment: fixed;
        }

        .main,
        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        header[data-testid="stHeader"] {
            background: #000000;
        }

        .block-container {
            max-width: 1680px;
            padding-top: 2rem;
            padding-bottom: 6rem;
        }

        .block-container [data-testid="stVerticalBlock"] {
            gap: 1rem;
        }

        .vertical-space { height: 0.75rem; }
        .vertical-space-large { height: 1.5rem; }

        /* ============================================================
           SIDEBAR
           Brand on top, navigation in the middle,
           system status pinned to the bottom
           ============================================================ */

        section[data-testid="stSidebar"] {
            background: var(--side);
            border-right: 1px solid #1c1c20;
        }

        section[data-testid="stSidebar"] > div {
            padding: 1.25rem 0.9rem 1.25rem;
        }

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0;
            min-height: calc(100vh - 8rem);
        }

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > *:last-child {
            margin-top: auto;
        }

        .brand {
            padding: 0.25rem 0.75rem 1.25rem;
        }

        .brand-name {
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: 0.24em;
            line-height: 1.2;
        }

        .brand-subtitle {
            color: var(--text-3);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.14em;
            margin-top: 0.4rem;
        }

        .sidebar-rule {
            height: 1px;
            background: var(--rule);
            margin: 0 0 1.1rem;
        }

        /* Nav: styled label with an invisible button laid over it */

        section[data-testid="stSidebar"] div[data-testid="stButton"] {
            margin-top: calc(var(--nav-h) * -1);
            margin-bottom: 0.4rem;
            position: relative;
            z-index: 3;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            opacity: 0;
            background: transparent;
            border: none;
            box-shadow: none;
            height: var(--nav-h);
            min-height: var(--nav-h);
            cursor: pointer;
            transform: none;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            background: transparent;
            border: none;
            transform: none;
        }

        .nav-button,
        .nav-active {
            width: 100%;
            height: var(--nav-h);
            box-sizing: border-box;
            display: flex;
            align-items: center;
            padding: 0 1rem;
            font-size: 0.8125rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            transition: background 0.15s ease, color 0.15s ease;
        }

        .nav-button {
            color: var(--text-2);
            background: var(--side-item);
        }

        .nav-button:hover {
            color: #ffffff;
            background: var(--side-item-hover);
        }

        .nav-active {
            color: var(--on-white);
            background: #ffffff;
        }

        .system-state {
            padding: 1rem 1.1rem;
            background: var(--side-item);
        }

        .system-label {
            color: var(--text-3);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.14em;
        }

        .system-value {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin-top: 0.55rem;
            color: var(--text);
            font-size: 0.9375rem;
            font-weight: 600;
            letter-spacing: 0.08em;
        }

        .state-dot {
            width: 9px;
            height: 9px;
            display: inline-block;
        }

        .state-dot.online {
            background: #ffffff;
        }

        .state-dot.offline {
            background: var(--text-4);
        }

        /* ============================================================
           PAGE TITLE BANNER
           ============================================================ */

        .page-kicker {
            background: darkgrey;
            color: var(--on-white-3);
            font-family: var(--mono);
            font-size: 0.8125rem;
            font-weight: 500;
            letter-spacing: 0.08em;
            padding: 1.75rem 2rem 0;
        }

        .page-title {
            background: linear-gradient(180deg, darkgrey 0%, white 100%);
            color: var(--on-white);
            font-size: 3.25rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.05;
            padding: 0.65rem 2rem 0;
        }

        .page-description {
            background: white;
            color: var(--on-white-2);
            font-size: 1.0625rem;
            line-height: 1.45;
            padding: 0.85rem 2rem 1.9rem;
            margin-bottom: 0.5rem;
        }

        /* ============================================================
           METRICS
           ============================================================ */

        .metric {
            background: var(--surface);
            padding: 1.1rem 1.25rem 1.25rem;
            min-height: 112px;
            box-sizing: border-box;
        }

        .metric-label {
            color: var(--text-2);
            font-size: 0.9375rem;
            font-weight: 500;
        }

        .metric-value {
            color: #ffffff;
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -0.035em;
            line-height: 1.05;
            margin-top: 0.5rem;
            font-variant-numeric: tabular-nums;
        }

        /* ============================================================
           SECTION HEADERS: white bars
           ============================================================ */

        .section-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: #ffffff;
            padding: 0.9rem 1.1rem;
        }

        .section-name {
            color: var(--on-white);
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        .section-note {
            color: var(--on-white-3);
            font-size: 0.8125rem;
            font-weight: 500;
        }

        /* ============================================================
           LIVE FEED
           ============================================================ */

        .live-state {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--on-white);
            font-size: 0.8125rem;
            font-weight: 600;
            letter-spacing: 0.06em;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--on-white);
            animation: blink 1.4s steps(2, jump-none) infinite;
        }

        @keyframes blink {
            50% { opacity: 0.25; }
        }

        @media (prefers-reduced-motion: reduce) {
            .live-dot { animation: none; }
            * { transition: none !important; }
        }

        .feed-placeholder {
            height: 430px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--surface);
        }

        .feed-placeholder-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 0.14em;
        }

        .feed-placeholder-text {
            color: var(--text-3);
            font-size: 0.9375rem;
            margin-top: 0.6rem;
        }

        /* ============================================================
           EVENT ROWS AND SNAPSHOTS
           ============================================================ */

        .event-list {
            display: grid;
            gap: 0.5rem;
        }

        .event-row {
            padding: 0.85rem 1rem;
            background: var(--surface);
            transition: background 0.15s ease;
        }

        .event-row:hover {
            background: var(--surface-hover);
        }

        .event-row-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
        }

        .event-row-id {
            color: var(--text);
            font-family: var(--mono);
            font-size: 0.9rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .event-row-time {
            color: var(--text-3);
            font-size: 0.8125rem;
            margin-top: 0.4rem;
        }

        /* Threat levels: a square marker plus the word */

        
/* ============================================================
   STRIX THREAT STATUS BADGES
   ============================================================ */

.level-high,
.level-medium,
.level-low,
.level-false {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.55rem;

    padding: 0.55rem 0.85rem;
    min-height: 36px;

    border: 1px solid transparent;
    border-radius: 5px;

    font-size: 0.95rem;
    font-weight: 750;
    letter-spacing: 0.07em;
    line-height: 1.2;
    white-space: nowrap;

    transition:
        background 180ms ease,
        border-color 180ms ease,
        box-shadow 180ms ease;
}

/* Status indicator */
.level-high::before,
.level-medium::before,
.level-low::before,
.level-false::before {
    content: "";
    display: inline-block;
    width: 9px;
    height: 9px;
    flex: 0 0 9px;
}

/* HIGH — red */


.level-high::before {
    background: #ef4444;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.55);
}


.level-medium::before {
    background: #f97316;
}

/* LOW — yellow */


.level-low::before {
    background: #facc15;
}



.level-false::before {
    background: #22c55e;
}

/* Make status badges more prominent inside event cards */
.event-row .level-high,
.event-row .level-medium,
.event-row .level-low,
.event-row .level-false {
    font-size: 0.95rem;
    padding: 0.6rem 0.85rem;
    min-height: 38px;
}

@media (max-width: 600px) {
    .event-row .level-high,
    .event-row .level-medium,
    .event-row .level-low,
    .event-row .level-false {
        font-size: 0.78rem;
        padding: 0.4rem 0.55rem;
        min-height: 30px;
        letter-spacing: 0.035em;
    }
}

@media (prefers-reduced-motion: reduce) {
    .level-high,
    .level-medium,
    .level-low,
    .level-false {
        transition: none;
    }
}


        .empty-state {
            padding: 2.25rem 1rem;
            background: var(--surface);
            color: var(--text-3);
            text-align: center;
            font-size: 0.875rem;
            font-weight: 500;
            letter-spacing: 0.1em;
        }

        .snapshot-caption {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.4rem;
            padding: 0.8rem 0.95rem 0.9rem;
            background: var(--surface);
        }

        .snapshot-id {
            color: var(--text);
            font-family: var(--mono);
            font-size: 0.85rem;
            overflow-wrap: anywhere;
        }

        .snapshot-time {
            color: var(--text-3);
            font-size: 0.8125rem;
        }

        .snapshot-missing {
            min-height: 180px;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--sunken);
            color: var(--text-3);
            font-size: 0.8125rem;
            font-weight: 500;
            letter-spacing: 0.1em;
        }

        img {
            border-radius: 0 !important;
        }

        [data-testid="stImage"] img {
            background: #000000;
        }

        /* ============================================================
           CONTROL PANEL
           ============================================================ */

        .unit-map {
            position: relative;
            min-height: 560px;
            overflow: hidden;
            background-color: var(--sunken);
            background-image:
                linear-gradient(#202024 1px, transparent 1px),
                linear-gradient(90deg, #202024 1px, transparent 1px);
            background-size: 36px 36px;
            border: 1px solid #35353b;
        }

        .map-topline {
            position: absolute;
            z-index: 4;
            top: 0;
            left: 0;
            right: 0;
            min-height: 42px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0 1rem;
            background: #17171a;
            border-bottom: 1px solid #35353b;
            color: var(--text-2);
            font-family: var(--mono);
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.07em;
        }

        .map-routes {
            position: absolute;
            inset: 0;
            z-index: 0;
            width: 100%;
            height: 100%;
            overflow: visible;
            pointer-events: none;
        }

        .map-routes line {
            stroke: #67676e;
            stroke-width: 0.28;
            stroke-dasharray: 1.2 1.1;
            vector-effect: non-scaling-stroke;
        }

        .map-routes circle {
            fill: #eeeeef;
            stroke: #101012;
            stroke-width: 0.5;
            vector-effect: non-scaling-stroke;
        }

        /* Camera / threat-origin marker */
        .camera-marker {
            position: absolute;
            z-index: 3;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.3rem;
            pointer-events: none;
        }

        .camera-dot {
            width: 10px;
            height: 10px;
            background: #ef4444;
            border: 2px solid #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.7);
            animation: pulse-camera 2s ease-in-out infinite;
        }

        @keyframes pulse-camera {
            0%, 100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.7); }
            50% { box-shadow: 0 0 16px rgba(239, 68, 68, 1); }
        }

        .camera-label {
            color: #ef4444;
            font-family: var(--mono);
            font-size: 0.6rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            white-space: nowrap;
            text-shadow: 0 1px 3px #000000;
        }

        .map-legend {
            position: absolute;
            z-index: 3;
            left: 0;
            right: 0;
            bottom: 0;
            min-height: 38px;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            padding: 0 1rem;
            background: #17171a;
            border-top: 1px solid #35353b;
            color: var(--text-3);
            font-family: var(--mono);
            font-size: 0.68rem;
            letter-spacing: 0.06em;
        }

        .map-legend span {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
        }

        .map-key {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #d7d7da;
        }

        .map-key.link-key {
            width: 16px;
            height: 1px;
            background: #77777e;
        }

        .map-grid-label {
            position: absolute;
            top: 0.8rem;
            left: 1rem;
            color: var(--text-3);
            font-size: 0.8125rem;
            font-weight: 500;
            pointer-events: none;
        }

        .unit-card {
            position: absolute;
            z-index: 2;
            width: min(156px, 36%);
            min-height: 112px;
            transform: translate(-50%, -50%);
            padding: 0.8rem 0.9rem;
            box-sizing: border-box;
            background: var(--surface);
            transition: background 0.15s ease;
        }

        .unit-card:hover {
            z-index: 3;
            background: var(--surface-hover);
            outline: 1px solid #9a9aa2;
        }

        /* Unit state is shown by an outline, idle units have none */

        .unit-card.status-queued,
        .unit-card.status-sent {
            outline: 1px solid #70707a;
        }

        .unit-card.status-acknowledged,
        .unit-card.status-enroute {
            outline: 2px solid #ffffff;
        }

        .unit-card.status-resolved .unit-name,
        .unit-card.status-resolved .unit-leader,
        .unit-card.status-resolved .unit-zone,
        .unit-card.status-resolved .unit-badge {
            color: var(--text-4);
        }

        .unit-card.status-failed {
            outline: 1px dashed #cbcbd1;
        }

        .unit-name {
            color: #ffffff;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }

        .unit-leader {
            color: var(--text-2);
            font-size: 0.8125rem;
            margin-top: 0.25rem;
        }

        .unit-badge {
            margin-top: 0.6rem;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            color: var(--text-2);
        }

        .unit-badge.idle {
            color: var(--text-4);
            font-weight: 600;
        }

        .unit-zone {
            color: var(--text-3);
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }

        /* Assignments */

        .assignment-heading {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.7rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid var(--rule);
        }

        .assignment-unit {
            color: #ffffff;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        .assignment-meta-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            padding: 0.9rem 0;
            border-bottom: 1px solid var(--rule);
        }

        .assignment-meta-grid span,
        .assignment-note > span {
            display: block;
            color: var(--text-3);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.08em;
            margin-bottom: 0.3rem;
        }

        .assignment-meta-grid strong {
            color: var(--text);
            font-size: 0.9375rem;
            font-weight: 600;
            overflow-wrap: anywhere;
        }

        .assignment-note {
            color: var(--text-2);
            font-size: 0.9375rem;
            line-height: 1.5;
            padding: 0.8rem 0 0.2rem;
            overflow-wrap: anywhere;
        }

        .assignment-action-label {
            color: var(--text-2);
            font-size: 0.875rem;
            font-weight: 500;
            line-height: 1.5;
            min-height: 1.75rem;
        }

        .selected-event-fields {
            display: grid;
            gap: 0.75rem;
            align-content: start;
        }

        .form-evidence-label {
            color: var(--text-2);
            font-size: 0.8125rem;
            font-weight: 600;
            letter-spacing: 0.06em;
        }

        .evidence-field span {
            display: block;
            color: var(--text-3);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.06em;
            margin-bottom: 0.2rem;
        }

        .evidence-field strong {
            display: block;
            color: var(--text);
            font-size: 0.9375rem;
            font-weight: 500;
            line-height: 1.35;
            overflow-wrap: anywhere;
        }

        /* Event records */

        .event-record-heading {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            padding: 0 0 0.9rem;
            border-bottom: 1px solid var(--rule);
        }

        .event-record-kicker {
            color: var(--text-3);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.1em;
        }

        .event-record-id {
            color: #ffffff;
            font-family: var(--mono);
            font-size: 1.125rem;
            overflow-wrap: anywhere;
            margin-top: 0.4rem;
        }

        .event-record-table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 0.4rem;
            table-layout: fixed;
        }

        .event-record-table tr {
            border-bottom: 1px solid var(--rule);
            transition: background 0.14s ease;
        }

        .event-record-table tbody tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.035);
        }

        .event-record-table tbody tr:hover {
            background: rgba(255, 255, 255, 0.09);
        }

        .event-record-table tr:last-child {
            border-bottom: none;
        }

        .event-record-table th,
        .event-record-table td {
            padding: 0.65rem 0.2rem;
            text-align: left;
            vertical-align: top;
        }

        .event-record-table th {
            width: 31%;
            padding-right: 0.7rem;
            color: var(--text-3);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.08em;
        }

        .event-record-table td {
            color: var(--text-2);
            font-size: 0.9375rem;
            overflow-wrap: anywhere;
        }

        .event-inference {
            margin-top: 1rem;
            padding: 0.9rem 1rem;
            background: var(--sunken);
            border-left: 2px solid #9a9aa2;
        }

        .event-inference-title {
            color: var(--text-3);
            font-family: var(--mono);
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            margin-bottom: 0.45rem;
        }

        .event-inference-text {
            color: var(--text-2);
            font-size: 0.9375rem;
            line-height: 1.5;
            overflow-wrap: anywhere;
            white-space: pre-wrap;
        }

        /* ============================================================
           STREAMLIT CONTAINERS: solid grey, no outline, square
           The keyed cards (card_*) work on current Streamlit versions,
           the BorderWrapper selector covers older ones.
           ============================================================ */

        [class*="st-key-card_"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--surface) !important;
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            outline: 0 !important;
        }

        [class*="st-key-card_"] {
            padding: 1.1rem 1.25rem !important;
        }

        [data-testid="stForm"] {
            background: var(--surface);
            border: 0;
            border-radius: 0;
            padding: 1.5rem;
        }

        [data-testid="stWidgetLabel"] p {
            color: var(--text-2);
            font-size: 1rem;
            font-weight: 500;
        }

        .stTextInput input,
        .stTextArea textarea,
        [data-baseweb="select"] > div {
            background: var(--sunken) !important;
            color: var(--text) !important;
            border: 1px solid var(--sunken) !important;
            border-radius: 0 !important;
            font-size: 1.0625rem !important;
            transition: border-color 0.15s ease, background 0.15s ease;
        }

        [data-testid="stForm"] [data-baseweb="select"] > div {
            min-height: 3rem;
        }

        [data-testid="stForm"] textarea {
            min-height: 7rem;
        }

        [data-baseweb="input"],
        [data-baseweb="textarea"],
        [data-baseweb="base-input"] {
            border-radius: 0 !important;
            background: var(--sunken) !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: var(--text-4) !important;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus,
        [data-baseweb="select"] > div:focus-within {
            border-color: #e4e4e7 !important;
            box-shadow: none !important;
        }

        [data-baseweb="select"] > div:hover {
            border-color: #55555d !important;
        }

        [data-baseweb="select"] span,
        [data-baseweb="select"] svg {
            color: var(--text) !important;
            fill: var(--text-3) !important;
        }

        [data-baseweb="popover"] > div,
        [data-baseweb="menu"],
        ul[role="listbox"] {
            background: #17171a !important;
            border: 0;
            border-radius: 0 !important;
        }

        li[role="option"] {
            color: var(--text-2) !important;
            background: #17171a !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {
            background: var(--control) !important;
            color: #ffffff !important;
        }

        /* Buttons: grey by default, white for the primary form action */

        .stButton > button {
            background: var(--control);
            color: var(--text);
            border: 0;
            border-radius: 0;
            box-shadow: none;
            min-height: 2.5rem;
            padding: 0.3rem 1rem;
            font-size: 0.9375rem !important;
            font-weight: 600;
            transition: background 0.15s ease;
        }

        .stButton > button p,
        [data-testid="stFormSubmitButton"] > button p {
            font-size: 0.9375rem !important;
            font-weight: 600;
            line-height: 1.2 !important;
            margin: 0 !important;
        }

        .stButton > button:hover {
            background: var(--control-hover);
            color: #ffffff;
        }

        [data-testid="stFormSubmitButton"] > button {
            background: var(--button-light);
            color: var(--on-white);
            border: 0;
            border-radius: 0;
            min-height: 2.8rem;
            font-weight: 700;
            box-shadow: none;
            transition: background 0.15s ease;
        }

        [data-testid="stFormSubmitButton"] > button p {
            color: var(--on-white);
            font-weight: 700;
        }

        [data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(180deg, #ffffff 0%, #d9d9de 100%);
            color: #000000;
        }

        .stButton > button:focus-visible,
        [data-testid="stFormSubmitButton"] > button:focus-visible {
            outline: 2px solid #ffffff;
            outline-offset: 2px;
        }

        /* Expander */

        [data-testid="stExpander"] {
            background: var(--surface);
            border: 0 !important;
            border-radius: 0 !important;
        }

        [data-testid="stExpander"] details {
            background: var(--surface);
            border: 0;
            border-radius: 0;
        }

        [data-testid="stExpander"] summary {
            color: var(--text);
            font-size: 0.9375rem;
            font-weight: 600;
        }

        [data-testid="stExpander"] summary:hover {
            color: #ffffff;
        }

        /* Alerts */

        div[data-testid="stAlert"] {
            background: var(--surface-hover);
            border: 0;
            border-radius: 0;
            color: var(--text);
        }

        /* Dataframe */

        div[data-testid="stDataFrame"] {
            border: 0;
            border-radius: 0;
            overflow: hidden;
        }

        .mail-table-wrap {
            width: 100%;
            overflow-x: auto;
            margin-top: 0.75rem;
        }

        .mail-table {
            width: 100%;
            min-width: 820px;
            border-collapse: collapse;
            background: var(--surface);
            color: var(--text);
            font-size: 1.125rem;
            text-align: left;
        }

        .mail-table th {
            padding: 1rem 1.1rem;
            background: #303035;
            color: var(--text-2);
            border-bottom: 1px solid var(--rule);
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            white-space: nowrap;
        }

        .mail-table td {
            padding: 1.05rem 1.1rem;
            color: var(--text);
            border-bottom: 1px solid var(--rule);
            font-size: 1rem;
            line-height: 1.4;
        }

        .mail-table tbody tr:hover {
            background: var(--surface-hover);
        }

        .mail-table tbody tr.strix-enter {
            animation: strix-table-row-enter 0.28s ease both;
        }

        @keyframes strix-table-row-enter {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        [data-testid="stExpander"] [data-testid="stForm"] {
            border-top: 1px solid var(--rule);
            padding-top: 1rem;
        }

        [data-testid="stCaptionContainer"] {
            color: var(--text-2);
        }

        hr {
            border-color: var(--rule);
        }

        /* ============================================================
           SCROLLBAR, SELECTION, SMALL SCREENS
           ============================================================ */

        ::selection {
            background: #ffffff;
            color: #000000;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #000000;
        }

        ::-webkit-scrollbar-thumb {
            background: #3a3a41;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #55555d;
        }

        @media (max-width: 820px) {
            .page-kicker { padding: 1.25rem 1.1rem 0; }
            .page-title { font-size: 2.25rem; padding: 0.5rem 1.1rem 0; }
            .page-description { padding: 0.75rem 1.1rem 1.4rem; }
            .metric-value { font-size: 2.25rem; }
            .assignment-meta-grid { grid-template-columns: minmax(0, 1fr); }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )