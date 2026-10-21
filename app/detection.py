from pathlib import Path

from ultralytics import YOLO
import cv2
import numpy as np
import os

# Flexible detector configuration supporting either:
# - a single combined model that outputs both person & weapon classes
# - OR separate person (pretrained COCO) + weapon (trained gun-only) models
# Behavior is chosen automatically based on WEAPON_MODEL_PATH being set.

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent


def resolve_model_path(*parts: str) -> str:
    candidates = [
        PROJECT_ROOT.joinpath(*parts),
        APP_DIR.joinpath(*parts),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(PROJECT_ROOT.joinpath(*parts))


# Path to combined model (used when no WEAPON_MODEL_PATH is set)
MODEL_PATH = resolve_model_path("models", "gun_best.pt")

# Optional: separate person and weapon model paths. If WEAPON_MODEL_PATH is set
# and the file exists, the detector will use two-model mode.
PERSON_MODEL_PATH = resolve_model_path("app", "yolov8n.pt")
WEAPON_MODEL_PATH = resolve_model_path("models", "gun_best.pt")

# Class ids and thresholds
PERSON_CLASS_ID = 0
PERSON_CONF_THRESHOLD = 0.3
WEAPON_CLASS_IDS = [1]  # single-model combined mapping; not used in two-model mode
WEAPON_CONF_THRESHOLD = 0.3

SIMULATE_SECOND_PERSON_AS_WEAPON = False


class WeaponPersonDetector:
    """Detector that flexibly supports single combined model or two-model setup.

    Rules:
    - If WEAPON_MODEL_PATH is set (and file exists), use two-model mode:
        person model = PERSON_MODEL_PATH
        weapon model = WEAPON_MODEL_PATH
      In two-model mode, persons are filtered by PERSON_CLASS_ID from person model,
      and weapons are any detections from the weapon model above WEAPON_CONF_THRESHOLD.

    - Otherwise, use single-model mode: load MODEL_PATH and extract persons/weapons
      by class ids (PERSON_CLASS_ID and WEAPON_CLASS_IDS).
    """

    def __init__(self, model_path: str | None = None):
        self.model = None
        self.person_model = None
        self.weapon_model = None
        self.two_model = False

        resolved_model_path = model_path or MODEL_PATH

        if WEAPON_MODEL_PATH and os.path.exists(WEAPON_MODEL_PATH):
            self.person_model = YOLO(PERSON_MODEL_PATH)
            self.weapon_model = YOLO(WEAPON_MODEL_PATH)
            self.two_model = True
        elif os.path.exists(resolved_model_path):
            self.model = YOLO(resolved_model_path)
        else:
            raise FileNotFoundError(f"Detection model not found: {resolved_model_path}")

    def _parse_results(self, results, class_filter=None, conf_threshold=0.5):
        dets = []
        if results.boxes is None:
            return dets

        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy().astype(int)

        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            if conf < conf_threshold:
                continue
            if class_filter is not None and cls_id not in class_filter:
                continue
            x1, y1, x2, y2 = map(int, box)
            dets.append({
                "box": (x1, y1, x2, y2),
                "confidence": float(conf),
                "class_id": int(cls_id),
                "center": ((x1 + x2) // 2, (y1 + y2) // 2)
            })
        return dets

    def detect(self, frame):
        persons = []
        weapons = []

        if self.two_model:
            # person detections from the person model
            pres = self.person_model(frame, verbose=False)[0]
            persons = self._parse_results(pres, class_filter=[PERSON_CLASS_ID], conf_threshold=PERSON_CONF_THRESHOLD)
            # weapon detections from the dedicated weapon model (accept any class)
            wets = self.weapon_model(frame, verbose=False)[0]
            weapons = self._parse_results(wets, class_filter=None, conf_threshold=WEAPON_CONF_THRESHOLD)
        else:
            # single combined model
            res = self.model(frame, verbose=False)[0]
            persons = self._parse_results(res, class_filter=[PERSON_CLASS_ID], conf_threshold=PERSON_CONF_THRESHOLD)
            weapons = self._parse_results(res, class_filter=WEAPON_CLASS_IDS if WEAPON_CLASS_IDS else None, conf_threshold=WEAPON_CONF_THRESHOLD)

        # development fallback
        if SIMULATE_SECOND_PERSON_AS_WEAPON and (not weapons) and len(persons) >= 2:
            fake_weapon = persons[1].copy()
            fake_conf = persons[1].get("confidence", 0.65)
            fake_weapon["confidence"] = float(fake_conf)
            fake_weapon["simulated"] = True
            weapons = [fake_weapon]
            persons = [persons[0]]

        return persons, weapons


def draw_detections(frame, persons, weapons, pairs=None):
    """
    Draw person (green) and weapon (red) boxes.
    Optionally draw lines between person-weapon pairs.
    """

    for p in persons:
        x1, y1, x2, y2 = p["box"]
        conf = p["confidence"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"Person {conf:.2f}", (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    for w in weapons:
        x1, y1, x2, y2 = w["box"]
        conf = w["confidence"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"Weapon {conf:.2f}", (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    if pairs:
        for pair in pairs:
            p_center = pair["person"]["center"]
            w_center = pair["weapon"]["center"]
            dist = pair["distance"]
            iou = pair["iou"]
            score = pair["threat_score"]

            cv2.line(frame, p_center, w_center, (0, 255, 255), 2)
            mid_x = (p_center[0] + w_center[0]) // 2
            mid_y = (p_center[1] + w_center[1]) // 2
            cv2.putText(frame, f"D:{int(dist)} IoU:{iou:.2f} T:{score:.2f}",
                        (mid_x - 40, mid_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    return frame