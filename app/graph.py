from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END

import numpy as np

from detection import WeaponPersonDetector
from proximity import find_person_weapon_pairs
from tracker import MultiFrameConfirmer
from alert import EmailAlerter
from mistral_verification import MistralVerifier
from event_manager import ThreatEventManager


                                                              
                
                                                              

detector = WeaponPersonDetector()

confirmer = MultiFrameConfirmer(
    window_size=7,
    confirm_threshold=0.2,                  
    min_hits=5,
    min_avg_score=0.2                       
)

verifier = MistralVerifier()
alerter = EmailAlerter()

event_manager = ThreatEventManager(
    event_timeout=5.0,
    mistral_cooldown=60.0
)


                                                              
       
                                                              

class STRIXState(TypedDict):

    frame: Optional[np.ndarray]

    persons: List[dict]
    weapons: List[dict]
    pairs: List[dict]

    current_score: float
    avg_score: float

    confirmed: bool
    status: str

    mistral_decision: str
    mistral_reasoning: str


                                                              
           
                                                              

def detection_node(state: STRIXState) -> dict:

    frame = state["frame"]

    persons, weapons = detector.detect(frame)

                                                              
                            
                                                             
                                                              

    if len(persons) >= 2:

        fake_weapon = persons[1].copy()
        fake_weapon["confidence"] = 0.85

        weapons = [fake_weapon]
        persons = [persons[0]]

    else:

        weapons = []

    return {
        "persons": persons,
        "weapons": weapons
    }


                                                              
                          
                                                              

def proximity_node(state: STRIXState) -> dict:

    persons = state["persons"]
    weapons = state["weapons"]

    pairs = find_person_weapon_pairs(
        persons,
        weapons
    )

    current_score = 0.0

    if pairs:

        best = max(
            pairs,
            key=lambda x: x["threat_score"]
        )

        current_score = best["threat_score"]

    return {
        "pairs": pairs,
        "current_score": current_score
    }


                                                              
                          
                                                              

def confirmation_node(state: STRIXState) -> dict:

    current_score = state["current_score"]

    confirmed, avg_score = confirmer.update(
        current_score
    )

    status = (
        "THREAT CONFIRMED"
        if confirmed
        else "Monitoring..."
    )

    return {
        "confirmed": confirmed,
        "avg_score": avg_score,
        "status": status
    }


                                                              
                     
                                                              

def confirmation_router(state: STRIXState) -> str:

    confirmed = state["confirmed"]
    frame = state["frame"]

                                                              
                           
     
                          
                              
                         
                                  
                                                              

    if event_manager.should_verify(
        confirmed,
        frame
    ):

        print(
            "[EVENT] New event -> Mistral"
        )

        return "mistral"

                                                              
                                                   
     
                                    
                                      
                                                              

    if confirmed:

        print(
            "[EVENT] Same event / "
            "Mistral cooldown -> Skip"
        )

    return "monitoring"


                                                              
                      
                                                              

def mistral_verification_node(
    state: STRIXState
) -> dict:

    pairs = state["pairs"]

                                                              
             
                                                              

    if not pairs:

        event_manager.mark_mistral_processed(
            level="FALSE ALARM",
            reasoning=(
                "No valid person-weapon relationship "
                "was available for verification."
            )
        )

        return {
            "mistral_decision": "FALSE ALARM",
            "mistral_reasoning": (
                "No valid person-weapon relationship "
                "was available for verification."
            ),
            "status": "Mistral: FALSE ALARM"
        }

                                                              
                    
                                                              

    best = max(
        pairs,
        key=lambda x: x["threat_score"]
    )

                                                              
                                                 
     
                                                      
                                   
                                                              

    result = verifier.verify(
        frame=state["frame"],
        weapon_conf=best["weapon"]["confidence"],
        distance=best["distance"],
        iou=best["iou"]
    )

    level = result["level"]
    reasoning = result["reasoning"]

    print(
        f"[MISTRAL] Level: {level}"
    )

    print(
        f"[MISTRAL] Reasoning: {reasoning}"
    )

                                                              
                                                            
     
                                           
                                                              

    event_manager.mark_mistral_processed(
        level=level,
        reasoning=reasoning
    )

    return {
        "mistral_decision": level,
        "mistral_reasoning": reasoning,
        "status": f"Mistral: {level}"
    }


                                                              
                
                                                              

def mistral_router(state: STRIXState) -> str:

    level = state["mistral_decision"]

    if level == "FALSE ALARM":

        return "false_alarm"

    return "alert"


                                                              
       
                                                              

def alert_node(state: STRIXState) -> dict:

    level = state["mistral_decision"]
    reasoning = state["mistral_reasoning"]

                                                              
                                  
                                                              

    if not event_manager.should_alert(level):

        return {
            "status": "Alert skipped"
        }

    frame = state["frame"]

                                                              
                
                                                              

    success = alerter.send_alert(
        frame=frame,
        level=level,
        reasoning=reasoning
    )

                                                              
                                   
                                                              

    event_manager.mark_alert_result(
        success
    )

    status = (
        "ALERT SENT"
        if success
        else "ALERT FAILED / COOLDOWN"
    )

    return {
        "status": status
    }


                                                              
             
                                                              

def build_graph():

    workflow = StateGraph(
        STRIXState
    )

    workflow.add_node(
        "detect",
        detection_node
    )

    workflow.add_node(
        "proximity",
        proximity_node
    )

    workflow.add_node(
        "confirm",
        confirmation_node
    )

    workflow.add_node(
        "mistral",
        mistral_verification_node
    )

    workflow.add_node(
        "alert",
        alert_node
    )

    workflow.set_entry_point(
        "detect"
    )

    workflow.add_edge(
        "detect",
        "proximity"
    )

    workflow.add_edge(
        "proximity",
        "confirm"
    )

    workflow.add_conditional_edges(
        "confirm",
        confirmation_router,
        {
            "mistral": "mistral",
            "monitoring": END
        }
    )

    workflow.add_conditional_edges(
        "mistral",
        mistral_router,
        {
            "alert": "alert",
            "false_alarm": END
        }
    )

    workflow.add_edge(
        "alert",
        END
    )

    return workflow.compile()