
import os

import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func

from app.alert import dispatch_unit_alert
from app.database import (
    SessionLocal,
    ThreatEvent,
    Unit,
    UnitAssignment,
    SNAPSHOT_DIR,
    create_assignment,
    create_unit,
    delete_assignment,
    delete_event as delete_event_record,
    delete_unit,
    get_unit,
    get_setting,
    set_setting,
    init_database,
    list_assignments,
    list_units,
    seed_default_units,
    update_assignment_status,
    update_unit,
)


init_database()
seed_default_units()


app = FastAPI(
    title="STRIX API",
    version="1.0.0",
)


class UnitAssignmentRequest(BaseModel):
    event_id: str = Field(default="manual-assign")
    unit_id: int
    threat_level: str = "HIGH"
    channel: str = "email"
    priority: str = "normal"
    note: str | None = None
    message: str | None = None


class UnitCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    leader_name: str = Field(default="Unit Lead", max_length=100)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    whatsapp: str | None = Field(default=None, max_length=50)
    zone: str | None = Field(default=None, max_length=100)


class StatusUpdateRequest(BaseModel):
    status: str = "sent"
    message: str | None = None
    note: str | None = None


class AssignmentDeleteRequest(BaseModel):
    confirm: bool = False


class UnitUpdateRequest(BaseModel):
    leader_name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    whatsapp: str | None = Field(default=None, max_length=50)
    zone: str | None = Field(default=None, max_length=100)


class CameraSettingsRequest(BaseModel):
    zone: str = Field(default="Camera", max_length=100)
    x: float = Field(default=50.0, ge=0.0, le=100.0)
    y: float = Field(default=50.0, ge=0.0, le=100.0)


                                                              
       
                                                              

SNAPSHOT_ROOT = os.path.realpath(
    str(SNAPSHOT_DIR)
)

LIVE_FEED_PATH = os.path.join(
    str(SNAPSHOT_DIR),
    "live_feed.jpg",
)


                                                              
         
                                                              

def _find_snapshot_on_disk(event_id: str | None):
    if not event_id:
        return None

    snapshot_dir = os.path.realpath(str(SNAPSHOT_DIR))
    if not os.path.isdir(snapshot_dir):
        return None

    candidate_names = []
    event_prefix = str(event_id).strip()
    if event_prefix:
        candidate_names.append(f"{event_prefix}.jpg")
        candidate_names.append(f"{event_prefix}.jpeg")

    for name in candidate_names:
        full_path = os.path.join(snapshot_dir, name)
        if os.path.isfile(full_path):
            return os.path.realpath(full_path)

    for file_name in sorted(os.listdir(snapshot_dir)):
        lowered = file_name.lower()
        if not (lowered.endswith(".jpg") or lowered.endswith(".jpeg")):
            continue
        if event_prefix and event_prefix in file_name:
            full_path = os.path.join(snapshot_dir, file_name)
            if os.path.isfile(full_path):
                return os.path.realpath(full_path)

    return None


def serialize_event(event: ThreatEvent) -> dict:
    resolved_snapshot = resolve_event_snapshot_path(event.event_id)
    if not resolved_snapshot:
        resolved_snapshot = _find_snapshot_on_disk(event.event_id) or event.snapshot_path

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
        "snapshot_path": resolved_snapshot,
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


def serialize_unit(unit: Unit) -> dict:
    return {
        "id": unit.id,
        "name": unit.name,
        "leader_name": unit.leader_name,
        "email": unit.email,
        "phone": unit.phone,
        "whatsapp": unit.whatsapp,
        "zone": unit.zone,
        "x": unit.x,
        "y": unit.y,
    }


def serialize_assignment(assignment: UnitAssignment) -> dict:
    unit = get_unit(assignment.unit_id) if assignment.unit_id is not None else None

    return {
        "id": assignment.id,
        "event_id": assignment.event_id,
        "unit_id": assignment.unit_id,
        "unit_name": unit.name if unit else None,
        "threat_level": assignment.threat_level,
        "channel": assignment.channel,
        "priority": assignment.priority,
        "status": assignment.status,
        "note": assignment.note,
        "message": assignment.message,
        "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
        "dispatched_at": assignment.dispatched_at.isoformat() if assignment.dispatched_at else None,
    }


def resolve_event_snapshot_path(event_id: str | None):
    if not event_id:
        return None

    db = SessionLocal()
    try:
        event = db.query(ThreatEvent).filter(ThreatEvent.event_id == event_id).first()
        if event is None:
            return _find_snapshot_on_disk(event_id)

        snapshot_path = event.snapshot_path
        if snapshot_path:
            absolute_path = os.path.realpath(snapshot_path)
            if absolute_path.startswith(os.path.realpath(str(SNAPSHOT_DIR)) + os.sep) and os.path.isfile(absolute_path):
                try:
                    img = cv2.imread(absolute_path, cv2.IMREAD_COLOR)
                    if img is not None and img.size > 0 and img.mean() > 2.0:
                        return absolute_path
                except Exception:
                    pass

        fallback = _find_snapshot_on_disk(event_id)
        if fallback:
            return fallback

        return None
    finally:
        db.close()


                                                              
        
                                                              

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


@app.get("/api/units")
def get_units():
    units = list_units()
    return {"units": [serialize_unit(unit) for unit in units]}


