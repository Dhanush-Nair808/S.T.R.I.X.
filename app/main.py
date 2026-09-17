import os
import time
import cv2

from graph import build_graph
from detection import draw_detections
from database import init_database, SNAPSHOT_DIR

LIVE_FEED_PATH = os.path.join(str(SNAPSHOT_DIR), "live_feed.jpg")

def write_live_frame(frame):
    os.makedirs(str(SNAPSHOT_DIR), exist_ok=True)
    temp_path = os.path.join(str(SNAPSHOT_DIR), "live_feed_tmp.jpg")
    success, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not success:
        return
    try:
        with open(temp_path, "wb") as file:
            file.write(encoded.tobytes())
        os.replace(temp_path, LIVE_FEED_PATH)
    except OSError:
        pass

def main():
    init_database()
    graph = build_graph()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return

    print("STRIX LangGraph running...")
    print(f"Live feed: {LIVE_FEED_PATH}")
    print("Press 'q' to quit.")

    cooldown_until = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Could not read camera frame.")
                break

            current_time = time.monotonic()
            if current_time < cooldown_until:
                for _ in range(5):
                    cap.grab()
                time.sleep(0.1)
                continue

            initial_state = {
                "frame": frame,
                "persons": [],
                "weapons": [],
                "pairs": [],
                "current_score": 0.0,
                "avg_score": 0.0,
                "confirmed": False,
                "status": "Starting...",
                "mistral_decision": "NOT_CHECKED",
                "mistral_reasoning": "",
            }

            result = graph.invoke(initial_state)

            if result.get("status") == "cooldown_active":
                cooldown_until = time.monotonic() + 1.5
                print("[THROTTLING] Cooldown engaged. Camera loop paused.")

            processed_frame = draw_detections(
                frame,
                result["persons"],
                result["weapons"],
                result["pairs"],
            )

            cv2.putText(
                processed_frame,
                f"Current: {result['current_score']:.2f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                processed_frame,
                f"Average: {result['avg_score']:.2f}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            status_color = (0, 0, 255) if result["confirmed"] else (0, 255, 0)
            cv2.putText(
                processed_frame,
                result["status"],
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                status_color,
                3,
            )

            write_live_frame(processed_frame)
            cv2.imshow("STRIX - LangGraph", processed_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
