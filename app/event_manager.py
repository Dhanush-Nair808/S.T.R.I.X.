import time
from datetime import datetime
import os
import cv2

from database import (
    create_event,
    update_snapshot,
    update_mistral_result,
    update_email_status,
    end_event,
    SNAPSHOT_DIR
)

class ThreatEventManager:

    def __init__(
        self,
        event_timeout=5.0,
        mistral_cooldown=60.0
    ):

                                                                  
                     
                                                                  

        self.event_active = False
        self.mistral_processed = False
        self.alert_sent = False

        self.current_event_id = None
        self.event_counter = 0

                                                                  
                
                                                                  

        self.event_timeout = event_timeout
        self.mistral_cooldown = mistral_cooldown

        self.last_confirmed_time = None
        self.last_mistral_time = None

                                                                  
                       
                                                                  

    def new_event(self):

        self.event_active = True
        self.mistral_processed = False
        self.alert_sent = False

        self.last_confirmed_time = time.monotonic()

                                                                  
                           
                                                                  

        self.event_counter += 1

        event_id = (
            f"STRIX-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            f"-{self.event_counter:04d}"
        )

        self.current_event_id = event_id

                                                                  
                                
                                                                  

        create_event(
            event_id=event_id,
            started_at=datetime.now()
        )

        print(
            f"[EVENT] New event: {event_id}"
        )
    def save_snapshot(self, frame):

        if self.current_event_id is None:
            return None

        if frame is None:
            return None

        filename = (
            f"{self.current_event_id}.jpg"
        )

        snapshot_path = os.path.join(
            SNAPSHOT_DIR,
            filename
        )

        success = cv2.imwrite(
            snapshot_path,
            frame
        )

        if not success:

            print(
                "[EVENT] Failed to save snapshot."
            )

            return None

        update_snapshot(
            event_id=self.current_event_id,
            snapshot_path=snapshot_path
        )

        print(
            f"[EVENT] Snapshot saved: "
            f"{snapshot_path}"
        )

        return snapshot_path
                                                                  
                            
                                                                  

    def update(self, confirmed: bool):

        now = time.monotonic()

                                                                  
                   
                                                                  

        if confirmed:

            self.last_confirmed_time = now

                                          
            if not self.event_active:

                self.new_event()

            return

                                                                  
                        
                                                                  

        if not self.event_active:
            return

        if self.last_confirmed_time is None:
            return

                                                                  
                                    
                                                                  

        elapsed = (
            now - self.last_confirmed_time
        )

                                                                  
                           
                                                                  

        if elapsed < self.event_timeout:
            return

                                                                  
                     
                                                                  

        event_id = self.current_event_id

        print(
            f"[EVENT] Event ended: {event_id}"
        )

        if event_id is not None:

            end_event(
                event_id=event_id,
                ended_at=datetime.now()
            )

        self.reset()

                                                                  
                               
                                                                  

    def should_verify(
        self,
        confirmed: bool, frame=None
    ) -> bool:

        now = time.monotonic()

                                                                  
                                      
                                                                  

        self.update(confirmed)

                                                                  
                                    
                                                                  

        if not confirmed:
            return False

                                                                  
                                              
                                                                  

        if self.mistral_processed:
            return False

                                                                  
                                 
                                                                  

        if self.last_mistral_time is not None:

            elapsed = (
                now - self.last_mistral_time
            )

            if elapsed < self.mistral_cooldown:

                remaining = (
                    self.mistral_cooldown - elapsed
                )

                print(
                    f"[MISTRAL] Cooldown active: "
                    f"{remaining:.1f}s remaining"
                )

                return False

                                                                  
                         
                                                                  

        return True

                                                                  
                            
                                                                  

    def mark_mistral_processed(
        self,
        level,
        reasoning
    ):

        self.mistral_processed = True
        self.last_mistral_time = time.monotonic()

                                                                  
                                         
                                                                  

        if self.current_event_id is not None:

            update_mistral_result(
                event_id=self.current_event_id,
                level=level,
                reasoning=reasoning
            )

        print(
            "[MISTRAL] Event verification complete"
        )

                                                                  
                    
                                                                  

    def should_alert(
        self,
        mistral_level: str
    ) -> bool:

                                                                  
                                
                                                                  

        if mistral_level == "FALSE ALARM":

            if self.current_event_id is not None:

                update_email_status(
                    event_id=self.current_event_id,
                    sent=False
                )

            return False

                                                                  
                                        
                                                                  

        if self.alert_sent:
            return False

        self.alert_sent = True

        return True

                                                                  
                         
                                                                  

    def mark_alert_result(
        self,
        sent: bool
    ):

        if self.current_event_id is not None:

            update_email_status(
                event_id=self.current_event_id,
                sent=sent
            )

                                                                  
                         
                                                                  

    def reset(self):

        self.event_active = False
        self.mistral_processed = False
        self.alert_sent = False

        self.current_event_id = None
        self.last_confirmed_time = None