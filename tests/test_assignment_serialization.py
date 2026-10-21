import unittest

from app.api.server import serialize_assignment
from app.database import SessionLocal, Unit, UnitAssignment, init_database


class SerializeAssignmentTest(unittest.TestCase):
    def test_serialize_assignment_after_session_close(self):
        init_database()
        db = SessionLocal()
        try:
            unit = db.query(Unit).filter(Unit.name == "Delta").first()
            if unit is None:
                unit = Unit(
                    name="Delta",
                    leader_name="Captain Nia",
                    email="dhanushnair005@gmail.com",
                    phone="+1-555-0104",
                    whatsapp="+1-555-0104",
                    zone="West Sector",
                    x=30,
                    y=68,
                )
                db.add(unit)
                db.commit()
                db.refresh(unit)

            assignment = UnitAssignment(
                event_id="test-event",
                unit_id=unit.id,
                threat_level="HIGH",
                channel="email",
                priority="immediate",
                note="Test note",
                message="Test message",
                status="queued",
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        finally:
            db.close()

        payload = serialize_assignment(assignment)

        self.assertEqual(payload["unit_name"], "Delta")
        self.assertEqual(payload["status"], "queued")


if __name__ == "__main__":
    unittest.main()
