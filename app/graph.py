from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END

import numpy as np

try:
    from app.detection import WeaponPersonDetector
    from app.proximity import find_person_weapon_pairs
    from app.tracker import MultiFrameConfirmer, SimpleTracker
    from app.alert import EmailAlerter
    from app.mistral_verification import MistralVerifier
    from app.event_manager import ThreatEventManager
    from app.database import create_detection_record
except ImportError:
    from detection import WeaponPersonDetector
    from proximity import find_person_weapon_pairs
    from tracker import MultiFrameConfirmer, SimpleTracker
    from alert import EmailAlerter
    from mistral_verification import MistralVerifier
    from event_manager import ThreatEventManager
    from database import create_detection_record

detector = WeaponPersonDetector()

# These thresholds are deliberately looser so the system does not require
# the target to remain static across many frames before LLM verification.
# Threat score still incorporates proximity, IoU, weapon confidence, and
# tracking consistency; motion alone should not suppress a strong threat.
confirmer = MultiFrameConfirmer(
    window_size=6,
    confirm_threshold=0.46,
    min_hits=3,
    min_avg_score=0.40,
    instant_confirm_threshold=0.80
)

tracker = SimpleTracker(iou_threshold=0.3, max_age=5)
verifier = MistralVerifier()
alerter = EmailAlerter()

event_manager = ThreatEventManager(
    event_timeout=5.0,
    mistral_cooldown=60.0
)

class STRIXState(TypedDict):
    frame: Optional[np.ndarray]
    persons: List[dict]
    weapons: List[dict]
    pairs: List[dict]
    current_score: float
    avg_score: float
    confirmed: bool
    status: str
    mistral_decision: str
    mistral_reasoning: str

def detection_node(state: STRIXState) -> dict:
    frame = state["frame"]
    persons, weapons = detector.detect(frame)

    if weapons is None:
        weapons = []

    if weapons:
        try:
            tracker.update(weapons)
        except Exception:
            pass

    return {
        "persons": persons,
        "weapons": weapons
    }

def proximity_node(state: STRIXState) -> dict:
    persons = state["persons"]
    weapons = state["weapons"]

    pairs = find_person_weapon_pairs(persons, weapons)
    current_score = 0.0

    if pairs:
        best = max(pairs, key=lambda x: x["threat_score"])
        current_score = best["threat_score"]

    return {
        "pairs": pairs,
        "current_score": current_score
    }

def confirmation_node(state: STRIXState) -> dict:
    current_score = state["current_score"]
    confirmed, avg_score = confirmer.update(current_score)

    status = "THREAT CONFIRMED" if confirmed else "Monitoring..."

    return {
        "confirmed": confirmed,
        "avg_score": avg_score,
        "status": status
    }

def confirmation_router(state: STRIXState) -> str:
    confirmed = state["confirmed"]
    frame = state["frame"]

    if event_manager.should_verify(confirmed, frame):
        return "mistral"

    if confirmed:
        return "cooldown_active"

    return "monitoring"

def mistral_verification_node(state: STRIXState) -> dict:
    pairs = state["pairs"]

    if event_manager.current_event_id is not None:
        try:
            snapshot_path = event_manager.save_snapshot(state.get("frame"))
            if snapshot_path is None:
                print(
                    f"[EVENT] No snapshot was saved for "
                    f"{event_manager.current_event_id}."
                )
        except Exception as exc:
            print(f"[EVENT] Snapshot save failed: {exc}")

    if not pairs:
        event_manager.mark_mistral_processed(
            level="FALSE ALARM",
            reasoning="No valid person-weapon relationship was available for verification."
        )
        return {
            "mistral_decision": "FALSE ALARM",
            "mistral_reasoning": "No valid person-weapon relationship was available for verification.",
            "status": "Mistral: FALSE ALARM"
        }

    best = max(pairs, key=lambda x: x["threat_score"])

    try:
        result = verifier.verify(
            frame=state["frame"],
            weapon_conf=best["weapon"]["confidence"],
            distance=best["distance"],
            iou=best["iou"],
            threat_score=best.get("threat_score"),
            tracking_consistency=best.get("tracking_consistency"),
            avg_score=state.get("avg_score")
        )
    except Exception as e:
        print(f"[AI ANALYSIS] Verification node crashed: {e}")
        result = {
            "level": "FALSE ALARM",
            "reasoning": "Verification node failed, so threat escalation was not accepted."
        }

    level = result.get("level", "FALSE ALARM")
    reasoning = result.get("reasoning", "Verification node failed, so threat escalation was not accepted.")

    print(f"[AI ANALYSIS] Level: {level}")
    print(f"[AI ANALYSIS] Reasoning: {reasoning}")

    if level in {"HIGH", "MEDIUM", "LOW"}:
        try:
            if event_manager.current_event_id is not None:
                weapon = best["weapon"]
                create_detection_record(
                    event_id=event_manager.current_event_id,
                    track_id=weapon.get("track_id"),
                    bbox=weapon.get("box"),
                    confidence=weapon.get("confidence"),
                    tracking_consistency=best.get("tracking_consistency"),
                    frame_index=None,
                )
        except Exception:
            pass

    event_manager.mark_mistral_processed(level=level, reasoning=reasoning)

    return {
        "mistral_decision": level,
        "mistral_reasoning": reasoning,
        "status": f"Mistral: {level}"
    }

def mistral_router(state: STRIXState) -> str:
    level = state["mistral_decision"]
    if level == "FALSE ALARM":
        return "false_alarm"
    return "alert"

def alert_node(state: STRIXState) -> dict:
    level = state["mistral_decision"]
    reasoning = state["mistral_reasoning"]

    if not event_manager.should_alert(level):
        return {"status": "Alert skipped"}

    frame = state["frame"]
    success = alerter.send_alert(frame=frame, level=level, reasoning=reasoning)
    event_manager.mark_alert_result(success)

    status = "ALERT SENT" if success else "ALERT FAILED / COOLDOWN"
    return {"status": status}

def build_graph():
    workflow = StateGraph(STRIXState)

    workflow.add_node("detect", detection_node)
    workflow.add_node("proximity", proximity_node)
    workflow.add_node("confirm", confirmation_node)
    workflow.add_node("mistral", mistral_verification_node)
    workflow.add_node("alert", alert_node)

    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "proximity")
    workflow.add_edge("proximity", "confirm")

    workflow.add_conditional_edges(
        "confirm",
        confirmation_router,
        {
            "mistral": "mistral",
            "cooldown_active": END,
            "monitoring": END
        }
    )

    workflow.add_conditional_edges(
        "mistral",
        mistral_router,
        {
            "alert": "alert",
            "false_alarm": END
        }
    )

    workflow.add_edge("alert", END)
    return workflow.compile()
