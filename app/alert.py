import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from dotenv import load_dotenv
from datetime import datetime

try:
    import cv2
except ImportError:
    cv2 = None


load_dotenv()


def _is_valid_snapshot(path):
    if not path or not os.path.isfile(path):
        return False

    try:
        if os.path.getsize(path) < 4096:
            return False

        if cv2 is not None:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None or img.size == 0:
                return False
            if img.mean() < 2.0:
                return False

        return True
    except Exception:
        return False


def _latest_event_snapshot_path():
    snapshot_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "app",
            "data",
            "snapshots",
        )
    )
    if not os.path.isdir(snapshot_dir):
        return None

    snapshots = []
    for file_name in os.listdir(snapshot_dir):
        lowered = file_name.lower()
        if (lowered.endswith(".jpg") or lowered.endswith(".jpeg")) and file_name.lower() not in {"live_feed.jpg", "live_feed_tmp.jpg"}:
            full_path = os.path.join(snapshot_dir, file_name)
            if _is_valid_snapshot(full_path):
                snapshots.append(full_path)

    if not snapshots:
        return None

    return max(snapshots, key=lambda p: os.path.getmtime(p))


def dispatch_unit_alert(unit, threat_level, channel, message, snapshot_path=None):
    channel = (channel or "email").lower()
    contact_map = {
        "email": unit.email,
        "sms": unit.phone,
        "whatsapp": unit.whatsapp,
    }

    target = contact_map.get(channel)
    if not target:
        return False, f"No {channel} contact configured for {unit.name}."

    if channel == "email":
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        if sender and password:
            try:
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = target
                msg["Subject"] = f"STRIX Alert - {unit.name} / {threat_level}"
                body = (
                    f"Unit: {unit.name}\n"
                    f"Leader: {unit.leader_name}\n"
                    f"Threat Level: {threat_level}\n"
                    f"Message: {message or 'Threat assignment pending review.'}\n"
                    f"Zone: {unit.zone or 'Unassigned'}\n"
                    f"Evidence: Attached latest STRIX snapshot.\n"
                )
                msg.attach(MIMEText(body, "plain"))

                resolved_snapshot = snapshot_path if _is_valid_snapshot(snapshot_path) else None
                if resolved_snapshot is None:
                    resolved_snapshot = _latest_event_snapshot_path()

                if resolved_snapshot and os.path.isfile(resolved_snapshot):
                    with open(resolved_snapshot, "rb") as image_file:
                        image_data = image_file.read()
                    image_part = MIMEImage(image_data, name=os.path.basename(resolved_snapshot))
                    msg.attach(image_part)

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender, password)
                    server.send_message(msg)
                return True, f"Email dispatched to {unit.name} ({target})."
            except Exception as exc:
                print(f"[ALERT] Email dispatch failed: {exc}")
                return False, str(exc)

        print(f"[ALERT] Simulated email dispatch to {unit.name} ({target})")
        return True, f"Simulated email dispatched to {unit.name} ({target})."

    if channel in {"sms", "whatsapp"}:
        print(f"[ALERT] {channel.upper()} message sent to {unit.name}: {message or 'Threat assigned'}")
        return True, f"{channel.upper()} message dispatched to {unit.name} ({target})."

    return False, f"Unsupported dispatch channel: {channel}"


class EmailAlerter:

    def __init__(self):

        self.sender = os.getenv(
            "EMAIL_SENDER"
        )

        self.password = os.getenv(
            "EMAIL_PASSWORD"
        )

        self.receiver = os.getenv(
            "EMAIL_RECEIVER"
        )

                                
        self.last_sent = None
        self.cooldown_seconds = 45

                                                
              
                                                

    def can_send(self):

        if self.last_sent is None:
            return True

        elapsed = (
            datetime.now() - self.last_sent
        ).total_seconds()

        return elapsed >= self.cooldown_seconds

                                                
                
                                                

    def send_alert(
        self,
        frame,
        level,
        reasoning
    ):

        if cv2 is None:
            print("[ALERT] OpenCV is not installed; snapshot alert cannot be sent.")
            return False

        if not self.can_send():

            print(
                "[ALERT] Cooldown active. Email skipped."
            )

            return False

        if not all([
            self.sender,
            self.password,
            self.receiver
        ]):

            print(
                "[ALERT] Missing email credentials in .env"
            )

            return False

        try:

                                                
                             
                                                

            success, buffer = cv2.imencode(
                ".jpg",
                frame
            )

            if not success:
                print(
                    "[ALERT] Failed to encode snapshot."
                )
                return False

            image_data = buffer.tobytes()

                                                
                   
                                                

            msg = MIMEMultipart()

            msg["From"] = self.sender
            msg["To"] = self.receiver

            msg["Subject"] = (
                f"STRIX Alert - {level}"
            )

            body = f"""
STRIX WEAPON DETECTION SYSTEM
================================

Threat Classification: {level}

Time:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

MISTRAL ASSESSMENT
------------------

{reasoning}

The threat was confirmed across multiple
surveillance frames before visual verification.

A snapshot from the confirmed event is attached.

================================
STRIX AI Security System
"""

            msg.attach(
                MIMEText(
                    body,
                    "plain"
                )
            )

            msg.attach(
                MIMEImage(
                    image_data,
                    name="strix_snapshot.jpg"
                )
            )

                                                
                  
                                                

            with smtplib.SMTP_SSL(
                "smtp.gmail.com",
                465
            ) as server:

                server.login(
                    self.sender,
                    self.password
                )

                server.send_message(msg)

            self.last_sent = datetime.now()

            print(
                f"[ALERT] {level} email sent successfully."
            )

            return True

        except Exception as e:

            print(
                f"[ALERT] Failed to send email: {e}"
            )

            return False