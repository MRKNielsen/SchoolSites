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
        # Workbook 6 — SQL III — aggregation

        Goes with **Topic 14**. Up to now every query returned rows of the data. Aggregation returns a summary of it —
        and the thing to watch is which rows end up in each group.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w06_aggregation as bank
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

        `aggregate function`  ·  `COUNT`  ·  `SUM`  ·  `AVG`  ·  `MIN`  ·  `MAX`  ·  `GROUP BY`  ·  `HAVING`  ·  `alias`
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

        *What is the wettest single day at each station?* `GROUP BY` collapses the 2190 rows into one row per station; `MAX` then runs inside each group, not across the lot.

        `AS` renames a computed column. Without it the column comes back called `MAX(rainfall_mm)`, which is awkward to refer to and ugly in a report.
        """
    )
    return


@app.cell
def _(data_path):
    import sqlite3
    con = sqlite3.connect(data_path("climate.db"))
    con.execute("""
        SELECT station_id, MAX(rainfall_mm) AS wettest_day
        FROM observation
        GROUP BY station_id
        ORDER BY wettest_day DESC
    """).fetchall()
    return (con, sqlite3)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 6.1

        How many observations are in the database? One number, no grouping.
        """
    )
    return


@app.cell
def _():
    answer_6_1 = """
    -- your query here
    """
    return (answer_6_1,)


@app.cell(hide_code=True)
def _(answer_6_1, panel):
    panel("6.1", answer_6_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 6.2

        For each station, how many days it recorded and its mean maximum temperature, warmest station first.

        Show the station id, the day count, and the mean rounded to one decimal place — `ROUND(x, 1)`.
        """
    )
    return


@app.cell
def _():
    answer_6_2 = """
    -- your query here
    """
    return (answer_6_2,)


@app.cell(hide_code=True)
def _(answer_6_2, panel):
    panel("6.2", answer_6_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 6.3

        For each station, how many **wet days** it had — days where any rain at all fell.

        Most days in this dataset recorded 0.0 mm, and a day that recorded 0.0 mm is not a wet day. `WHERE` runs before the grouping, so that is where the filter goes.
        """
    )
    return


@app.cell
def _():
    answer_6_3 = """
    -- your query here
    """
    return (answer_6_3,)


@app.cell(hide_code=True)
def _(answer_6_3, panel):
    panel("6.3", answer_6_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 6.4

        Same as 6.3, but only the stations with more than 100 wet days.

        You cannot put `COUNT(*)` in a `WHERE` — at that point the groups do not exist yet. `HAVING` filters the groups after they are formed.
        """
    )
    return


@app.cell
def _():
    answer_6_4 = """
    -- your query here
    """
    return (answer_6_4,)


@app.cell(hide_code=True)
def _(answer_6_4, panel):
    panel("6.4", answer_6_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 6.5

        For each region, the mean maximum temperature across all its stations, warmest first.

        Show the region **name** and the mean to one decimal. Join first, then group.
        """
    )
    return


@app.cell
def _():
    answer_6_5 = """
    -- your query here
    """
    return (answer_6_5,)


@app.cell(hide_code=True)
def _(answer_6_5, panel):
    panel("6.5", answer_6_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** in your own words, the difference between `WHERE` and `HAVING`, and one example of a question that needs both. Then: region means average over *stations*, not over people — write one sentence on why that makes 'the warmest region' a slightly misleading phrase.
        """
    )
    return


if __name__ == "__main__":
    app.run()
