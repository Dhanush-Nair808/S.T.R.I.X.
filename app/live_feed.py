
import threading


_latest_frame = None
_frame_lock = threading.Lock()


def set_latest_frame(frame_bytes: bytes):
    """Store the latest JPEG-encoded camera frame."""
    global _latest_frame

    with _frame_lock:
        _latest_frame = frame_bytes


def get_latest_frame():
    """Return the latest JPEG frame, or None if unavailable."""
    with _frame_lock:
        return _latest_frame

