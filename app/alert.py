import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from dotenv import load_dotenv
from datetime import datetime

import cv2


load_dotenv()


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