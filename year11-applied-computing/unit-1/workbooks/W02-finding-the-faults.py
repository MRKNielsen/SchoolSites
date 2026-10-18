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
        # Workbook 2 — Finding the faults

        Goes with **Topic 4**. This is the raw extract, exactly as a data dump arrives.
        It has nine kinds of fault in it. Your job is to find and count them — and to name the damage each one does.
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import w02_data_quality as bank
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

        The five quality factors from Topic 4, plus what you will meet today:

        `accuracy`  ·  `bias`  ·  `integrity`  ·  `relevance`  ·  `reliability`  ·  `outlier`  ·  `missing value`  ·  `duplicate`  ·  `orphan record`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The raw extract

        `observations_raw.csv` is one wide table — denormalised, unvalidated, and wrong in nine different ways. Load it and look at a row.
        """
    )
    return


@app.cell
def _(data_path):
    import csv
    raw = list(csv.DictReader(open(data_path("observations_raw.csv"), encoding="utf-8")))
    raw[0]
    return (csv, raw)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.1

        How many data rows does the raw extract hold? The header line does not count.

        *(The clean dataset holds 2190. This one does not.)*
        """
    )
    return


@app.cell
def _():
    answer_2_1 = ''
    return (answer_2_1,)


@app.cell(hide_code=True)
def _(answer_2_1, panel):
    panel("2.1", answer_2_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Missing values

        An empty cell is **not** a zero. Zero means somebody stood at the gauge and measured no rain. Empty means nobody recorded anything. Treating one as the other drags every average you compute afterwards.
        """
    )
    return


@app.cell
def _(raw):
    missing = [r for r in raw if r["rainfall_mm"].strip() == ""]
    len(missing)
    return (missing,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.2

        How many rows have no rainfall value at all?
        """
    )
    return


@app.cell
def _():
    answer_2_2 = ''
    return (answer_2_2,)


@app.cell(hide_code=True)
def _(answer_2_2, panel):
    panel("2.2", answer_2_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Type contamination

        Somebody typed the unit into the value, so the column is no longer a number. `float("24.4°C")` raises an error; the whole column has to be cleaned before any arithmetic works.
        """
    )
    return


@app.cell
def _(raw):
    contaminated = [r for r in raw if "\u00b0" in r["max_temp_c"]]
    contaminated[:3]
    return (contaminated,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.3

        How many rows carry a unit inside the `max_temp_c` column?
        """
    )
    return


@app.cell
def _():
    answer_2_3 = ''
    return (answer_2_3,)


@app.cell(hide_code=True)
def _(answer_2_3, panel):
    panel("2.3", answer_2_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Duplicates

        A duplicate is a row identical to one already seen. Here is the pattern: build a key from the whole row, and remember every key you have met.
        """
    )
    return


@app.cell
def _(raw):
    seen, dupes = set(), []
    for r in raw:
        key = tuple(r.values())
        if key in seen:
            dupes.append(r)
        seen.add(key)
    len(dupes)
    return (dupes, key, r, seen)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.4

        How many duplicate rows are there?
        """
    )
    return


@app.cell
def _():
    answer_2_4 = ''
    return (answer_2_4,)


@app.cell(hide_code=True)
def _(answer_2_4, panel):
    panel("2.4", answer_2_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Broken relationships

        Some rows name station `99999`, which is not one of the six real stations (86038, 86338, 85072, 76031, 90015, 87031). A row pointing at a record that does not exist is an **orphan**.

        Adapt the counting pattern from above.
        """
    )
    return


@app.cell
def _(raw):
    # count the orphan rows



    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.5

        How many rows reference station `99999`?
        """
    )
    return


@app.cell
def _():
    answer_2_5 = ''
    return (answer_2_5,)


@app.cell(hide_code=True)
def _(answer_2_5, panel):
    panel("2.5", answer_2_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Impossible values

        Three things cannot be true: a maximum above 55 °C, negative rainfall, or humidity above 100%.

        Watch your conversions — some of these cells are contaminated too, so `float()` will raise. Count each bad row once, even if it breaks two rules.
        """
    )
    return


@app.cell
def _(raw):
    # count the impossible rows



    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.6

        How many rows hold an impossible value?
        """
    )
    return


@app.cell
def _():
    answer_2_6 = ''
    return (answer_2_6,)


@app.cell(hide_code=True)
def _(answer_2_6, panel):
    panel("2.6", answer_2_6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Whitespace

        Leading and trailing spaces break every join and every grouping, silently — `"Mildura Airport"` and `"Mildura Airport "` group as two different places.

        Compare each `station_name` to itself with `.strip()` applied.
        """
    )
    return


@app.cell
def _(raw):
    # count the padded station names



    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### 2.7

        How many rows carry stray whitespace in `station_name`?
        """
    )
    return


@app.cell
def _():
    answer_2_7 = ''
    return (answer_2_7,)


@app.cell(hide_code=True)
def _(answer_2_7, panel):
    panel("2.7", answer_2_7)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## The clean-up

        If you removed the duplicate rows and the orphan-station rows, how many rows would be left?

        Two of the faults above overlap with neither, so this is just a subtraction.
        """
    )
    return


@app.cell
def _():
    answer_2_8 = ''
    return (answer_2_8,)


@app.cell(hide_code=True)
def _(answer_2_8, panel):
    panel("2.8", answer_2_8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---

        **In your booklet:** for each fault you counted, write one sentence naming the quality factor it damages — accuracy, bias, integrity, relevance or reliability — and one sentence on what it would do to a mean rainfall figure if it went unfixed.
        """
    )
    return


if __name__ == "__main__":
    app.run()
