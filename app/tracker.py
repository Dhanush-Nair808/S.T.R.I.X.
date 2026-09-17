from collections import deque
import numpy as np


class SimpleTracker:
    """
    Very small IoU-based tracker that assigns incremental IDs to detections
    and computes a simple tracking_consistency metric = hits / age.

    - update(detections): detections is a list of dicts each containing at least
      'box': (x1,y1,x2,y2). The method mutates each detection to include
      'track_id' and 'tracking_consistency' and returns a list of active tracks.

    This is intentionally lightweight and designed to reduce flicker-based
    false positives by preferring objects seen across multiple frames.
    """

    def __init__(self, iou_threshold=0.3, max_age=5):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.next_id = 1
        self.tracks = {}  # id -> track dict

    @staticmethod
    def _iou(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        inter_w = max(0, xB - xA)
        inter_h = max(0, yB - yA)
        inter_area = inter_w * inter_h

        boxA_area = max(0, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
        boxB_area = max(0, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

        union = boxA_area + boxB_area - inter_area
        if union <= 0:
            return 0.0
        return inter_area / union

    def update(self, detections):
        """Match detections to existing tracks (greedy by IoU), update tracks,
        create new tracks for unmatched detections, and expire old tracks.

        Mutates each detection with 'track_id' and 'tracking_consistency'.
        Returns list of current track dicts.
        """
        # Prepare list of unmatched detections and track ids
        unmatched_dets = list(range(len(detections)))
        track_ids = list(self.tracks.keys())

        # Build IoU matrix
        iou_pairs = []  # (iou, track_id, det_idx)
        for tid in track_ids:
            tbox = self.tracks[tid]["bbox"]
            for didx in unmatched_dets:
                dbox = detections[didx]["box"]
                iou_val = self._iou(tbox, dbox)
                iou_pairs.append((iou_val, tid, didx))

        # Greedy match by highest IoU
        iou_pairs.sort(reverse=True, key=lambda x: x[0])
        matched_tracks = set()
        matched_dets = set()

        for iou_val, tid, didx in iou_pairs:
            if iou_val < self.iou_threshold:
                break
            if tid in matched_tracks or didx in matched_dets:
                continue
            # assign
            matched_tracks.add(tid)
            matched_dets.add(didx)

            detections[didx]["track_id"] = tid
            # update track
            tr = self.tracks[tid]
            tr["bbox"] = detections[didx]["box"]
            tr["hits"] += 1
            tr["misses"] = 0
            tr["age"] += 1

        # Unmatched detections -> create new tracks
        for didx in range(len(detections)):
            if didx in matched_dets:
                continue
            det = detections[didx]
            tid = self.next_id
            self.next_id += 1
            detections[didx]["track_id"] = tid
            self.tracks[tid] = {
                "id": tid,
                "bbox": det["box"],
                "hits": 1,
                "misses": 0,
                "age": 1,
            }

        # Tracks not matched -> increment misses and age
        for tid in list(self.tracks.keys()):
            if tid in matched_tracks:
                continue
            tr = self.tracks[tid]
            tr["misses"] += 1
            tr["age"] += 1
            # expire
            if tr["misses"] > self.max_age:
                del self.tracks[tid]

        # Compute tracking_consistency and attach to detections
        for det in detections:
            tid = det.get("track_id")
            if tid is None:
                det["tracking_consistency"] = 0.0
                continue
            tr = self.tracks.get(tid)
            if tr is None:
                det["tracking_consistency"] = 0.0
            else:
                consistency = tr["hits"] / max(1, tr["age"]) if tr["age"] > 0 else 0.0
                det["tracking_consistency"] = round(min(1.0, consistency), 3)

        # Return snapshot of tracks
        return list(self.tracks.values())


class MultiFrameConfirmer:
    def __init__(
        self,
        window_size=6,
        confirm_threshold=0.46,
        min_hits=3,
        min_avg_score=0.40,
        instant_confirm_threshold=0.80
    ):
        self.window_size = window_size
        self.confirm_threshold = confirm_threshold
        self.min_hits = min_hits
        self.min_avg_score = min_avg_score
        self.instant_confirm_threshold = instant_confirm_threshold
        self.scores = deque(maxlen=window_size)

    def update(self, threat_score):
        self.scores.append(threat_score)

        if len(self.scores) == 0:
            return False, 0.0

        avg_score = float(np.mean(self.scores))
        recent_hits = sum(1 for s in self.scores if s >= self.confirm_threshold)

        # Do not require the object to remain perfectly still for many frames.
        # A strong threat score from proximity + weapon confidence should still
        # trigger verification even while the target is moving.
        if threat_score >= self.instant_confirm_threshold and avg_score >= self.min_avg_score:
            return True, round(avg_score, 3)

        if len(self.scores) < self.min_hits:
            return False, round(avg_score, 3)

        confirmed = (recent_hits >= self.min_hits) and (avg_score >= self.min_avg_score)
        return confirmed, round(avg_score, 3)

    def reset(self):
        self.scores.clear()