import json
from datetime import date
from pathlib import Path

from obligations.calendar import BusinessCalendar, easter, national_holidays
from obligations.generate import obligations_for, to_ics

CAL = BusinessCalendar()
CLIENTS = json.loads((Path(__file__).parents[1] / "samples" / "clients.json").read_text())["clients"]


def due(competence, client, name_part, cal=CAL):
    items = obligations_for(CLIENTS, competence, cal)
    return next(o for o in items if o.client.startswith(client) and name_part in o.name)


def test_easter_and_mobile_holidays_2026():
    assert easter(2026) == date(2026, 4, 5)
    hol = national_holidays(2026)
    assert {date(2026, 2, 16), date(2026, 2, 17), date(2026, 4, 3)} <= hol


def test_esocial_postponed_over_weekend_and_carnival():
    # Feb 15, 2026 is a Sunday; 16-17 are Carnival -> Wednesday 18
    assert due("2026-01", "Aurora", "eSocial").due == date(2026, 2, 18)


def test_fgts_anticipated_but_das_postponed():
    # Sep 20, 2026 is a Sunday
    assert due("2026-08", "Aurora", "FGTS").due == date(2026, 9, 18)
    assert due("2026-08", "Aurora", "DAS").due == date(2026, 9, 21)


def test_dctfweb_last_business_day():
    assert due("2026-10", "Cedro", "DCTFWeb filing").due == date(2026, 11, 30)


def test_quarterly_only_after_quarter_end():
    assert not [o for o in obligations_for(CLIENTS, "2026-10", CAL) if "quarterly" in o.name]
    assert due("2026-09", "Cedro", "quarterly").due == date(2026, 10, 30)


def test_profile_drives_obligations():
    delta = [o.name for o in obligations_for(CLIENTS, "2026-10", CAL) if o.client == "Delta Clinica"]
    assert delta == ["PGDAS-D and DAS (Simples Nacional)"]
    assert any("EFD-Reinf" in o.name for o in obligations_for(CLIENTS, "2026-10", CAL) if o.client == "Bussola Software")


def test_local_holiday_is_respected():
    cal = BusinessCalendar([date(2026, 11, 30)])
    assert due("2026-10", "Cedro", "DCTFWeb filing", cal).due == date(2026, 11, 27)


def test_ics_has_one_event_per_obligation():
    items = obligations_for(CLIENTS, "2026-10", CAL)
    assert to_ics(items).count("BEGIN:VEVENT") == len(items)


def test_black_consciousness_day_moves_federal_darf():
    # Nov 20, 2026 (Friday) is a national holiday -> DARF anticipated to Thursday 19
    assert due("2026-10", "Cedro", "INSS").due == date(2026, 11, 19)
