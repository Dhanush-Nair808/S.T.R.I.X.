from collections import deque
import numpy as np

class MultiFrameConfirmer:
    def __init__(
        self,
        window_size=7,                                 
        confirm_threshold=0.68,                    
        min_hits=5,                              
        min_avg_score=0.62                                  
    ):
        self.window_size = window_size
        self.confirm_threshold = confirm_threshold
        self.min_hits = min_hits
        self.min_avg_score = min_avg_score
        self.scores = deque(maxlen=window_size)

    def update(self, threat_score):
        self.scores.append(threat_score)

        if len(self.scores) < self.min_hits:
            return False, 0.0

        hits = sum(1 for s in self.scores if s >= self.confirm_threshold)
        avg_score = float(np.mean(self.scores))

        confirmed = (hits >= self.min_hits) and (avg_score >= self.min_avg_score)
        return confirmed, round(avg_score, 3)

    def reset(self):
        self.scores.clear()