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
        # Workbook 7 — Descriptive statistics

        Goes with **Topic 15**. Work these out in the spreadsheet — `climate-observations.xlsx`, in the `data` folder —
        then type each answer in here. The Python cells are a cross-check, not the method.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w07_statistics as bank
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

        `mean`  ·  `median`  ·  `mode`  ·  `range`  ·  `standard deviation`  ·  `skew`  ·  `outlier`  ·  `measure of centre`  ·  `measure of spread`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The spreadsheet

        Open `climate-observations.xlsx` from the `data` folder. Two sheets. The **observations** sheet holds 2190 rows: `obs_id`, `station_id`, `obs_date`, `min_temp_c`, `max_temp_c`, `rainfall_mm`, `humidity_9am`. The **stations** sheet holds the six stations, so you can look a station id up by name.

        The six stations are **86038** Melbourne Airport, **86338** Essendon Airport, **85072** East Sale Airport, **76031** Mildura Airport, **90015** Cape Otway Lighthouse and **87031** Laverton RAAF.

        The functions you need:

        | what you want | function |
        | --- | --- |
        | mean of a column | `=AVERAGE(range)` |
        | mean of part of a column | `=AVERAGEIF(criteria_range, criterion, average_range)` |
        | middle value | `=MEDIAN(range)` |
        | how many rows meet a test | `=COUNTIF(range, criterion)` |
        | spread | `=STDEV.S(range)` |
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The worked one

        *What is the mean minimum temperature across the whole dataset?*

        In the spreadsheet: `=AVERAGE(D2:D2191)`, rounded to one decimal.

        Here is the same figure in Python, so you can see the two agree.
        """
    )
    return


@app.cell
def _(data_path):
    import csv, statistics
    rows = list(csv.DictReader(open(data_path("observation.csv"), encoding="utf-8")))
    round(statistics.mean(float(r["min_temp_c"]) for r in rows), 1)
    return (csv, rows, statistics)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 7.1

        The mean **maximum** temperature across the whole dataset, in °C to one decimal place.
        """
    )
    return


@app.cell
def _():
    answer_7_1 = ''
    return (answer_7_1,)


@app.cell(hide_code=True)
def _(answer_7_1, panel):
    panel("7.1", answer_7_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 7.2

        The mean maximum temperature at **Mildura Airport, station 76031**, in °C to one decimal place.

        Only that station's 365 rows. `AVERAGEIF` does this in one formula.
        """
    )
    return


@app.cell
def _():
    answer_7_2 = ''
    return (answer_7_2,)


@app.cell(hide_code=True)
def _(answer_7_2, panel):
    panel("7.2", answer_7_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Centre is not one number

        The next three are all about rainfall at **Cape Otway Lighthouse, station 90015**. Do them in order and look at what happens.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 7.3

        Mean daily rainfall at station 90015, in mm to one decimal place. Include the dry days — a day that recorded 0.0 mm is a measurement, not a gap.
        """
    )
    return


@app.cell
def _():
    answer_7_3 = ''
    return (answer_7_3,)


@app.cell(hide_code=True)
def _(answer_7_3, panel):
    panel("7.3", answer_7_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 7.4

        The **median** daily rainfall at station 90015, in mm.
        """
    )
    return


@app.cell
def _():
    answer_7_4 = ''
    return (answer_7_4,)


@app.cell(hide_code=True)
def _(answer_7_4, panel):
    panel("7.4", answer_7_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 7.5

        How many days at station 90015 recorded any rain at all — more than 0.0 mm?
        """
    )
    return


@app.cell
def _():
    answer_7_5 = ''
    return (answer_7_5,)


@app.cell(hide_code=True)
def _(answer_7_5, panel):
    panel("7.5", answer_7_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        Stop and look at 7.3, 7.4 and 7.5 together. The mean sits well above the median, and the median sits where it does because most days are dry. This is a **skewed** distribution, and the mean on its own would tell somebody that Cape Otway gets a steady drizzle every day. It does not.

        This is the most useful idea in Topic 15: the measure of centre you choose is a claim about the shape of the data, and it can be a false one.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 7.6

        The **sample standard deviation** of the maximum temperature at **Mildura Airport, station 76031**, in °C to one decimal place. Use `STDEV.S`, not `STDEV.P`.
        """
    )
    return


@app.cell
def _():
    answer_7_6 = ''
    return (answer_7_6,)


@app.cell(hide_code=True)
def _(answer_7_6, panel):
    panel("7.6", answer_7_6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Your turn without the scaffold

        Work out the same standard deviation for **Cape Otway, station 90015**, and compare it with Mildura's. There is no check on this one.

        Coastal against inland, in one number. Bring both figures to the next lesson — you will need them for the visualisation task.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** for each of mean, median and standard deviation, one sentence on what it tells you and one sentence on a question it would answer badly. Then: a single reading of 48 °C is typed into the Mildura column by mistake. Which of the three figures changes most, and why?
        """
    )
    return


if __name__ == "__main__":
    app.run()
