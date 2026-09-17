import os
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class MistralVerifier:

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY is missing from .env"
            )

        # Initialize the model and pipe it straight into StrOutputParser
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,
            request_timeout=2000,
            max_retries=0
        )
        self.chain = self.llm | StrOutputParser()

    def verify(
        self,
        frame,
        weapon_conf,
        distance,
        iou,
        threat_score=None,
        tracking_consistency=None,
        avg_score=None
    ):
        success, buffer = self._encode_frame(frame)

        if not success:
            return {
                "level": "FALSE ALARM",
                "reasoning": "Unable to process the surveillance snapshot."
            }

        image_base64 = base64.b64encode(buffer).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        prompt = """
You are the final visual verification component of STRIX,
an AI-based weapon detection and threat alerting system.

A computer vision pipeline has already detected a possible
weapon and confirmed the detection across multiple frames.

You must inspect the surveillance snapshot and determine
the actual threat level.

Consider:
- Whether the detected object visually appears to be a weapon.
- Whether the object appears to be held or associated with the person.
- The person's proximity to the detected object.
- Whether the scene appears genuinely threatening.
- The possibility that the detection is a false positive,
  such as another person, object, or visual artifact.

Computer vision evidence (numeric):
Weapon confidence: {weapon_conf:.3f}
Person-weapon distance (px): {distance:.2f}
IoU: {iou:.3f}
Threat score: {threat_score:.3f}
Tracking consistency: {tracking_consistency:.3f}
Avg confirmed score: {avg_score:.3f}

Return your answer in EXACTLY this format:
LEVEL: <HIGH | MEDIUM | LOW | FALSE ALARM>
REASONING: <short explanation>

Rules:
HIGH:
Clearly appears to be a real weapon and represents a
strong/immediate potential threat.

MEDIUM:
Potentially dangerous situation, but visual evidence or
context is not strong enough for HIGH.

LOW:
Possible weapon-related situation with limited evidence
or low apparent immediate danger.

FALSE ALARM:
The detected object does not appear to be a weapon or
the scene is clearly a false positive. And also describe whats being seen in the image. For example, "The image shows a person holding a backpack" or "The image shows a tree branch".

Do not return any other level.
Do not include a threat score in your answer.
""".format(
            weapon_conf=weapon_conf,
            distance=distance,
            iou=iou,
            threat_score=(threat_score or 0.0),
            tracking_consistency=(tracking_consistency or 0.0),
            avg_score=(avg_score or 0.0)
        )

        try:
            response_text = self.chain.invoke([
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": image_data_url
                        }
                    ]
                }
            ])
            return self._parse_response(response_text)

        except Exception as e:
            # Do not crash the entire camera loop if the remote provider is slow,
            # rate limited, or temporarily unavailable.
            print(f"[AI ANALYSIS] Provider verification failed: {e}")
            return {
                "level": "FALSE ALARM",
                "reasoning": "Verification provider timed out or failed, so no autonomous threat escalation was made."
            }

    def _encode_frame(self, frame):
        import cv2
        if frame is None:
            return False, None

        max_dim = 640
        h, w = frame.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
        success, buffer = cv2.imencode(".jpg", frame, encode_params)
        return success, buffer

    def _parse_response(self, content):
        text = str(content).strip()
        level = "FALSE ALARM"
        reasoning = text

        lines = text.splitlines()
        for line in lines:
            upper = line.upper()
            if upper.startswith("LEVEL:"):
                raw_level = line.split(":", 1)[1].strip().upper()
                valid_levels = ["HIGH", "MEDIUM", "LOW", "FALSE ALARM"]
                if raw_level in valid_levels:
                    level = raw_level
            elif upper.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()

        level = level.upper()
        if level not in {"HIGH", "MEDIUM", "LOW", "FALSE ALARM"}:
            level = "FALSE ALARM"

        return {
            "level": level,
            "reasoning": reasoning
        }
