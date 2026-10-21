from app.database import (
    Base,
    SessionLocal,
    create_assignment,
    list_assignments,
    list_units,
    seed_default_units,
)


def test_seed_default_units_and_assignment_round_trip():
    Base.metadata.create_all(bind=SessionLocal.kw["bind"]) if False else None

    units = seed_default_units()
    assert len(units) >= 5
    assert {unit.name for unit in units} >= {"Alpha", "Beta", "Gamma", "Delta", "Epsilon"}

    first_unit = list_units()[0]
    assignment = create_assignment(
        event_id="evt-test-001",
        unit_id=first_unit.id,
        threat_level="HIGH",
        channel="email",
        priority="immediate",
        note="Suspected armed suspect near checkpoint",
        message="Threat assigned to unit leader for rapid response.",
    )

    saved = list_assignments(event_id="evt-test-001")
    assert len(saved) >= 1
    assert saved[0].unit_id == first_unit.id
    assert saved[0].channels == "email"
    assert saved[0].status in {"queued", "sent", "dispatched"}
