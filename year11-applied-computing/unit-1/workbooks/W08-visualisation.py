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
        # Workbook 8 — Visualisation conventions

        Goes with **Topic 16**. Every number below is a decision about a chart. Work them out first, then draw —
        because a chart drawn before you knew the numbers is a chart that chose its own axes.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w08_visualisation as bank
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

        `axis`  ·  `scale`  ·  `truncated axis`  ·  `gridline`  ·  `legend`  ·  `series`  ·  `categorical`  ·  `continuous`  ·  `chart junk`  ·  `aspect ratio`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The chart you are building

        A line chart of daily maximum temperature at **Mildura Airport, station 76031** across 2025, drawn in `climate-observations.xlsx` in the `data` folder.

        Before you draw anything you need to know how many points it holds and what the y-axis has to cover.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 8.1

        How many points will that line chart have?
        """
    )
    return


@app.cell
def _():
    answer_8_1 = ''
    return (answer_8_1,)


@app.cell(hide_code=True)
def _(answer_8_1, panel):
    panel("8.1", answer_8_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 8.2

        The mean maximum temperature at station 76031 **in January 2025 only**, in °C to one decimal place.

        January is `2025-01-01` to `2025-01-31`.
        """
    )
    return


@app.cell
def _():
    answer_8_2 = ''
    return (answer_8_2,)


@app.cell(hide_code=True)
def _(answer_8_2, panel):
    panel("8.2", answer_8_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## One axis for six stations

        Now a bar chart: the mean maximum temperature of each of the six stations, side by side. **86038** Melbourne Airport, **86338** Essendon Airport, **85072** East Sale Airport, **76031** Mildura Airport, **90015** Cape Otway Lighthouse, **87031** Laverton RAAF.

        Work out each station's mean maximum to one decimal place, then answer the next three.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 8.3

        Of those six means, the **lowest**, in °C.
        """
    )
    return


@app.cell
def _():
    answer_8_3 = ''
    return (answer_8_3,)


@app.cell(hide_code=True)
def _(answer_8_3, panel):
    panel("8.3", answer_8_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 8.4

        Of those six means, the **highest**, in °C.
        """
    )
    return


@app.cell
def _():
    answer_8_4 = ''
    return (answer_8_4,)


@app.cell(hide_code=True)
def _(answer_8_4, panel):
    panel("8.4", answer_8_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 8.5

        Highest minus lowest, in °C.
        """
    )
    return


@app.cell
def _():
    answer_8_5 = ''
    return (answer_8_5,)


@app.cell(hide_code=True)
def _(answer_8_5, panel):
    panel("8.5", answer_8_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## What 8.5 is for

        Draw that bar chart twice.

        (a) Once with the y-axis starting at **zero**.

        (b) Once with the y-axis starting just below your answer to 8.3.

        Both charts come from identical data and neither contains a false number. In the second one the tallest bar looks several times the shortest. Your answer to 8.5 is the real difference.

        A truncated axis is not always dishonest — sometimes it is the only way to see a small real change. It becomes dishonest when the reader is not told.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Choosing the chart type

        ### 8.6

        Total rainfall for the year at **Cape Otway Lighthouse, station 90015**, in mm to the nearest whole millimetre. Dry days included — they add zero, but they are still days.
        """
    )
    return


@app.cell
def _():
    answer_8_6 = ''
    return (answer_8_6,)


@app.cell(hide_code=True)
def _(answer_8_6, panel):
    panel("8.6", answer_8_6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        Now think about what you would draw that with. A **line** implies the values join up and that the distance between them means something — true of daily temperature, false of annual totals at six separate places. A **bar** compares separate things. A **pie** claims the parts make a meaningful whole, and total rainfall across six stations does not add up to anything that exists.

        There is no check on this part. It is the part the assessment asks about.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Your turn

        Using the spreadsheet, draw one chart that answers *is Mildura hotter than Cape Otway, and by how much, through the year?* You choose the chart type, the axes and the labels.

        Write underneath it, in one sentence, what a reader should take away — then check that your chart shows that, and not something else.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** take the two bar charts from 8.5 and write, for each, one audience it would suit and one it would mislead. Then list the five things every chart you submit this year must have, and tick them off against the chart you just drew.
        """
    )
    return


if __name__ == "__main__":
    app.run()
