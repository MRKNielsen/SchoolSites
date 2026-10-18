# Unit 1 workbooks — how to run them

Eight marimo notebooks, one per week of Area of Study 1. Every exercise checks
itself as you type. Nothing in here is marked.

## What you need

A copy of **two folders**, side by side, exactly as they are on the site:

```
unit-1/
  data/          <- the climate dataset
  workbooks/     <- these notebooks, and the checks/ folder inside
```

The notebooks find the dataset by looking one folder up and then into `data`.
If you move a notebook somewhere else on its own, every exercise will report
that it cannot find the data file.

## Setup — once, at the start of the unit

1. **Install Python.** 3.10 or newer. Check what you have with:

   ```
   python --version
   ```

2. **Install marimo:**

   ```
   pip install marimo
   ```

3. **Open a workbook.** From inside the `workbooks` folder:

   ```
   marimo edit W01-exploring-the-dataset.py
   ```

   It opens in your browser. Everything runs on your own machine — nothing is
   uploaded anywhere, and no account is needed.

## How a workbook works

Each one follows the same shape:

- **Key words** at the top. Copy the definitions in as they come up in the lesson.
- **A worked cell**, already written, showing the pattern.
- **A cell you fill in**, with feedback underneath that updates as you type.
- **A closing question** to answer in your booklet, away from the computer.

The feedback tells you what to fix, not just that something is wrong. You can
try as many times as you like, and nothing is recorded.

## When something does not work

**"No file called climate-mine.db next to this workbook"** — Workbook 3 only.
Save your database in the `workbooks` folder, not in Downloads, and check the
spelling. In DB Browser you must also click **Write Changes**; until you do,
your tables exist only in memory and the file on disk is still empty.

**An exercise says it cannot find the data** — the `data` folder is not sitting
beside the `workbooks` folder. Compare your folders against the layout above.

**"Nothing to check yet"** — the cell still holds the comment it came with.
Replace `-- your query here` with your query.

**A query runs but the check says the values are wrong** — look at the rows the
feedback prints underneath. The usual cause is a filter that includes a value it
should exclude, or a sort in the wrong direction.

## Workbook 3 needs DB Browser

Workbook 3 is the only one where you build something outside the notebook. You
need **DB Browser for SQLite** — free, and it runs without installing anything
if you use the portable version. The workbook has the steps.

## The checks folder

`checks/` holds the exercise banks the notebooks import. You never need to open
it, and editing it will break the feedback. The expected answers in there are
stored as hashes, so reading the files will not tell you what the answers are —
work them out from the data instead, which is the point.
