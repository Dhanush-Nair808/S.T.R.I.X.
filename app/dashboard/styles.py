
import streamlit as st


def apply_styles():

    st.markdown(
        """
        <style>

        

        :root {
            --black: #080808;
            --background: #0d0d0d;
            --surface: #121212;
            --surface-2: #171717;
            --line: #292929;
            --line-light: #353535;

            --white: #f2f2f2;
            --light: #d0d0d0;
            --grey: #999999;
            --dark-grey: #666666;

            --red: #d9d9d9;
            --base-font-size: 24px;
        }

        html {
            font-size: var(--base-font-size);
        }

        body,
        .stApp,
        .stApp * {
            font-size: 1rem;
            line-height: 1.5;
        }


        

        .stApp {
            background: var(--background);
            color: var(--white);
        }

        .main {
            background: var(--background);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        header[data-testid="stHeader"] {
            background: var(--background);
        }


        

        section[data-testid="stSidebar"] {
            background: var(--black);
            border-right: 1px solid var(--line);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.25rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .brand {
            padding: 0.5rem 0.55rem 1.2rem;
        }

        .brand-name {
            color: var(--white);
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.18em;
        }

        .brand-subtitle {
            color: var(--dark-grey);
            font-size: 0.58rem;
            letter-spacing: 0.14em;
            margin-top: 0.38rem;
        }

        .sidebar-rule {
            height: 1px;
            background: var(--line);
            margin: 0.4rem 0 1rem;
        }

        

        section[data-testid="stSidebar"]
        div[data-testid="stButton"] {
            margin-top: -2.25rem;
            margin-bottom: 0.35rem;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stButton"] > button {
            opacity: 0;
            background: transparent;
            border: none;
            box-shadow: none;
            height: 2rem;
            min-height: 2rem;
            cursor: pointer;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stButton"] > button:hover {
            background: transparent;
            border: none;
        }

        .nav-button,
        .nav-active {
            width: 100%;
            box-sizing: border-box;

            padding: 0.55rem 0.65rem;

            color: #777777;
            background: transparent;

            border-left: 2px solid transparent;

            font-size: 0.67rem;
            letter-spacing: 0.13em;

            transition:
                color 0.15s ease,
                background 0.15s ease,
                border-color 0.15s ease;
        }

        .nav-button {
            margin-bottom: 0.15rem;
        }

        .nav-button:hover {
            color: var(--white);
            background: #111111;
        }

        .nav-active {
            color: var(--white);
            background: #161616;
            border-left-color: var(--white);
        }

        .system-state {
            padding: 0.75rem 0.55rem;
        }

        .system-label {
            color: #555555;
            font-size: 0.56rem;
            letter-spacing: 0.14em;
        }

        .system-value {
            display: flex;
            align-items: center;
            gap: 0.45rem;

            margin-top: 0.5rem;

            color: #999999;
            font-size: 0.62rem;
            letter-spacing: 0.08em;
        }

        .state-dot {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            display: inline-block;
        }

        .state-dot.online {
            background: #cfcfcf;
        }

        .state-dot.offline {
            background: #555555;
        }


        

        .page-kicker {
            color: #666666;
            font-size: 0.58rem;
            letter-spacing: 0.18em;
            margin-bottom: 0.45rem;
        }

        .page-title {
            color: var(--white);
            font-size: 1.65rem;
            font-weight: 400;
            letter-spacing: -0.025em;
            line-height: 1.2;
        }

        .page-description {
            color: #6e6e6e;
            font-size: 0.72rem;
            margin-top: 0.45rem;
            margin-bottom: 1.4rem;
        }


        

        .metric {
            background: #111111;

            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);

            padding: 0.85rem 0.95rem;
            min-height: 68px;

            box-sizing: border-box;
        }

        .metric-label {
            color: #666666;
            font-size: 0.56rem;
            letter-spacing: 0.13em;
        }

        .metric-value {
            color: var(--white);
            font-size: 1.45rem;
            font-weight: 400;
            margin-top: 0.45rem;
        }


        

        .vertical-space {
            height: 1.3rem;
        }

        .vertical-space-large {
            height: 2rem;
        }

        .section-head {
            display: flex;
            align-items: center;
            justify-content: space-between;

            border-bottom: 1px solid var(--line);

            padding-bottom: 0.55rem;
            margin-bottom: 0.2rem;
        }

        .section-name {
            color: #bdbdbd;
            font-size: 0.63rem;
            letter-spacing: 0.15em;
        }

        .section-note {
            color: #505050;
            font-size: 0.55rem;
            letter-spacing: 0.13em;
        }


        

        .live-state {
            display: flex;
            align-items: center;
            gap: 0.4rem;

            color: #777777;
            font-size: 0.55rem;
            letter-spacing: 0.12em;
        }

        .live-dot {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #bdbdbd;
        }

        .feed-placeholder {
            height: 430px;

            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            background: #101010;
            border: 1px solid var(--line);
        }

        .feed-placeholder-title {
            color: #999999;
            font-size: 0.66rem;
            letter-spacing: 0.14em;
        }

        .feed-placeholder-text {
            color: #555555;
            font-size: 0.62rem;
            margin-top: 0.4rem;
        }


        

        .event-row {
            padding: 0.78rem 0;

            border-bottom: 1px solid #202020;
        }

        .event-row-top {
            display: flex;
            align-items: center;
            justify-content: space-between;

            gap: 0.8rem;
        }

        .event-row-id {
            color: #d0d0d0;
            font-size: 0.68rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .event-row-time {
            color: #555555;
            font-size: 0.58rem;
            margin-top: 0.32rem;
        }

        .level-high,
        .level-medium,
        .level-low,
        .level-false {
            font-size: 0.54rem;
            letter-spacing: 0.11em;
            white-space: nowrap;
        }

        .level-high {
            color: #eeeeee;
        }

        .level-medium {
            color: #bbbbbb;
        }

        .level-low {
            color: #888888;
        }

        .level-false {
            color: #555555;
        }


        

        .empty-state {
            padding: 2rem 1rem;

            border-bottom: 1px solid var(--line);

            color: #555555;
            text-align: center;

            font-size: 0.6rem;
            letter-spacing: 0.12em;
        }


        

        .snapshot-caption {
            padding-top: 0.55rem;
        }

        .snapshot-id {
            color: #cccccc;
            font-size: 0.65rem;
            margin-bottom: 0.25rem;
        }

        .snapshot-time {
            color: #555555;
            font-size: 0.57rem;
            margin-top: 0.25rem;
        }

        .snapshot-missing {
            height: 180px;

            display: flex;
            align-items: center;
            justify-content: center;

            border: 1px solid var(--line);

            color: #555555;
            font-size: 0.58rem;
            letter-spacing: 0.1em;
        }

        img {
            border-radius: 0 !important;
        }


        

        .control-panel {
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);

            padding: 1.4rem 0;
        }

        .control-title {
            color: #aaaaaa;
            font-size: 0.62rem;
            letter-spacing: 0.13em;
        }

        .control-text {
            color: #555555;
            font-size: 0.65rem;
            margin-top: 0.45rem;
        }


        

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 0;
            overflow: hidden;
        }


        

        .stButton > button {
            border-radius: 0;
            box-shadow: none;
        }


        

        ::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }

        ::-webkit-scrollbar-track {
            background: var(--black);
        }

        ::-webkit-scrollbar-thumb {
            background: #333333;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #4a4a4a;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )

