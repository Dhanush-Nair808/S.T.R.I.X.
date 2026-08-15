import numpy as np

def calculate_iou(boxA, boxB):
    """Intersection over Union between two boxes (x1,y1,x2,y2)"""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    boxA_area = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxB_area = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    union = boxA_area + boxB_area - inter_area
    if union == 0:
        return 0.0
    return inter_area / union


def calculate_distance(centerA, centerB):
    """Euclidean distance between two centers"""
    return np.sqrt((centerA[0] - centerB[0])**2 + (centerA[1] - centerB[1])**2)


def compute_threat_score(weapon_conf, distance, iou, max_distance=350):
    """
    Stricter threat score.
    """
    proximity_score = max(0.0, 1.0 - (distance / max_distance))
    holding_score = min(1.0, iou * 2.5)

                                          
    threat_score = (
        0.40 * weapon_conf +
        0.35 * proximity_score +
        0.25 * holding_score
    )
    return round(min(1.0, threat_score), 3)


def find_person_weapon_pairs(persons, weapons, max_distance=400):
    """
    For every weapon, find the nearest person and compute metrics.
    Returns list of pair dicts.
    """
    pairs = []

    for weapon in weapons:
        nearest_person = None
        min_dist = float("inf")

        for person in persons:
            dist = calculate_distance(person["center"], weapon["center"])
            if dist < min_dist:
                min_dist = dist
                nearest_person = person

        if nearest_person is None:
            continue

        iou = calculate_iou(nearest_person["box"], weapon["box"])
        threat = compute_threat_score(
            weapon_conf=weapon["confidence"],
            distance=min_dist,
            iou=iou,
            max_distance=max_distance
        )

        pairs.append({
            "person": nearest_person,
            "weapon": weapon,
            "distance": min_dist,
            "iou": round(iou, 3),
            "threat_score": threat
        })

    return pairs