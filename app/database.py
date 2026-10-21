import os
import math
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import declarative_base, sessionmaker, relationship


                                                              
                        
                                                              

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        BASE_DIR,
        ".."
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "app",
    "data"
)

SNAPSHOT_DIR = os.path.join(
    DATA_DIR,
    "snapshots"
)

os.makedirs(
    SNAPSHOT_DIR,
    exist_ok=True
)

DATABASE_PATH = os.path.join(
    DATA_DIR,
    "strix.db"
)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


                                                              
            
                                                              

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


                                                              
             
                                                              

class Unit(Base):

    __tablename__ = "units"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    leader_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(200),
        nullable=True
    )

    phone = Column(
        String(50),
        nullable=True
    )

    whatsapp = Column(
        String(50),
        nullable=True
    )

    zone = Column(
        String(100),
        nullable=True
    )

    x = Column(
        Integer,
        default=0,
        nullable=False
    )

    y = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )


class AppSetting(Base):

    __tablename__ = "app_settings"

    key = Column(
        String(80),
        primary_key=True
    )

    value = Column(
        String(255),
        nullable=False
    )


class UnitAssignment(Base):

    __tablename__ = "unit_assignments"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    event_id = Column(
        String(50),
        nullable=False,
        index=True
    )

    unit_id = Column(
        Integer,
        ForeignKey("units.id"),
        nullable=False
    )

    threat_level = Column(
        String(30),
        nullable=False,
        default="HIGH"
    )

    channel = Column(
        String(20),
        nullable=False,
        default="email"
    )

    priority = Column(
        String(20),
        nullable=False,
        default="normal"
    )

    status = Column(
        String(20),
        nullable=False,
        default="queued"
    )

    note = Column(
        Text,
        nullable=True
    )

    message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    dispatched_at = Column(
        DateTime,
        nullable=True
    )

    unit = relationship("Unit", backref="assignments")


class ThreatEvent(Base):

    __tablename__ = "threat_events"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    event_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    started_at = Column(
        DateTime,
        nullable=False
    )

    ended_at = Column(
        DateTime,
        nullable=True
    )

    duration_seconds = Column(
        Float,
        nullable=True
    )

    snapshot_path = Column(
        String(500),
        nullable=True
    )

    mistral_level = Column(
        String(30),
        nullable=True
    )

    mistral_reasoning = Column(
        Text,
        nullable=True
    )

    email_sent = Column(
        Boolean,
        default=False,
        nullable=False
    )

    status = Column(
        String(30),
        default="ACTIVE",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )


                                                              
                     
                                                              

def init_database():

    Base.metadata.create_all(
        bind=engine
    )
    seed_default_units()

    print(
        f"[DATABASE] SQLite database ready: "
        f"{DATABASE_PATH}"
    )


def get_unit(unit_id):

    db = SessionLocal()

    try:
        return db.query(Unit).filter(Unit.id == unit_id).first()
    finally:
        db.close()


def get_unit_by_name(name):

    db = SessionLocal()

    try:
        return db.query(Unit).filter(Unit.name == name).first()
    finally:
        db.close()


def seed_default_units():

    default_units = [
        {
            "name": "Alpha",
            "leader_name": "Captain Sol",
            "email": "nairabhiramv@gmail.com",
            "phone": "+1-555-0101",
            "whatsapp": "+1-555-0101",
            "zone": "North Sector",
            "x": 18,
            "y": 22,
        },
        {
            "name": "Beta",
            "leader_name": "Captain Mira",
            "email": "beta.leader@strix.local",
            "phone": "+1-555-0102",
            "whatsapp": "+1-555-0102",
            "zone": "East Sector",
            "x": 80,
            "y": 22,
        },
        {
            "name": "Gamma",
            "leader_name": "Captain Orion",
            "email": "gamma.leader@strix.local",
            "phone": "+1-555-0103",
            "whatsapp": "+1-555-0103",
            "zone": "South Sector",
            "x": 80,
            "y": 78,
        },
        {
            "name": "Delta",
            "leader_name": "Captain Nia",
            "email": "dhanushnair005@gmail.com",
            "phone": "+1-555-0104",
            "whatsapp": "+1-555-0104",
            "zone": "West Sector",
            "x": 18,
            "y": 78,
        },
        {
            "name": "Epsilon",
            "leader_name": "Captain Vega",
            "email": "epsilon.leader@strix.local",
            "phone": "+1-555-0105",
            "whatsapp": "+1-555-0105",
            "zone": "Central Hub",
            "x": 50,
            "y": 50,
        },
    ]

    db = SessionLocal()

    try:
        seed_marker = db.query(AppSetting).filter(AppSetting.key == "default_units_seeded").first()
        if seed_marker is not None:
            return db.query(Unit).order_by(Unit.name.asc()).all()

        existing_by_name = {
            unit.name: unit
            for unit in db.query(Unit).all()
        }

        for payload in default_units:
            unit = existing_by_name.get(payload["name"])
            if unit is None:
                db.add(Unit(**payload))
            else:
                unit.x = payload["x"]
                unit.y = payload["y"]

        db.flush()
        _reposition_units(db)
        db.add(AppSetting(key="default_units_seeded", value="1"))

        db.commit()
        return db.query(Unit).order_by(Unit.name.asc()).all()

    finally:
        db.close()


