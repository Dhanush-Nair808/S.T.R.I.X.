
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func

from app.database import (
    SessionLocal,
    ThreatEvent,
    SNAPSHOT_DIR,
)


app = FastAPI(
    title="STRIX API",
    version="1.0.0",
)


                                                              
       
                                                              

SNAPSHOT_ROOT = os.path.realpath(
    str(SNAPSHOT_DIR)
)

LIVE_FEED_PATH = os.path.join(
    str(SNAPSHOT_DIR),
    "live_feed.jpg",
)


                                                              
         
                                                              

def serialize_event(event: ThreatEvent) -> dict:
    return {
        "id": event.id,
        "event_id": event.event_id,
        "started_at": (
            event.started_at.isoformat()
            if event.started_at
            else None
        ),
        "ended_at": (
            event.ended_at.isoformat()
            if event.ended_at
            else None
        ),
        "duration_seconds": event.duration_seconds,
        "snapshot_path": event.snapshot_path,
        "mistral_level": event.mistral_level,
        "mistral_reasoning": event.mistral_reasoning,
        "email_sent": event.email_sent,
        "status": event.status,
        "created_at": (
            event.created_at.isoformat()
            if event.created_at
            else None
        ),
    }


                                                              
        
                                                              

@app.get("/api/health")
def health():

    db = SessionLocal()

    try:

        db.query(
            ThreatEvent.id
        ).limit(1).all()

        return {
            "status": "operational"
        }

    finally:
        db.close()


                                                              
           
                                                              

@app.get("/api/live-feed")
def live_feed():

    if not os.path.isfile(LIVE_FEED_PATH):

        raise HTTPException(
            status_code=404,
            detail="Live feed unavailable",
        )

    return FileResponse(
        LIVE_FEED_PATH,
        media_type="image/jpeg",
        filename="live_feed.jpg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


                                                              
        
                                                              

@app.get("/api/events")
def get_events(
    limit: int = 50,
    level: str | None = None,
    status: str | None = None,
):

    limit = max(
        1,
        min(limit, 200),
    )

    db = SessionLocal()

    try:

        query = db.query(ThreatEvent)

        if level:

            query = query.filter(
                ThreatEvent.mistral_level == level
            )

        if status:

            query = query.filter(
                ThreatEvent.status == status
            )

        events = (
            query
            .order_by(
                ThreatEvent.started_at.desc()
            )
            .limit(limit)
            .all()
        )

        return {
            "events": [
                serialize_event(event)
                for event in events
            ]
        }

    finally:
        db.close()


                                                              
              
                                                              

@app.get("/api/events/{event_id}")
def get_event(event_id: str):

    db = SessionLocal()

    try:

        event = (
            db.query(ThreatEvent)
            .filter(
                ThreatEvent.event_id == event_id
            )
            .first()
        )

        if event is None:

            raise HTTPException(
                status_code=404,
                detail="Event not found",
            )

        return serialize_event(event)

    finally:
        db.close()


                                                              
          
                                                              

@app.get("/api/events/{event_id}/snapshot")
def get_snapshot(event_id: str):

    db = SessionLocal()

    try:

        event = (
            db.query(ThreatEvent)
            .filter(
                ThreatEvent.event_id == event_id
            )
            .first()
        )

        if event is None:

            raise HTTPException(
                status_code=404,
                detail="Event not found",
            )

        if not event.snapshot_path:

            raise HTTPException(
                status_code=404,
                detail="No snapshot available",
            )

        real_snapshot = os.path.realpath(
            event.snapshot_path
        )

        if not real_snapshot.startswith(
            SNAPSHOT_ROOT + os.sep
        ):

            raise HTTPException(
                status_code=403,
                detail="Invalid snapshot path",
            )

        if not os.path.isfile(
            real_snapshot
        ):

            raise HTTPException(
                status_code=404,
                detail="Snapshot file not found",
            )

        return FileResponse(
            real_snapshot,
            media_type="image/jpeg",
            filename=os.path.basename(
                real_snapshot
            ),
            headers={
                "Cache-Control": "no-store",
            },
        )

    finally:
        db.close()


                                                              
           
                                                              

@app.get("/api/stats")
def get_stats():

    db = SessionLocal()

    try:

        total = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .scalar()
            or 0
        )

        active = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.status == "ACTIVE"
            )
            .scalar()
            or 0
        )

        ended = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.status == "ENDED"
            )
            .scalar()
            or 0
        )

        high = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.mistral_level == "HIGH"
            )
            .scalar()
            or 0
        )

        medium = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.mistral_level == "MEDIUM"
            )
            .scalar()
            or 0
        )

        low = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.mistral_level == "LOW"
            )
            .scalar()
            or 0
        )

        false_alarm = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.mistral_level
                == "FALSE ALARM"
            )
            .scalar()
            or 0
        )

        emails = (
            db.query(
                func.count(
                    ThreatEvent.id
                )
            )
            .filter(
                ThreatEvent.email_sent.is_(True)
            )
            .scalar()
            or 0
        )

        return {
            "total_events": total,
            "active_events": active,
            "ended_events": ended,
            "high": high,
            "medium": medium,
            "low": low,
            "false_alarm": false_alarm,
            "emails_sent": emails,
        }

    finally:
        db.close()
