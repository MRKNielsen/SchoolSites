import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "checks"))
    from contract import data_path
    nb_dir = os.path.dirname(os.path.abspath(__file__))
    return data_path, mo, nb_dir, os, sys


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Workbook 3 — Database design

        Goes with **Topics 10 and 11**. You are going to build the database yourself, in DB Browser for SQLite,
        and this workbook will check it. Three checks, each stricter than the last.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w03_database_design as bank
    CHECKS = bank.build()
    return CHECKS, bank


@app.cell(hide_code=True)
def _(CHECKS, mo):
    def panel(eid, submission):
        c = CHECKS[eid]
        r = c.run(submission)
        head = f"**{eid} — {'correct' if r.passed else 'not yet'}**"
        rows = ""
        if isinstance(r.detail, list) and r.detail:
            shown = r.detail[:6]
            width = len(shown[0]) if isinstance(shown[0], tuple) else 1
            rows = ("\n\n|" + " |" * width + "\n|" + " --- |" * width + "\n"
                    + "\n".join("| " + " | ".join(str(x) for x in row) + " |" for row in shown))
            if len(r.detail) > 6:
                rows += f"\n\n*{len(r.detail) - 6} more row(s)*"
        return mo.md(head + "\n\n" + r.feedback + rows)
    return (panel,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Key words for today

        `entity`  ·  `attribute`  ·  `record`  ·  `primary key`  ·  `foreign key`  ·  `one-to-many`  ·  `normalisation`  ·  `referential integrity`  ·  `orphan record`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The problem with one big table

        Run this cell. It prints the column names of the raw extract and the first two rows.
        """
    )
    return


@app.cell
def _(data_path):
    import csv
    raw = list(csv.DictReader(open(data_path("observations_raw.csv"), encoding="utf-8")))
    list(raw[0].keys())
    return (csv, raw)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        Look at what repeats. `Mildura Airport`, `Mallee` and `VIC` are written out **365 times** between them. Every one of those copies is a chance to spell it differently, and you saw in Workbook 2 that some of them are.

        Run this to see the scale of it.
        """
    )
    return


@app.cell
def _(raw):
    names = {}
    for r in raw:
        names[r["station_name"]] = names.get(r["station_name"], 0) + 1
    sorted(names.items(), key=lambda kv: -kv[1])
    return (names, r)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The design you are building

        Three tables, because the data describes three different kinds of thing:

        | table | primary key | holds |
        | --- | --- | --- |
        | `region` | `region_id` | the four regions and their state |
        | `station` | `station_id` | the six stations, each naming its region |
        | `observation` | `obs_id` | one row per station per day |

        Two foreign keys: `station.region_id` → `region.region_id`, and `observation.station_id` → `station.station_id`.

        Column names are **lower_snake_case** throughout — no capitals, no spaces, no hyphens. That is a convention, not a rule of SQLite, and the check enforces it because every professional codebase does.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Building it

        In DB Browser for SQLite:

        (a) **File → New Database**, and save it as `climate-mine.db` **in the same folder as this workbook**.

        (b) **Create Table** for `region` first. A table can only reference one that already exists, so build them in the order region, station, observation.

        (c) For each primary key, tick **PK** and **NN** (not null).

        (d) For each foreign key, use the **Foreign Key** column in the table designer.

        (e) **File → Import → Table from CSV file** for the data. Import `region.csv`, `station.csv` and `observation.csv` from the `data` folder into the matching table.

        (f) **Write Changes** before you check. DB Browser holds your edits in memory until you do, and this workbook reads the file on disk.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 3.1 — the three tables exist

        Type the name of your database file below. It must sit in the same folder as this workbook.
        """
    )
    return


@app.cell
def _():
    answer_3_1 = 'climate-mine.db'
    return (answer_3_1,)


@app.cell(hide_code=True)
def _(answer_3_1, nb_dir, os, panel):
    panel("3.1", answer_3_1 if os.path.isabs(answer_3_1) else os.path.join(nb_dir, answer_3_1))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 3.2 — the keys and the naming

        Same file. This check looks at the primary keys, and at whether every table and column name is lower_snake_case.
        """
    )
    return


@app.cell
def _():
    answer_3_2 = 'climate-mine.db'
    return (answer_3_2,)


@app.cell(hide_code=True)
def _(answer_3_2, nb_dir, os, panel):
    panel("3.2", answer_3_2 if os.path.isabs(answer_3_2) else os.path.join(nb_dir, answer_3_2))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 3.3 — the relationships hold

        Same file again. This check looks for the two foreign keys, and then counts rows that point at a record which does not exist.

        If it reports orphans: SQLite declares foreign keys but does **not** enforce them unless you turn them on. In DB Browser that is **Edit → Preferences → Database → Foreign keys**. Clean the orphan rows out of your import file and import again.
        """
    )
    return


@app.cell
def _():
    answer_3_3 = 'climate-mine.db'
    return (answer_3_3,)


@app.cell(hide_code=True)
def _(answer_3_3, nb_dir, os, panel):
    panel("3.3", answer_3_3 if os.path.isabs(answer_3_3) else os.path.join(nb_dir, answer_3_3))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** draw the entity relationship diagram for the database you just built. Mark the primary keys, the foreign keys and the direction of each one-to-many relationship. Then write one sentence on what the one big table made impossible that three tables make easy.
        """
    )
    return


if __name__ == "__main__":
    app.run()
