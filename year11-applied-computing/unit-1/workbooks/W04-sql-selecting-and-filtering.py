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
        # Workbook 4 — SQL I — selecting and filtering

        Goes with **Topic 12**. Write each query in the cell under the question. The feedback below it updates as you type,
        and you can try as many times as you like.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w04_sql_basics as bank
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

        `query`  ·  `SELECT`  ·  `FROM`  ·  `WHERE`  ·  `ORDER BY`  ·  `LIMIT`  ·  `BETWEEN`  ·  `predicate`  ·  `result set`
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

        This query answers *which stations are in region 1, nearest the equator first*. Read it clause by clause — SQL is written in the order `SELECT … FROM … WHERE … ORDER BY`, but it is *evaluated* `FROM`, then `WHERE`, then `SELECT`, then `ORDER BY`.
        """
    )
    return


@app.cell
def _(data_path):
    import sqlite3
    con = sqlite3.connect(data_path("climate.db"))
    con.execute("""
        SELECT station_name, latitude
        FROM station
        WHERE region_id = 1
        ORDER BY latitude DESC
    """).fetchall()
    return (con, sqlite3)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 4.1

        List every station's name and elevation, highest first.
        """
    )
    return


@app.cell
def _():
    answer_4_1 = """
    -- your query here
    """
    return (answer_4_1,)


@app.cell(hide_code=True)
def _(answer_4_1, panel):
    panel("4.1", answer_4_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 4.2

        Which stations sit above 75 metres? Show the name and the elevation.

        *Above* 75 does not include a station sitting at exactly 75.
        """
    )
    return


@app.cell
def _():
    answer_4_2 = """
    -- your query here
    """
    return (answer_4_2,)


@app.cell(hide_code=True)
def _(answer_4_2, panel):
    panel("4.2", answer_4_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 4.3

        Find the five hottest days at Mildura Airport, station `76031`. Show the date and the maximum.

        Three clauses: filter to one station, sort, then cap the number of rows.
        """
    )
    return


@app.cell
def _():
    answer_4_3 = """
    -- your query here
    """
    return (answer_4_3,)


@app.cell(hide_code=True)
def _(answer_4_3, panel):
    panel("4.3", answer_4_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 4.4

        This one runs against the **raw staging table** instead: one table called `observation_raw`, same columns as the raw CSV, every one of them text.

        How many rows recorded no rainfall value at all?

        Careful — in a text column a missing value is an empty string, and an empty string is not a zero.
        """
    )
    return


@app.cell
def _():
    answer_4_4 = """
    -- your query here
    """
    return (answer_4_4,)


@app.cell(hide_code=True)
def _(answer_4_4, panel):
    panel("4.4", answer_4_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 4.5

        List the winter observations at Cape Otway Lighthouse, station `90015`, on days when it rained.

        Winter is 1 June to 31 August 2025. Show the date and the rainfall, earliest first.

        Dates are text in `YYYY-MM-DD`, which is exactly why they sort and compare correctly as text.
        """
    )
    return


@app.cell
def _():
    answer_4_5 = """
    -- your query here
    """
    return (answer_4_5,)


@app.cell(hide_code=True)
def _(answer_4_5, panel):
    panel("4.5", answer_4_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** write out the six SQL clauses you have met, in the order SQL *evaluates* them, and one line each on what each clause does to the rows.
        """
    )
    return


if __name__ == "__main__":
    app.run()
