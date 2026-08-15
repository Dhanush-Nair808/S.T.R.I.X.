import os
import base64
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI


load_dotenv()


class MistralVerifier:

    def __init__(self):

        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY is missing from .env"
            )

        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            temperature=0,
            api_key=api_key
        )

    def verify(
        self,
        frame,
        weapon_conf,
        distance,
        iou
    ):

                                                    
                                              
                                                    

        success, buffer = self._encode_frame(frame)

        if not success:
            return {
                "level": "FALSE ALARM",
                "reasoning": "Unable to process the surveillance snapshot."
            }

        image_base64 = base64.b64encode(
            buffer
        ).decode("utf-8")

        image_data_url = (
            f"data:image/jpeg;base64,{image_base64}"
        )

                                                    
                        
                                                    

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

Computer vision evidence:

Weapon confidence: {weapon_conf:.3f}
Person-weapon distance: {distance:.2f}
IoU: {iou:.3f}

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
the scene is clearly a false positive.

Do not return any other level.
Do not include a threat score in your answer.
""".format(
            weapon_conf=weapon_conf,
            distance=distance,
            iou=iou
        )

                                                    
                                      
                                                    

        response = self.llm.invoke([
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

        return self._parse_response(
            response.content
        )

                                                
                         
                                                

    def _encode_frame(self, frame):

        import cv2

        success, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        return success, buffer

                                                
                            
                                                

    def _parse_response(self, content):

        text = content.strip()

        level = "FALSE ALARM"
        reasoning = text

        lines = text.splitlines()

        for line in lines:

            upper = line.upper()

            if upper.startswith("LEVEL:"):

                raw_level = line.split(
                    ":", 1
                )[1].strip().upper()

                valid_levels = [
                    "HIGH",
                    "MEDIUM",
                    "LOW",
                    "FALSE ALARM"
                ]

                if raw_level in valid_levels:
                    level = raw_level

            elif upper.startswith("REASONING:"):

                reasoning = line.split(
                    ":",
                    1
                )[1].strip()

        return {
            "level": level,
            "reasoning": reasoning
        }