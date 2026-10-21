
(() => {
  "use strict";

  // ============================================================
  // STRIX — DASHBOARD INTERACTIONS
  // Visual enhancements only. No backend/API modifications.
  // ============================================================

  const installDashboardInteractions = () => {
    if (document.documentElement.dataset.strixInteractions === "ready") {
      return;
    }

    document.documentElement.dataset.strixInteractions = "ready";

    const style = document.createElement("style");

    style.textContent = `
      :root {
        --strix-motion-fast: 160ms;
        --strix-motion-normal: 260ms;
        --strix-motion-slow: 420ms;
        --strix-ease: cubic-bezier(.2, .7, .25, 1);
      }

      .block-container .strix-enter {
        animation: strix-enter var(--strix-motion-slow) var(--strix-ease) both;
        animation-delay: var(--strix-delay, 0ms);
      }

      .block-container .metric,
      .block-container [class*="st-key-card_"] {
        transition:
          transform var(--strix-motion-normal) var(--strix-ease),
          box-shadow var(--strix-motion-normal) ease,
          border-color var(--strix-motion-normal) ease,
          background var(--strix-motion-normal) ease;
        transform-origin: center;
      }

      .block-container .metric:hover,
      .block-container [class*="st-key-card_"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(0, 0, 0, .22);
      }

      .block-container .metric-value {
        transition: opacity 200ms ease, transform 200ms ease;
        font-variant-numeric: tabular-nums;
      }

      .block-container .event-row {
        transition:
          background var(--strix-motion-fast) ease,
          padding-left var(--strix-motion-fast) ease;
      }

      .block-container .event-row:hover {
        padding-left: 1.15rem;
        background: rgba(255, 255, 255, .055);
      }

      .block-container .mail-table tbody tr {
        transition: background var(--strix-motion-fast) ease;
      }

      .block-container .mail-table tbody tr:hover {
        background: rgba(255, 255, 255, .07);
      }

      .block-container .event-record-table tbody tr {
        transition: background var(--strix-motion-fast) ease;
      }

      .block-container .event-record-table tbody tr:hover {
        background: rgba(255, 255, 255, .035);
      }

      .block-container button,
      .block-container [data-testid="stFormSubmitButton"] button {
        transition:
          transform var(--strix-motion-fast) var(--strix-ease),
          filter var(--strix-motion-fast) ease,
          box-shadow var(--strix-motion-fast) ease;
      }

      .block-container button:hover {
        filter: brightness(1.1);
      }

      .block-container button.strix-pressed {
        transform: scale(.975);
        filter: brightness(.95);
      }

      .block-container .nav-button,
      .block-container .nav-active {
        transition:
          transform var(--strix-motion-fast) var(--strix-ease),
          background var(--strix-motion-fast) ease,
          color var(--strix-motion-fast) ease;
      }

      .block-container .nav-button:hover,
      .block-container .nav-active:hover {
        transform: translateX(3px);
      }

      .block-container .snapshot-caption {
        transition: background var(--strix-motion-normal) ease;
      }

      .block-container [data-testid="stImage"] img {
        transition: filter 240ms ease;
      }

      .block-container [data-testid="stImage"]:hover img {
        filter: brightness(1.045);
      }

      .block-container .section-head {
        transition: background var(--strix-motion-normal) ease;
      }

      .block-container .empty-state,
      .block-container .snapshot-missing,
      .block-container .feed-placeholder {
        animation: strix-fade-in 400ms ease both;
      }

      .block-container .state-dot.online {
        animation: strix-status-pulse 2.2s ease-in-out infinite;
      }

      .block-container .live-dot {
        animation: strix-live-pulse 1.4s ease-in-out infinite;
      }

      .block-container .strix-focus-ring:focus-visible {
        outline: 2px solid #f1f1f3;
        outline-offset: 3px;
      }

      @keyframes strix-enter {
        from {
          opacity: 0;
          transform: translateY(12px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      @keyframes strix-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      @keyframes strix-status-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: .48; }
      }

      @keyframes strix-live-pulse {
        0%, 100% {
          opacity: 1;
          box-shadow: 0 0 0 0 rgba(255, 255, 255, .2);
        }
        50% {
          opacity: .55;
          box-shadow: 0 0 0 4px rgba(255, 255, 255, 0);
        }
      }

      @media (max-width: 768px) {
        .block-container .metric:hover,
        .block-container [class*="st-key-card_"]:hover {
          transform: translateY(-1px);
        }
      }

      @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
          animation-duration: .01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: .01ms !important;
          scroll-behavior: auto !important;
        }
      }
    `;

    document.head.appendChild(style);

    const bindElements = () => {
      const animatedElements = document.querySelectorAll(
        ".block-container .metric, " +
        ".block-container .event-row, " +
        ".block-container [class*='st-key-card_'], " +
        ".block-container .page-title, " +
        ".block-container .section-head, " +
        ".block-container .snapshot-caption"
      );

      animatedElements.forEach((element, index) => {
        if (element.dataset.strixAnimated) return;

        element.dataset.strixAnimated = "true";
        element.classList.add("strix-enter");

        element.style.setProperty(
          "--strix-delay",
          `${Math.min(index * 35, 245)}ms`
        );
      });

      const tableRows = document.querySelectorAll(
        ".block-container .event-record-table tbody tr, " +
        ".block-container .mail-table tbody tr"
      );

      tableRows.forEach((row, index) => {
        if (row.dataset.strixAnimated) return;

        row.dataset.strixAnimated = "true";
        row.classList.add("strix-enter");

        row.style.setProperty(
          "--strix-delay",
          `${Math.min(index * 25, 250)}ms`
        );
      });

      document.querySelectorAll(
        ".block-container button"
      ).forEach((button) => {
        button.classList.add("strix-focus-ring");
      });
    };

    bindElements();

    // Streamlit dynamically replaces elements during reruns.
    // Observe DOM additions without repeatedly binding handlers.
    const observer = new MutationObserver((mutations) => {
      if (
        mutations.some((mutation) => mutation.addedNodes.length > 0)
      ) {
        bindElements();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Button press feedback.
    document.addEventListener("pointerdown", (event) => {
      const button = event.target.closest(
        ".block-container button"
      );

      if (button && !button.disabled) {
        button.classList.add("strix-pressed");
      }
    }, true);

    const releaseButton = (event) => {
      const button = event.target.closest?.(
        ".block-container button"
      );

      if (button) {
        button.classList.remove("strix-pressed");
      }
    };

    ["pointerup", "pointercancel", "pointerleave"].forEach(
      (eventName) => {
        document.addEventListener(
          eventName,
          releaseButton,
          true
        );
      }
    );

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;

      document.querySelectorAll(".unit-map .unit-card").forEach(
        (card) => {
          card.classList.remove("is-focused");
          card.setAttribute("aria-pressed", "false");
        }
      );

      document.querySelectorAll(
        ".unit-map .map-routes line"
      ).forEach((line) => {
        line.classList.remove("is-focused");
      });

      const selection = document.querySelector(
        ".unit-map .map-selection"
      );

      if (selection) {
        selection.textContent = "ALL UNITS / ACTIVE ROSTER";
      }
    });
  };

  installDashboardInteractions();

  // ============================================================
  // INTERACTIVE UNIT MAP
  // Works when .unit-map is in the current document.
  // ============================================================

  const initializeUnitMap = () => {
    const map = document.querySelector(".unit-map");

    if (!map || map.dataset.strixMapReady === "true") {
      return;
    }

    map.dataset.strixMapReady = "true";
    
    const mapStyle = document.createElement("style");

    mapStyle.textContent = `
      * { box-sizing: border-box; }

      html, body {
        margin: 0;
        width: 100%;
        background: transparent;
        overflow: hidden;
      }

      body {
        color: #f1f1f3;
        font-family: Inter, "Segoe UI", sans-serif;
      }

      .unit-map {
        position: relative;
        width: 100%;
        min-height: 560px;
        overflow: hidden;
        isolation: isolate;
        background-color: #101012;
        background-image:
          linear-gradient(#202024 1px, transparent 1px),
          linear-gradient(90deg, #202024 1px, transparent 1px);
        background-size: 36px 36px;
        border: 1px solid #35353b;
      }

      .map-topline, .map-legend {
        position: absolute;
        z-index: 4;
        left: 0;
        right: 0;
        display: flex;
        align-items: center;
        background: #17171a;
        color: #cbcbd1;
        font-family: "JetBrains Mono", Consolas, monospace;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: .08em;
      }

      .map-topline {
        top: 0;
        min-height: 42px;
        justify-content: space-between;
        gap: 12px;
        padding: 0 16px;
        border-bottom: 1px solid #35353b;
      }

      .map-selection {
        max-width: 65%;
        overflow: hidden;
        color: #9a9aa2;
        text-align: right;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .map-legend {
        bottom: 0;
        min-height: 38px;
        gap: 20px;
        padding: 0 16px;
        border-top: 1px solid #35353b;
        color: #9a9aa2;
        font-size: 10px;
      }

      .map-legend span {
        display: inline-flex;
        align-items: center;
        gap: 7px;
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

      .map-routes {
        position: absolute;
        z-index: 0;
        inset: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
      }

      .map-routes line {
        stroke: #67676e;
        stroke-width: .28;
        stroke-dasharray: 1.2 1.1;
        opacity: .52;
        vector-effect: non-scaling-stroke;
        transition: opacity .18s ease, stroke .18s ease,
                    stroke-width .18s ease;
      }

      .map-routes line.is-focused {
        stroke: #f1f1f3;
        stroke-width: .65;
        opacity: .95;
      }

      .map-routes circle {
        fill: #eeeeef;
        stroke: #101012;
        stroke-width: .5;
        vector-effect: non-scaling-stroke;
      }

      .unit-card {
        position: absolute;
        z-index: 2;
        width: min(156px, 36%);
        min-height: 112px;
        transform: translate(-50%, -50%);
        padding: 13px 14px;
        background: #232327;
        color: #f1f1f3;
        outline: 1px solid transparent;
        cursor: pointer;
        animation: map-arrive .28s ease both;
        transition: background .16s ease,
                    outline-color .16s ease,
                    transform .16s ease,
                    box-shadow .16s ease;
        box-shadow: 0 4px 14px rgba(0, 0, 0, .22);
      }

      .unit-card:hover,
      .unit-card:focus-visible,
      .unit-card.is-focused {
        z-index: 3;
        background: #2b2b30;
        outline-color: #bfc0c5;
        transform: translate(-50%, -50%) scale(1.035);
        box-shadow: 0 7px 20px rgba(0, 0, 0, .38);
      }

      .unit-card:focus-visible {
        outline-width: 2px;
      }

      .unit-card.status-queued,
      .unit-card.status-sent {
        outline-color: #70707a;
      }

      .unit-card.status-acknowledged,
      .unit-card.status-enroute {
        outline-color: #cbcbd1;
      }

      .unit-card.status-failed {
        outline-color: #a0a0a5;
        outline-style: dashed;
      }

      .unit-name {
        color: #fff;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: .04em;
      }

      .unit-leader {
        margin-top: 4px;
        color: #cbcbd1;
        font-size: 13px;
      }

      .unit-badge {
        margin-top: 9px;
        color: #cbcbd1;
        font-size: 12px;
        letter-spacing: .08em;
      }

      .unit-badge.idle {
        color: #9a9aa2;
        font-weight: 600;
      }

      .unit-zone {
        margin-top: 7px;
        color: #9a9aa2;
        font-size: 12px;
        line-height: 1.35;
      }

      @keyframes map-arrive {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      @media (max-width: 560px) {
        .map-topline {
          font-size: 9px;
          padding: 0 10px;
        }

        .map-selection { max-width: 52%; }

        .unit-card {
          width: 40%;
          padding: 9px;
        }

        .unit-name { font-size: 13px; }

        .unit-leader, .unit-zone {
          font-size: 10px;
        }

        .unit-badge { font-size: 10px; }
      }

      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
          animation-duration: .01ms !important;
          transition-duration: .01ms !important;
        }
      }
    `;

    document.head.appendChild(mapStyle);


    const cards = Array.from(
      map.querySelectorAll(".unit-card")
    );

    const lines = Array.from(
      map.querySelectorAll(".map-routes line")
    );

    const selection = map.querySelector(".map-selection");

    let pinnedCard = null;

    const resetPreview = () => {
      cards.forEach((card) => {
        card.classList.remove("is-focused");
        card.setAttribute("aria-pressed", "false");
      });

      lines.forEach((line) => {
        line.classList.remove("is-focused");
      });

      if (selection) {
        selection.textContent = "ALL UNITS / ACTIVE ROSTER";
      }
    };

    const preview = (card, pin = false) => {
      cards.forEach((item) => {
        const active = item === card;

        item.classList.toggle("is-focused", active);

        item.setAttribute(
          "aria-pressed",
          active && pin ? "true" : "false"
        );
      });

      lines.forEach((line) => {
        line.classList.toggle(
          "is-focused",
          line.dataset.unitId === card.dataset.unitId
        );
      });

      if (selection) {
        const unitName =
          card.querySelector(".unit-name")?.textContent || "UNIT";

        const status = card.dataset.status || "UNKNOWN";
        const threat = card.dataset.threat || "UNKNOWN";

        selection.textContent =
          `${unitName} / ${status} / ${threat}`;
      }

      if (pin) {
        pinnedCard = card;
      }
    };

    cards.forEach((card, index) => {
      card.style.animationDelay =
        `${Math.min(index * 45, 270)}ms`;

      card.setAttribute("tabindex", "0");
      card.setAttribute("role", "button");
      card.setAttribute("aria-pressed", "false");

      card.addEventListener("pointerenter", () => {
        preview(card);
      });

      card.addEventListener("pointerleave", () => {
        if (pinnedCard) {
          preview(pinnedCard, true);
        } else {
          resetPreview();
        }
      });

      card.addEventListener("focus", () => {
        preview(card);
      });

      card.addEventListener("blur", () => {
        if (pinnedCard) {
          preview(pinnedCard, true);
        } else {
          resetPreview();
        }
      });

      card.addEventListener("click", () => {
        if (pinnedCard === card) {
          pinnedCard = null;
          resetPreview();
        } else {
          pinnedCard = card;
          preview(card, true);
        }
      });

      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          card.click();
        }

        if (event.key === "Escape") {
          pinnedCard = null;
          resetPreview();
          card.blur();
        }
      });
    });
  };

  initializeUnitMap();
})();
