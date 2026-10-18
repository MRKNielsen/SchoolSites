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
        # Workbook 5 — SQL II — joins

        Goes with **Topic 13**. Normalising the data split it across three tables. A join puts it back together,
        one question at a time.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w05_joins as bank
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

        `join`  ·  `inner join`  ·  `join condition`  ·  `table alias`  ·  `qualified column name`  ·  `cartesian product`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### The database

        Every SQL question below runs against `climate.db`. Three tables:

        | table | columns |
        | --- | --- |
        | `region` | `region_id`, `region_name`, `state` |
        | `station` | `station_id`, `station_name`, `region_id`, `latitude`, `longitude`, `elevation_m`, `opened` |
        | `observation` | `obs_id`, `station_id`, `obs_date`, `min_temp_c`, `max_temp_c`, `rainfall_mm`, `humidity_9am` |

        Six stations, four regions, 2190 daily observations for the 2025 calendar year.
        `station.region_id` points at `region.region_id`; `observation.station_id` points at `station.station_id`.
        Dates are stored as text in `YYYY-MM-DD`.

        The stations are **86038** Melbourne Airport, **86338** Essendon Airport,
        **85072** East Sale Airport, **76031** Mildura Airport,
        **90015** Cape Otway Lighthouse and **87031** Laverton RAAF.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The worked one

        *Which region is each station in?* The station table holds `region_id`, a number. The name lives in `region`. So you join them on the column they share.

        `s` and `r` are **aliases** — short names for the tables, so you can write `s.station_name` instead of `station.station_name`. Once a column name appears in two tables you have no choice but to qualify it.
        """
    )
    return


@app.cell
def _(data_path):
    import sqlite3
    con = sqlite3.connect(data_path("climate.db"))
    con.execute("""
        SELECT s.station_name, s.elevation_m, r.state
        FROM station s
        JOIN region r ON r.region_id = s.region_id
        ORDER BY s.elevation_m DESC
    """).fetchall()
    return (con, sqlite3)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        **Forget the `ON` clause and SQLite will not complain.** It will pair every station with every region — 6 × 4 = 24 rows of nonsense. Run the worked query again without the `ON` line and count the rows, so you know what the mistake looks like.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 5.1

        List every station with the name of its region, station name A to Z.
        """
    )
    return


@app.cell
def _():
    answer_5_1 = """
    -- your query here
    """
    return (answer_5_1,)


@app.cell(hide_code=True)
def _(answer_5_1, panel):
    panel("5.1", answer_5_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 5.2

        What was the hottest day ever recorded at Cape Otway Lighthouse?

        Show the station name, the date and the maximum. Filter on the station's **name**, not its id — that is what forces the join.
        """
    )
    return


@app.cell
def _():
    answer_5_2 = """
    -- your query here
    """
    return (answer_5_2,)


@app.cell(hide_code=True)
def _(answer_5_2, panel):
    panel("5.2", answer_5_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 5.3

        Every observation where more than 40 mm of rain fell, wettest first. Show the region name, the date and the rainfall.

        Two joins this time: `observation` → `station` → `region`.
        """
    )
    return


@app.cell
def _():
    answer_5_3 = """
    -- your query here
    """
    return (answer_5_3,)


@app.cell(hide_code=True)
def _(answer_5_3, panel):
    panel("5.3", answer_5_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 5.4

        How many observations were recorded in the Greater Melbourne region?

        One number. Join out to `region` so you can name the region in words.
        """
    )
    return


@app.cell
def _():
    answer_5_4 = """
    -- your query here
    """
    return (answer_5_4,)


@app.cell(hide_code=True)
def _(answer_5_4, panel):
    panel("5.4", answer_5_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** draw the three tables as boxes, and draw an arrow along each join you used today. Then write one sentence on what SQLite does when you leave the `ON` clause out, and why it does not warn you.
        """
    )
    return


if __name__ == "__main__":
    app.run()
