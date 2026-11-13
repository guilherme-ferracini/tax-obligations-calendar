"""python -m obligations samples/clients.json --competence 2026-08 [--holiday 2026-12-08] [--ics out/agenda.ics]"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from .calendar import BusinessCalendar
from .generate import obligations_for, to_ics, to_markdown


def main() -> None:
    p = argparse.ArgumentParser(description="Monthly tax and payroll obligations per client, with real due dates")
    p.add_argument("clients", type=Path)
    p.add_argument("--competence", required=True, help="competence month, YYYY-MM")
    p.add_argument("--holiday", action="append", default=[], type=date.fromisoformat,
                   help="extra state/municipal holiday (repeatable)")
    p.add_argument("--ics", type=Path, default=None, help="also write an iCalendar file")
    a = p.parse_args()

    clients = json.loads(a.clients.read_text(encoding="utf-8"))["clients"]
    items = obligations_for(clients, a.competence, BusinessCalendar(a.holiday))
    print(to_markdown(items))
    print("\nWorkload by team: " + ", ".join(f"{t}: {n}" for t, n in Counter(o.team for o in items).most_common()))
    if a.ics:
        a.ics.parent.mkdir(parents=True, exist_ok=True)
        a.ics.write_text(to_ics(items), encoding="utf-8")
        print(f"Calendar file written to {a.ics}")


if __name__ == "__main__":
    main()
