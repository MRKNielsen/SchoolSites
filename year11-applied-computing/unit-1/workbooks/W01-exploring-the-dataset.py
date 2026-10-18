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
        # Workbook 1 — Exploring the dataset

        Goes with **Topics 2 and 3**. Before you can analyse data you have to know what you are holding.
        Work through each cell in order. Type your answers where it says to, and the feedback under the cell updates itself.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w01_exploring as bank
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

        Write a definition for each as it comes up:

        `data`  ·  `information`  ·  `record`  ·  `field`  ·  `qualitative`  ·  `quantitative`  ·  `data type`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Loading the data

        Run this cell. It reads the three files into lists of dictionaries.
        """
    )
    return


@app.cell
def _(data_path):
    import csv
    observations = list(csv.DictReader(open(data_path("observation.csv"), encoding="utf-8")))
    stations     = list(csv.DictReader(open(data_path("station.csv"),     encoding="utf-8")))
    regions      = list(csv.DictReader(open(data_path("region.csv"),      encoding="utf-8")))
    len(observations), len(stations), len(regions)
    return (csv, observations, regions, stations)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## What is in a row?

        Look at the first observation and the first station. Notice that **every value is a string** — `csv` does not know your data types. That is the first thing you have to fix.
        """
    )
    return


@app.cell
def _(observations, stations):
    observations[0], stations[0]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 1.1

        How many observations are in `observation.csv`?
        """
    )
    return


@app.cell
def _():
    answer_1_1 = ''
    return (answer_1_1,)


@app.cell(hide_code=True)
def _(answer_1_1, panel):
    panel("1.1", answer_1_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 1.2

        How many weather stations are in `station.csv`?
        """
    )
    return


@app.cell
def _():
    answer_1_2 = ''
    return (answer_1_2,)


@app.cell(hide_code=True)
def _(answer_1_2, panel):
    panel("1.2", answer_1_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 1.3

        Every station recorded the same number of days. How many days is that?

        Work it out in the cell below, then type the number in.
        """
    )
    return


@app.cell
def _(observations, stations):
    # work it out here



    return


@app.cell
def _():
    answer_1_3 = ''
    return (answer_1_3,)


@app.cell(hide_code=True)
def _(answer_1_3, panel):
    panel("1.3", answer_1_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Finding the extreme

        Here is the pattern for pulling one number out of 2190 rows. `float()` is doing the real work — without it you would be comparing text, and `"9.0"` sorts above `"25.1"`.
        """
    )
    return


@app.cell
def _(observations):
    hottest = max(float(r["max_temp_c"]) for r in observations)
    hottest
    return (hottest,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 1.4

        What was the highest maximum temperature recorded anywhere in the file, in °C?
        """
    )
    return


@app.cell
def _():
    answer_1_4 = ''
    return (answer_1_4,)


@app.cell(hide_code=True)
def _(answer_1_4, panel):
    panel("1.4", answer_1_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Your turn without the pattern

        Use the cell below to find the **coldest minimum** anywhere in the file. There is no check on this one — bring the number to the next lesson.
        """
    )
    return


@app.cell
def _(observations):
    # coldest minimum



    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **Before you leave:** of the seven columns in `observation.csv`, which are quantitative, which are qualitative, and which are identifiers that only look numeric? Write your answer in your booklet.
        """
    )
    return


if __name__ == "__main__":
    app.run()
