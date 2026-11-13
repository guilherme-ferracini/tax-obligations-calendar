# Tax Obligations Calendar

[![tests](https://github.com/guilherme-ferracini/tax-obligations-calendar/actions/workflows/tests.yml/badge.svg)](https://github.com/guilherme-ferracini/tax-obligations-calendar/actions)

Generates each client's **monthly tax and payroll obligations** (DAS, eSocial, EFD-Reinf, FGTS Digital, DCTFWeb, PIS/COFINS, quarterly IRPJ/CSLL) from their profile, with **real due dates**: weekends, national and bank holidays and each obligation's own rolling rule are applied. The output is a Markdown agenda plus an **.ics file** you can import into Google Calendar, Outlook or Teams.

## Why this exists

Missed deadlines are the most expensive mistake in an accounting firm, and the trap is that the rules differ. When day 20 falls on a Sunday, **FGTS is anticipated to Friday but the DAS is postponed to Monday**. When November 20 (a national holiday since 2024) falls on a Friday, federal DARFs move to Thursday. Doing this by hand for every client, every month, is where errors come from.

Design choices:

- **Rules are configuration.** Every obligation lives in [`obligations/rules.json`](obligations/rules.json) with who it applies to, the due day, the rolling rule (`next`, `previous`, `none`) and its legal source. A regulation change means editing a line, not code.
- **The profile drives the list.** Regime, employees and retentions decide which obligations each client gets.
- **The calendar is computed.** National holidays include the moving ones (Carnival, Good Friday) via the Easter algorithm. State and municipal holidays can be added with `--holiday`.

## Quickstart

```bash
python -m obligations samples/clients.json --competence 2026-08 --ics out/agenda.ics
python -m obligations samples/clients.json --competence 2026-10 --holiday 2026-12-08   # add a local holiday
python -m pytest -q
```

September 2026 (competence August), from [`samples/sample_output/agenda_2026-09.md`](samples/sample_output/agenda_2026-09.md):

```
| Fri 18/09/2026 | Aurora Distribuidora | FGTS Digital                       | Payroll | moved from 20/09 |
| Mon 21/09/2026 | Aurora Distribuidora | PGDAS-D and DAS (Simples Nacional) | Tax     | moved from 20/09 |
| Wed 30/09/2026 | Cedro Engenharia     | DCTFWeb filing                     | Tax     |                  |
Workload by team: Tax: 10, Payroll: 6
```

## What the tests pin down

- Easter 2026 = April 5, so Carnival falls on Feb 16–17 and Good Friday on Apr 3.
- eSocial for January 2026: day 15 is a Sunday, followed by Carnival → **Wednesday Feb 18**.
- August 2026: FGTS → **Sep 18** (anticipated), DAS → **Sep 21** (postponed).
- DCTFWeb → last business day of the following month; quarterly IRPJ/CSLL only after quarter-end months.
- A local holiday added at runtime is respected.

## Important

Due dates and rolling rules change through regulation. The sources are noted in `rules.json`; review them at the start of each year before relying on the output.

## License

MIT
