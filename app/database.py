import os
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    DateTime
)

from sqlalchemy.orm import declarative_base, sessionmaker


                                                              
                        
                                                              

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
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

    print(
        f"[DATABASE] SQLite database ready: "
        f"{DATABASE_PATH}"
    )


                                                              
              
                                                              

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