# Unit 1 Area of Study 1 — teaching dataset

Victorian climate observations, calendar year 2025. Four regions, six weather
stations, 2190 daily observations.

## What each file is for

| File | Used in | Notes |
| --- | --- | --- |
| `observations_raw.csv` | Weeks 2–4 | The dirty extract. 2208 rows, nine classes of deliberate fault. This is what students clean. |
| `climate-raw.db` | Week 4 | The same dirty extract as one `observation_raw` staging table, for students who normalise in SQL rather than a spreadsheet. |
| `region.csv`, `station.csv`, `observation.csv` | Weeks 4–5 | The clean, normalised reference. Three tables. |
| `climate.db` | Weeks 5–6 | Clean normalised SQLite database with primary keys, foreign keys, CHECK constraints and a composite unique key. The SQL drills run against this. |
| `climate-observations.xlsx` | Weeks 6–7 | Two sheets, frozen header rows, for the descriptive-statistics and visualisation work. |
| `data-dictionary.md` | Throughout | Generated from the schema. Doubles as a worked example of the design-tool key knowledge. |

## Provenance — read this before using it with students

This dataset is **synthetic**. Its structure mirrors the Bureau of Meteorology's
daily observations, and each station's annual mean maximum, mean minimum and
rainfall are calibrated against that station's published climate normals, so the
figures behave realistically. It is **not** a Bureau extract and must not be
cited as one. The data dictionary says so too.

Synthetic was a deliberate choice, not a shortcut:

- Every fault in the dirty extract is **engineered and documented**, so the
  cleaning task has a known correct answer and can be auto-checked. Real data
  has whatever faults it happens to have, which is worse for teaching and
  impossible to autograde.
- There is **no licensing question** and nothing to re-clear each year.
- Variants with the same schema and different values can be generated for
  assessment integrity.

Where the study design wants **authentic** data — the Unit 1 Outcome 1 task,
and VCAA's "pose a guiding question using authentic data" activity — download a
real extract. The schema here matches the Bureau's, so real data drops into the
same tables. VCAA's own suggested sources are the Bureau of Meteorology, the
Australian Bureau of Statistics, the World Bank databank, Data Commons and
FiveThirtyEight.

## Regenerating

The generator scripts and the cleaning answer key are **deliberately not in this
repository** — this site is public, and they give the game away. They live with
the staff material.

## Referential integrity

`climate.db` declares foreign keys, but SQLite does not enforce them unless you
ask. Run `PRAGMA foreign_keys = ON;` at the start of every session.