@app.post("/api/units")
def add_unit(payload: UnitCreateRequest):
    if not any((value or "").strip() for value in (payload.email, payload.phone, payload.whatsapp)):
        raise HTTPException(
            status_code=422,
            detail="Provide an email address or phone number for the unit.",
        )

    unit = create_unit(
        name=payload.name,
        leader_name=payload.leader_name,
        email=payload.email,
        phone=payload.phone,
        whatsapp=payload.whatsapp,
        zone=payload.zone,
    )
    if unit is None:
        raise HTTPException(status_code=409, detail="A unit with this name already exists")

    return {"unit": serialize_unit(unit)}


@app.patch("/api/units/{unit_id}")
def edit_unit(unit_id: int, payload: UnitUpdateRequest):
    unit = update_unit(
        unit_id,
        leader_name=payload.leader_name,
        email=payload.email,
        phone=payload.phone,
        whatsapp=payload.whatsapp,
        zone=payload.zone,
    )
    if unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"unit": serialize_unit(unit)}


@app.delete("/api/units/{unit_id}")
def remove_unit(unit_id: int):
    deleted = delete_unit(unit_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    if not deleted:
        raise HTTPException(
            status_code=409,
            detail="This unit has assignments. Resolve or remove its assignments before removing the unit.",
        )
    return {"status": "deleted", "unit_id": unit_id}


@app.get("/api/settings/camera")
def get_camera_settings():
    """Return the configured camera / threat-origin location."""
    return {
        "zone": get_setting("camera_zone", "Camera"),
        "x": float(get_setting("camera_x", "50")),
        "y": float(get_setting("camera_y", "50")),
    }


@app.put("/api/settings/camera")
def update_camera_settings(payload: CameraSettingsRequest):
    """Persist the camera / threat-origin location."""
    set_setting("camera_zone", payload.zone.strip() or "Camera")
    set_setting("camera_x", str(round(payload.x, 1)))
    set_setting("camera_y", str(round(payload.y, 1)))
    return {
        "zone": get_setting("camera_zone"),
        "x": float(get_setting("camera_x")),
        "y": float(get_setting("camera_y")),
    }


@app.get("/api/unit-assignments")
def get_assignments(event_id: str | None = None, unit_id: int | None = None):
    records = list_assignments(event_id=event_id, unit_id=unit_id)
    return {"assignments": [serialize_assignment(item) for item in records]}


@app.post("/api/assign-threat")
def assign_threat(payload: UnitAssignmentRequest):
    unit = get_unit(payload.unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")

    message = (payload.message or "").strip() or (
        f"Threat level {payload.threat_level.upper()} assigned to {unit.name}. "
        f"Confirm deployment and alert the leader."
    )

    assignment = create_assignment(
        event_id=payload.event_id,
        unit_id=unit.id,
        threat_level=payload.threat_level,
        channel=payload.channel,
        priority=payload.priority,
        note=payload.note,
        message=message,
    )

    snapshot_path = resolve_event_snapshot_path(payload.event_id)
    success, detail = dispatch_unit_alert(
        unit,
        payload.threat_level,
        payload.channel,
        message,
        snapshot_path=snapshot_path,
    )
    new_status = "sent" if success else "queued"
    assignment = update_assignment_status(assignment.id, new_status)

    return {
        "assignment": serialize_assignment(assignment),
        "dispatch": {"success": success, "detail": detail},
    }


@app.post("/api/assignments/{assignment_id}/status")
def update_assignment_status_route(assignment_id: int, payload: StatusUpdateRequest):
    assignment = update_assignment_status(assignment_id, payload.status)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if payload.message:
        assignment.message = payload.message
    if payload.note:
        assignment.note = payload.note
    db = SessionLocal()
    try:
        db.merge(assignment)
        db.commit()
    finally:
        db.close()
    return {"assignment": serialize_assignment(assignment)}


@app.delete("/api/assignments/{assignment_id}")
def delete_assignment_route(assignment_id: int, payload: AssignmentDeleteRequest):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Deletion requires confirmation")

    deleted = delete_assignment(assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return {"status": "deleted", "assignment_id": assignment_id}


                                                              
           
                                                              

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


                                                              
          
                                                              

@app.delete("/api/events/{event_id}")
def delete_event_route(event_id: str, payload: AssignmentDeleteRequest):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Deletion requires confirmation")

    db = SessionLocal()
    try:
        event = db.query(ThreatEvent).filter(ThreatEvent.event_id == event_id).first()
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.status == "ACTIVE":
            raise HTTPException(status_code=409, detail="Active events cannot be deleted until they end")
    finally:
        db.close()

    snapshot_candidate = resolve_event_snapshot_path(event_id) or _find_snapshot_on_disk(event_id)
    deleted, stored_snapshot_path = delete_event_record(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")

    candidate = snapshot_candidate or stored_snapshot_path
    snapshot_deleted = False
    if candidate:
        real_snapshot = os.path.realpath(candidate)
        if real_snapshot.startswith(SNAPSHOT_ROOT + os.sep) and os.path.isfile(real_snapshot):
            db = SessionLocal()
            try:
                shared = db.query(ThreatEvent.id).filter(ThreatEvent.snapshot_path == real_snapshot).first()
            finally:
                db.close()
            if shared is None:
                try:
                    os.remove(real_snapshot)
                    snapshot_deleted = True
                except OSError:
                    snapshot_deleted = False

    return {
        "status": "deleted",
        "event_id": event_id,
        "snapshot_deleted": snapshot_deleted,
    }


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

        real_snapshot = resolve_event_snapshot_path(event_id) or _find_snapshot_on_disk(event_id)

        if not real_snapshot:
            raise HTTPException(
                status_code=404,
                detail="No snapshot available",
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
