from ultralytics import YOLO
import cv2
import numpy as np

class WeaponPersonDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.person_class_id = 0               

    def detect(self, frame):
        """
        Returns:
            persons: list of dicts {"box": (x1,y1,x2,y2), "confidence": float}
            weapons: list of dicts (empty for now, will be filled later)
        """
        results = self.model(frame, verbose=False)[0]

        persons = []
        weapons = []

        if results.boxes is None:
            return persons, weapons

        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy().astype(int)

        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = map(int, box)

            if cls_id == self.person_class_id and conf > 0.65:
                persons.append({
                    "box": (x1, y1, x2, y2),
                    "confidence": float(conf),
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2)
                })

                                                                       

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