def list_units():

    db = SessionLocal()

    try:
        return db.query(Unit).order_by(Unit.name.asc()).all()
    finally:
        db.close()


def _reposition_units(db):
    units = db.query(Unit).order_by(Unit.name.asc()).all()
    count = len(units)
    if not count:
        return

    columns = min(4, max(2, math.ceil(math.sqrt(count * 0.75))))
    rows = math.ceil(count / columns)
    for index, unit in enumerate(units):
        row = index // columns
        column = index % columns
        items_in_row = min(columns, count - row * columns)
        horizontal_span = min(76, 44 + (items_in_row - 2) * 16)
        vertical_span = min(70, 48 + (rows - 2) * 11)
        unit.x = 50 if items_in_row == 1 else round(50 - horizontal_span / 2 + column * horizontal_span / (items_in_row - 1))
        unit.y = 50 if rows == 1 else round(50 - vertical_span / 2 + row * vertical_span / (rows - 1))


def create_unit(
    name,
    leader_name,
    email=None,
    phone=None,
    whatsapp=None,
    zone=None,
):
    db = SessionLocal()
    try:
        normalized_name = str(name).strip()
        existing = db.query(Unit).filter(Unit.name.ilike(normalized_name)).first()
        if existing is not None:
            return None

        unit = Unit(
            name=normalized_name,
            leader_name=str(leader_name).strip() or "Unit Lead",
            email=str(email).strip() or None if email else None,
            phone=str(phone).strip() or None if phone else None,
            whatsapp=str(whatsapp).strip() or None if whatsapp else None,
            zone=str(zone).strip() or "Unassigned" if zone else "Unassigned",
            x=50,
            y=50,
        )
        db.add(unit)
        db.flush()
        _reposition_units(db)
        db.commit()
        db.refresh(unit)
        return unit
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_unit(unit_id):
    db = SessionLocal()
    try:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if unit is None:
            return None

        has_assignments = db.query(UnitAssignment.id).filter(UnitAssignment.unit_id == unit_id).first()
        if has_assignments is not None:
            return False

        db.delete(unit)
        db.flush()
        _reposition_units(db)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_assignment(
    event_id,
    unit_id,
    threat_level,
    channel,
    priority="normal",
    note=None,
    message=None,
):

    db = SessionLocal()

    try:
        assignment = UnitAssignment(
            event_id=event_id,
            unit_id=unit_id,
            threat_level=str(threat_level).upper(),
            channel=str(channel).lower(),
            priority=str(priority).lower(),
            note=note,
            message=message,
            status="queued",
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    finally:
        db.close()


def list_assignments(event_id=None, unit_id=None):

    db = SessionLocal()

    try:
        query = db.query(UnitAssignment)

        if event_id:
            query = query.filter(UnitAssignment.event_id == event_id)

        if unit_id is not None:
            query = query.filter(UnitAssignment.unit_id == unit_id)

        return query.order_by(UnitAssignment.created_at.desc()).all()
    finally:
        db.close()


def update_assignment_status(assignment_id, status):

    db = SessionLocal()

    try:
        assignment = db.query(UnitAssignment).filter(UnitAssignment.id == assignment_id).first()
        if assignment is None:
            return None

        assignment.status = str(status).strip() or "queued"
        if assignment.status in {"sent", "dispatched", "acknowledged", "enroute", "resolved"}:
            assignment.dispatched_at = assignment.dispatched_at or datetime.now()
        db.commit()
        db.refresh(assignment)
        return assignment
    finally:
        db.close()


def delete_assignment(assignment_id):

    db = SessionLocal()

    try:
        assignment = db.query(UnitAssignment).filter(UnitAssignment.id == assignment_id).first()
        if assignment is None:
            return False

        db.delete(assignment)
        db.commit()
        return True
    finally:
        db.close()


                                                              
              
                                                              

def create_event(
    event_id,
    started_at,
    snapshot_path=None
):

    db = SessionLocal()

    try:

        event = ThreatEvent(
            event_id=event_id,
            started_at=started_at,
            snapshot_path=snapshot_path,
            status="ACTIVE"
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        print(
            f"[DATABASE] Event created: "
            f"{event_id}"
        )

        return event.id

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


                                                              
                       
                                                              

def update_mistral_result(
    event_id,
    level,
    reasoning
):

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
            return False

        event.mistral_level = level
        event.mistral_reasoning = reasoning

        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


                                                              
                     
                                                              

def update_email_status(
    event_id,
    sent
):

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
            return False

        event.email_sent = sent

        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()

def update_snapshot(
    event_id,
    snapshot_path
):

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
            return False

        event.snapshot_path = snapshot_path

        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()
                                                              
           
                                                              

def end_event(
    event_id,
    ended_at
):

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
            return False

        event.ended_at = ended_at

        event.duration_seconds = (
            ended_at - event.started_at
        ).total_seconds()

        event.status = "ENDED"

        db.commit()

        print(
            f"[DATABASE] Event ended: "
            f"{event_id}"
        )

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


                                                              
                   
                                                              

def get_recent_events(
    limit=50
):

    db = SessionLocal()

    try:

        events = (
            db.query(ThreatEvent)
            .order_by(
                ThreatEvent.started_at.desc()
            )
            .limit(limit)
            .all()
        )

        return events

    finally:

        db.close()


# --- Detection records for auditing / training (optional) ---
class DetectionRecord(Base):

    __tablename__ = "detection_records"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    event_id = Column(
        String(50),
        nullable=True,
        index=True
    )

    track_id = Column(
        Integer,
        nullable=True
    )

    bbox = Column(
        String(100),
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    tracking_consistency = Column(
        Float,
        nullable=True
    )

    frame_index = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )


def delete_event(event_id):
    db = SessionLocal()
    try:
        event = db.query(ThreatEvent).filter(ThreatEvent.event_id == event_id).first()
        if event is None:
            return False, None

        snapshot_path = event.snapshot_path
        db.query(UnitAssignment).filter(UnitAssignment.event_id == event_id).delete(synchronize_session=False)
        db.query(DetectionRecord).filter(DetectionRecord.event_id == event_id).delete(synchronize_session=False)
        db.delete(event)
        db.commit()
        return True, snapshot_path
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_detection_record(
    event_id,
    track_id,
    bbox,
    confidence,
    tracking_consistency=None,
    frame_index=None
):

    db = SessionLocal()

    try:

        rec = DetectionRecord(
            event_id=event_id,
            track_id=track_id,
            bbox=','.join(str(int(x)) for x in bbox),
            confidence=float(confidence),
            tracking_consistency=tracking_consistency,
            frame_index=frame_index
        )

        db.add(rec)
        db.commit()
        db.refresh(rec)

        print(
            f"[DATABASE] Detection record created: {rec.id} (event={event_id})"
        )

        return rec.id

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


def get_detections_for_event(
    event_id,
    limit=100
):

    db = SessionLocal()

    try:

        return (
            db.query(DetectionRecord)
            .filter(DetectionRecord.event_id == event_id)
            .order_by(DetectionRecord.created_at.asc())
            .limit(limit)
            .all()
        )

    finally:

        db.close()


# ---------------------------------------------------------------------------
# Unit editing
# ---------------------------------------------------------------------------

def update_unit(
    unit_id,
    leader_name=None,
    email=None,
    phone=None,
    whatsapp=None,
    zone=None,
):
    """Update mutable fields on an existing unit. Only non-None kwargs are applied."""
    db = SessionLocal()
    try:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if unit is None:
            return None

        if leader_name is not None:
            unit.leader_name = str(leader_name).strip() or "Unit Lead"
        if email is not None:
            unit.email = str(email).strip() or None
        if phone is not None:
            unit.phone = str(phone).strip() or None
        if whatsapp is not None:
            unit.whatsapp = str(whatsapp).strip() or None
        if zone is not None:
            unit.zone = str(zone).strip() or "Unassigned"

        db.commit()
        db.refresh(unit)
        return unit
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# App settings (generic key-value store backed by AppSetting table)
# ---------------------------------------------------------------------------

def get_setting(key: str, default=None):
    """Return the value stored under *key*, or *default* if absent."""
    db = SessionLocal()
    try:
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        return row.value if row is not None else default
    finally:
        db.close()


def set_setting(key: str, value: str):
    """Upsert a key-value pair into the app_settings table."""
    db = SessionLocal()
    try:
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        if row is not None:
            row.value = str(value)
        else:
            db.add(AppSetting(key=key, value=str(value)))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()