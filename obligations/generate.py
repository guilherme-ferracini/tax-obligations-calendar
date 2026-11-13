"""Builds each client's list of obligations for a competence month, with real due dates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List

from .calendar import BusinessCalendar

RULES_PATH = Path(__file__).with_name("rules.json")


@dataclass
class Obligation:
    client: str
    name: str
    team: str
    competence: str        # YYYY-MM
    nominal: date
    due: date
    source: str

    @property
    def moved(self) -> bool:
        return self.nominal != self.due


def load_rules(path: Path = RULES_PATH) -> List[Dict]:
    return json.loads(path.read_text(encoding="utf-8"))["rules"]


def applies(rule: Dict, client: Dict) -> bool:
    cond = rule["applies_to"]
    if "regimes" in cond and client["regime"] not in cond["regimes"]:
        return False
    for flag in ("has_employees", "has_retentions"):
        if flag in cond and bool(client.get(flag)) != cond[flag]:
            return False
    return True


def obligations_for(clients: List[Dict], competence: str, cal: BusinessCalendar,
                    rules: List[Dict] = None) -> List[Obligation]:
    rules = rules or load_rules()
    year, month = map(int, competence.split("-"))
    due_y, due_m = (year + 1, 1) if month == 12 else (year, month + 1)
    out: List[Obligation] = []
    for client in clients:
        for rule in rules:
            if not applies(rule, client):
                continue
            due_cfg = rule["due"]
            if "competence_months" in due_cfg and month not in due_cfg["competence_months"]:
                continue
            if due_cfg.get("last_business_day"):
                nominal = cal.last_business_day(due_y, due_m)
            else:
                nominal = date(due_y, due_m, due_cfg["day"])
            out.append(Obligation(client["name"], rule["name"], rule["team"], competence,
                                  nominal, cal.roll(nominal, rule["roll"]), rule["source"]))
    return sorted(out, key=lambda o: (o.due, o.client, o.name))


def to_markdown(items: List[Obligation]) -> str:
    lines = ["| Due | Client | Obligation | Team | Note |", "|---|---|---|---|---|"]
    for o in items:
        note = f"moved from {o.nominal:%d/%m}" if o.moved else ""
        lines.append(f"| {o.due:%a %d/%m/%Y} | {o.client} | {o.name} | {o.team} | {note} |")
    return "\n".join(lines)


def to_ics(items: List[Obligation]) -> str:
    """iCalendar file: import into Google Calendar, Outlook or Teams."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    events = []
    for i, o in enumerate(items):
        events.append("\r\n".join([
            "BEGIN:VEVENT",
            f"UID:{o.competence}-{i}@tax-obligations-calendar",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{o.due:%Y%m%d}",
            f"SUMMARY:{o.name} - {o.client}",
            f"DESCRIPTION:Competence {o.competence}. Team: {o.team}. {o.source}",
            "END:VEVENT",
        ]))
    return "\r\n".join(["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//tax-obligations-calendar//EN",
                        *events, "END:VCALENDAR"]) + "\r\n"
